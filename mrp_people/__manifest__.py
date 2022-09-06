{
    'name': 'Mrp People',
    'summary': 'Custom People for Manufacture Order Javara',
    'license': 'AGPL-3',
    'version': '11.0',
    'category': 'Sales',
    'author': 'Arkana, Joenan <joenan@arkana.co.id>',
    'website': 'https://www.arkana.co.id',
    'description': """Custom People for Manufacture Order Javara""",
    'depends': ['mrp'],
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_people_line_views.xml'
    ],
    'demo': [],
    'test': [],
    'installable': True,
}
