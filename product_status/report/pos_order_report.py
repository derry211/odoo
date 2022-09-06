# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools


class PosOrderReport(models.Model):
    _inherit = "report.pos.order"

    product_status_id = fields.Many2one('product.status', 'Product Status', ondelete='cascade')

    def _select(self):
        return super(PosOrderReport, self)._select() + ", pt.product_status_id as product_status_id"
    
    def _group_by(self):
        return super(PosOrderReport, self)._group_by() + ", pt.product_status_id"
