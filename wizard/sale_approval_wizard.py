from odoo import api, fields, models


class SaleApprovalWizard(models.TransientModel):
    _name = 'sale.approval.wizard'
    _description = 'Wizard Approval Sales Order'

    order_id = fields.Many2one(
        'sale.order', string='Sales Order', required=True, readonly=True,
    )
    so_approval_category = fields.Selection(
        related='order_id.so_approval_category', readonly=True,
    )
    today_attempt_count = fields.Integer(
        related='order_id.today_attempt_count', readonly=True,
    )
    requires_berita_acara = fields.Boolean(
        related='order_id.requires_berita_acara', readonly=True,
    )
    has_berita_acara = fields.Boolean(
        string='Berita Acara Terlampir', compute='_compute_has_berita_acara',
    )
    note = fields.Text(string='Catatan')

    @api.depends('order_id.berita_acara_file',
                 'order_id.berita_acara_photo',
                 'order_id.berita_acara_url')
    def _compute_has_berita_acara(self):
        for wiz in self:
            wiz.has_berita_acara = (
                wiz.order_id._has_berita_acara() if wiz.order_id else False
            )

    def action_approve(self):
        self.ensure_one()
        if self.note:
            self.order_id.approval_note = self.note
        # Validasi & set approved dilakukan di model sale.order.
        self.order_id.action_approve()
        return {'type': 'ir.actions.act_window_close'}

    def action_refuse(self):
        self.ensure_one()
        if self.note:
            self.order_id.approval_note = self.note
        self.order_id.action_refuse()
        return {'type': 'ir.actions.act_window_close'}
