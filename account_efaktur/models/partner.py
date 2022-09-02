# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import csv

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    npwp = fields.Char(string='NPWP', size=15, placeholder="tanpa titik ataupun minus")
    blok = fields.Char(string='Blok')
    nomor = fields.Char(string='Nomor')
    rt = fields.Char(string='RT')
    rw = fields.Char(string='RW')
#     nik = fields.Char(string='NIK/Paspor', help="Dibutuhkan dalam Faktur Pajak untuk pembeli tanpa NPWP")
    
