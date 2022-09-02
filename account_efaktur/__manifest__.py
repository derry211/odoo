# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Export e-Faktur',
    'version': '11.0',
    'category': 'Account',
    'author': 'Arkana, Joenan <joenan@arkana.co.id>',
    'website': 'https://www.arkana.co.id',
    'description': """
Allows you to export e-Faktur.
==============================================================
""",
    'depends': [
        'account',
        'state_city',
    ],
    'data': [
        'wizard/account_impor_efaktur_view.xml',
        'views/account_view.xml',
        'views/partner_view.xml',
        'reports/report.xml'
    ],
    'demo': [],
    'test': [
#         '../account/test/account_minimal_test.xml',
    ],
    'installable': True,
}
