# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import csv

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    no_faktur = fields.Char(string='No Faktur')
    

    @api.multi
    def generate_csv_imporbarang(self):
        return {
             'type' : 'ir.actions.act_url',
             'url': '/web/binary/download_imporbarang?model=account.invoice&id=%s&filename=ImporBarang.csv' % (self.id),
             'target': 'new',
        }
    
    @api.multi
    def generate_csv_imporlawan(self):
        return {
             'type' : 'ir.actions.act_url',
             'url': '/web/binary/download_imporlawan?model=account.invoice&id=%s&filename=ImporLawan.csv' % (self.id),
             'target': 'new',
        }

    @api.multi
    def generate_csv_imporpk(self):
        return {
             'type' : 'ir.actions.act_url',
             'url': '/web/binary/download_imporpk?model=account.invoice&id=%s&filename=ImporPK.csv' % (self.id),
             'target': 'new',
        }

    @api.multi
    def generate_csv_imporpm(self):
        return {
             'type' : 'ir.actions.act_url',
             'url': '/web/binary/download_imporpm?model=account.invoice&id=%s&filename=ImporPM.csv' % (self.id),
             'target': 'new',
        }
    
    @api.multi
    def print_faktur_pajak(self):
        return self.env.ref('account_efaktur.action_report_faktur_pajak').report_action(self)
