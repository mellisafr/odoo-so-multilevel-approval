{
    'name': 'Sales Approval',
    'version': '17.0.1.0.0',
    'summary': 'Approval workflow for sales orders',
    'category': 'Sales',
    'author': 'CNT',
    'website': '',
    'license': 'LGPL-3',
    'depends': ['sale_management', 'sale_stock'],
    'data': [
        'security/sales_approval_security.xml',
        'views/stock_warehouse_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
