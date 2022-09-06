{
    'name': 'Custom Report PO for MO',
    'summary': 'Custom Report PO for MO Javara',
    'license': 'AGPL-3',
    'version': '11.0',
    'category': 'Sales',
    'author': 'Arkana, Joenan <joenan@arkana.co.id>',
    'website': 'https://www.arkana.co.id',
    'description': """Custom Report PO for MO Javara""",
    'depends': ['mrp', 'product'],
    'data': [
        'report/mrp_production_custom_reports_pre.xml',
        'report/mrp_production_custom_reports.xml',
        'report/mrp_production_custom_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
}
