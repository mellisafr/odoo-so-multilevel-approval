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
        'views/stock_warehouse_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
