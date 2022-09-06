# -*- coding: utf-8 -*-
{
    'name': 'POS Arkana MemberShip Group',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'Custom POS untuk Arkana: MemberShip Group',
    'description': """

Custom POS untuk Arkana: MemberShip Group

""",
    'depends': ['point_of_sale','pos_javara'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/asset.xml',
        'views/product_pricelist_views.xml',    
        'views/res_partner_views.xml',    
        'views/res_partner_member_views.xml',    
    ],
    'qweb': [
        'static/src/xml/group_membership.xml',
    ],
    'installable': True,
    'author': 'Jidoka Team',
    'website': 'https://jidokasystem.co.id',
}