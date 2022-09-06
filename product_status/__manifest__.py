{
    'name': 'Product Status',
    'summary': 'Custom Product Template for Javara',
    'license': 'AGPL-3',
    'version': '11.0',
    'category': 'Inventory',
    'author': 'Arkana, Fady <fady@arkana.co.id>',
    'website': 'https://www.arkana.co.id',
    'description': """Custom Product Template for Javara""",
    'depends': [
        'stock','sale','point_of_sale'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_view.xml',
    ],
    'demo': [],
    'test': [
    ],
    'installable': True,
}
