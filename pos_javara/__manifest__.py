# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'PoS Javara',
    'summary': 'Custom PoS for Javara',
    'license': 'AGPL-3',
    'version': '11.0',
    'category': 'Point of Sale',
    'author': 'Arkana, Joenan <joenan@arkana.co.id>',
    'website': 'https://www.arkana.co.id',
    'description': """Custom PoS for Javara""",
    'depends': [
        'product',
        'pos_sale',
        'point_of_sale',
    ],
    'data': [
        'views/templates.xml',
        'views/pos_order_views.xml',
        'views/res_partner_member_views.xml',
        'views/pos_tender_type_views.xml',
        'views/pos_discount_bank_views.xml',
        'report/pos_order_report_views.xml',
        'security/ir.model.access.csv',
    ],
    'qweb': [
        "static/src/xml/pos.xml"
    ],
    'demo': [],
    'test': [
    ],
    'installable': True,
}
