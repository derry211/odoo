# -*- coding: utf-8 -*-
{
    'name': "Manufacture No Negative",

    'summary': """
        Prevent negative stock on manufacture
    """,

    'description': """

    """,

    'author': "Arkana",
    'website': "https://www.arkana.co.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'stock',
        'mrp',
    ],

    # always loaded
    'data': [
        'views/mrp_bom_views.xml',
        'views/mrp_production_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}