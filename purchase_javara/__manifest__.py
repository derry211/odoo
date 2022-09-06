{
    'name': 'Purchase Javara',
    'summary': 'Custom Purchase Management for Javara',
    'license': 'AGPL-3',
    'version': '11.0',
    'category': 'Purchase',
    'author': 'Arkana, Fady <fady@arkana.co.id>',
    'website': 'https://www.arkana.co.id',
    'description': """Custom Purchase Management for Javara""",
    'depends': [
        'purchase','stock_days'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_view.xml'
    ],
    'demo': [],
    'test': [
    ],
    'installable': True,
}
