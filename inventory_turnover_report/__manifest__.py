# -*- coding: utf-8 -*-
{
    'name': "Inventory Turnover Report",

    'summary': """
        Export inventory turnover report in excel format
    """,

    'description': """
        
    """,

    'author': "Arkana",
    'website': "http://www.arkana.co.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'stock',
        'purchase',
        'sale',
        'point_of_sale',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        'wizard/inventory_turnover_report_wizard.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}