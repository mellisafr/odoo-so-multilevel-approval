from odoo import api, fields, models


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
