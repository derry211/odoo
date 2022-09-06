# -*- coding: utf-8 -*-
{
    'name': 'POS Arkana Discount',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'Custom POS untuk Arkana: Discount',
    'description': """

Custom POS untuk Arkana: Discount

""",
    'depends': ['point_of_sale','pos_javara'],
    'data': [
        'views/asset.xml',
        'views/pos_order_views.xml',
        'views/pos_discount_bank_views.xml',
    ],
    'qweb': [
        'static/src/xml/discount.xml',
        'static/src/xml/discount_bank.xml',
    ],
    'installable': True,
    'author': 'Jidoka Team',
    'website': 'https://jidokasystem.co.id',
}