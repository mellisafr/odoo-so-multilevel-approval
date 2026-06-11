from odoo import models, fields


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    so_approval_category = fields.Selection(
        selection=[
            ('store', 'Store (Ritel)'),
            ('internal_3pl', 'Internal / 3PL'),
        ],
        string='Approval Category',
        help="Menentukan aturan approval Sales Order untuk gudang ini:\n"
             "- Store: SO pertama per hari bebas; attempt berikutnya butuh approval + Berita Acara.\n"
             "- Internal / 3PL: setiap SO wajib approval WH Manager + Berita Acara.",
    )
