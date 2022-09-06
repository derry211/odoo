# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    product_status_id = fields.Many2one('product.status', 'Product Status', ondelete='cascade')

    def _select(self):
        return super(AccountInvoiceReport, self)._select() + ", sub.product_status_id as product_status_id"
    
    def _sub_select(self):
        return super(AccountInvoiceReport, self)._sub_select() + ", pt.product_status_id AS product_status_id"
    
    def _group_by(self):
        return super(AccountInvoiceReport, self)._group_by() + ", pt.product_status_id"
