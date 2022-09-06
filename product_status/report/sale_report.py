# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    product_status_id = fields.Many2one('product.status', 'Product Status', ondelete='cascade')

    def _select(self):
        return super(SaleReport, self)._select() + ", t.product_status_id as product_status_id"

    def _group_by(self):
        return super(SaleReport, self)._group_by() + ", t.product_status_id"