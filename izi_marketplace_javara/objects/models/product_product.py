# -*- coding: utf-8 -*-
# Copyright 2021 IZI PT Solusi Usaha Mudah
import re
from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    custom_name = fields.Char(string='SKU From Product Name', compute='_compute_custom_name', store=True)

    @api.multi
    @api.depends('name')
    def _compute_custom_name(self):
        for rec in self:
            custom_name = re.findall("\d{13}", rec.name)
            if len(custom_name) > 0:
                rec.custom_name = custom_name[0]
