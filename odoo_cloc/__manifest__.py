# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Odoo Cloc',
    'version': '1.0',
    'category': 'Technical',
    'sequence': 6,
    'summary': 'Backport of cloc tool for version 11.0',
    'description': """

This module allow to count the line of extra module the same
way odoo cloc do it in version > 12.0
and send the information in update_msg

""",
    'depends': ['mail'],
    'data': [],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'cloc_exclude' : ['**/*'],
}
