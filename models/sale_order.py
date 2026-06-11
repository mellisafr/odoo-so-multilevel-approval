from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Kategori approval diturunkan dari gudang asal SO.
    so_approval_category = fields.Selection(
        related='warehouse_id.so_approval_category',
        string='Kategori Approval Gudang',
        store=True,
        readonly=True,
    )

    # Jumlah SO lain pada gudang & hari yang sama yang sudah disubmit.
    today_attempt_count = fields.Integer(
        string='Attempt Hari Ini',
        compute='_compute_today_attempt_count',
        help="Banyaknya SO lain dengan gudang dan tanggal yang sama "
             "yang sudah berstatus terkonfirmasi.",
    )

    # Flag kebutuhan (dihitung dari kategori gudang + attempt).
    requires_approval = fields.Boolean(
        string='Butuh Approval',
        compute='_compute_approval_requirements',
    )
    requires_berita_acara = fields.Boolean(
        string='Butuh Berita Acara',
        compute='_compute_approval_requirements',
    )

    # Status alur persetujuan.
    approval_state = fields.Selection(
        selection=[
            ('none', 'Tanpa Approval'),
            ('to_approve', 'Menunggu Approval'),
            ('approved', 'Disetujui'),
            ('refused', 'Ditolak'),
        ],
        string='Status Approval',
        default='none',
        copy=False,
        tracking=True,
    )
    approved_by = fields.Many2one(
        'res.users', string='Disetujui Oleh', readonly=True, copy=False,
    )
    approved_date = fields.Datetime(
        string='Tanggal Approval', readonly=True, copy=False,
    )
    approval_note = fields.Text(
        string='Catatan Approval', readonly=True, copy=False,
    )

    # Lampiran Berita Acara: file, foto, dan/atau URL bukti.
    berita_acara_file = fields.Binary(
        string='Berita Acara (File)', attachment=True, copy=False,
    )
    berita_acara_filename = fields.Char(
        string='Nama File Berita Acara', copy=False,
    )
    berita_acara_photo = fields.Image(
        string='Foto Bukti', max_width=1920, max_height=1920, copy=False,
    )
    berita_acara_url = fields.Char(string='URL Bukti', copy=False)

    @api.depends('warehouse_id', 'date_order', 'state')
    def _compute_today_attempt_count(self):
        for order in self:
            count = 0
            if order.warehouse_id:
                today = fields.Date.context_today(order)
                start = fields.Datetime.to_datetime(today)
                domain = [
                    ('warehouse_id', '=', order.warehouse_id.id),
                    ('state', 'in', ['sale', 'done']),
                    ('date_order', '>=', start),
                ]
                # Abaikan record sendiri (hanya untuk record yang sudah tersimpan).
                if isinstance(order.id, int):
                    domain.append(('id', '!=', order.id))
                count = order.env['sale.order'].search_count(domain)
            order.today_attempt_count = count

    @api.depends('so_approval_category', 'today_attempt_count')
    def _compute_approval_requirements(self):
        for order in self:
            category = order.so_approval_category
            if category == 'internal_3pl':
                # Internal/3PL: setiap SO wajib approval + Berita Acara.
                need = True
            elif category == 'store':
                # Store: attempt pertama bebas, berikutnya butuh approval + BA.
                need = order.today_attempt_count > 0
            else:
                need = False
            order.requires_approval = need
            order.requires_berita_acara = need

    def _has_berita_acara(self):
        """True bila minimal satu bentuk Berita Acara dilampirkan."""
        self.ensure_one()
        return bool(
            self.berita_acara_file
            or self.berita_acara_photo
            or self.berita_acara_url
        )

    def _approver_group_for(self):
        """Group yang berwenang menyetujui SO ini, sesuai kategori gudang."""
        self.ensure_one()
        if self.so_approval_category == 'internal_3pl':
            # Internal/3PL: approval oleh WH Manager.
            return 'stock.group_stock_manager'
        # Store: approval oleh user tertentu (SO Approver).
        return 'sales_approval.group_so_approver'

    def action_confirm(self):
        """Klik Confirm: validasi Berita Acara, lalu buka wizard approval.

        - Berita Acara belum lengkap -> ValidationError (blokir).
        - Sudah lengkap & butuh approval -> set 'to_approve' + buka wizard.
        - Tidak butuh approval / sudah approved -> konfirmasi normal.
        """
        to_confirm = self.env['sale.order']
        pending = self.env['sale.order']
        for order in self:
            # Hitung ulang kondisi terkini saat konfirmasi.
            order._compute_today_attempt_count()
            order._compute_approval_requirements()

            if order.requires_approval and order.approval_state != 'approved':
                # Berita Acara wajib sebelum masuk antrian approval.
                if order.requires_berita_acara and not order._has_berita_acara():
                    raise ValidationError(
                        "Berita Acara wajib dilampirkan (file, foto, atau URL) "
                        "sebelum SO ini dapat diajukan untuk persetujuan."
                    )
                order.approval_state = 'to_approve'
                pending |= order
            else:
                to_confirm |= order

        res = True
        if to_confirm:
            res = super(SaleOrder, to_confirm).action_confirm()

        # Buka popup review approval untuk SO yang baru masuk antrian.
        if pending:
            return pending[0].action_open_approval_wizard()
        return res

    def action_open_approval_wizard(self):
        """Buka popup review approval (Approve/Refuse)."""
        self.ensure_one()
        return {
            'name': 'Review Approval SO',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.approval.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_order_id': self.id},
        }

    def action_approve(self):
        """Setujui SO lalu lanjutkan konfirmasi."""
        for order in self:
            if not self.env.user.has_group(order._approver_group_for()):
                raise UserError(
                    "Anda tidak berwenang menyetujui Sales Order ini."
                )
            if order.requires_berita_acara and not order._has_berita_acara():
                raise ValidationError(
                    "Berita Acara wajib dilampirkan sebelum approval."
                )
            order.write({
                'approval_state': 'approved',
                'approved_by': self.env.user.id,
                'approved_date': fields.Datetime.now(),
            })
            order.action_confirm()
        return True

    def action_refuse(self):
        """Tolak pengajuan approval."""
        self.write({'approval_state': 'refused'})
        return True
