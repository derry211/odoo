# -*- coding: utf-8 -*-
{
    'name': 'POS Arkana Tender Type',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'Custom POS untuk Arkana: Tender Type',
    'description': """

Custom POS untuk Arkana: Tender Type

""",
    'depends': ['point_of_sale','pos_javara'],
    'data': [
        'views/asset.xml',
        # 'views/pos_config_views.xml'
    ],
    'qweb': [
        'static/src/xml/tender_type.xml',
    ],
    'installable': True,
    'author': 'Jidoka Team',
    'website': 'https://jidokasystem.co.id',
}