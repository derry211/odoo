# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime, timedelta
import logging
import pytz

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'
# PM: label CCO Jerrycan
# RM: Cempo Hitam Unpolished | Pecah Kulit

    def merge_product(self):
        total = len(self.search([('create_uid', '=', 17)]))
        loop = 0
        for prod_to_del in self.search([('create_uid', '=', 17)]):
            # find original variant from its template
            tmpl = prod_to_del.product_tmpl_id
            prod_to_merge = [
                prod for prod in tmpl.product_variant_ids if prod.id != prod_to_del.id]
            if not prod_to_merge:
                # set not available in pos
                self.env.cr.execute(
                    'UPDATE product_template SET available_in_pos=null where id=%i' % prod_to_del.product_tmpl_id.id)
                loop += 1
                _logger.info(
                    '== MERGE PROGRESS: %i%% ==' % int(loop / total * 100))
                continue
            # set not available in pos
            self.env.cr.execute(
                'UPDATE product_template SET available_in_pos=null where id=%i' % prod_to_del.product_tmpl_id.id)
            # merge product in pos order line
            self.env.cr.execute(
                'UPDATE pos_order_line SET product_id=%i where product_id=%i' % (prod_to_merge[0].id, prod_to_del.id,))
            # merge product in stock move
            self.env.cr.execute(
                'UPDATE stock_move SET product_id=%i where product_id=%i' % (prod_to_merge[0].id, prod_to_del.id,))
            # merge product in stock inventory line
            self.env.cr.execute(
                'UPDATE stock_inventory_line SET product_id=%i where product_id=%i' % (prod_to_merge[0].id, prod_to_del.id,))
            # merge product in stock quant
            self.env.cr.execute(
                'UPDATE stock_quant SET product_id=%i where product_id=%i' % (prod_to_merge[0].id, prod_to_del.id,))
            # merge product in MO
            self.env.cr.execute(
                'UPDATE mrp_production SET product_id=%i where product_id=%i' % (prod_to_merge[0].id, prod_to_del.id,))
            # merge product in BoM
            self.env.cr.execute(
                'UPDATE mrp_bom_line SET product_id=%i where product_id=%i' % (prod_to_merge[0].id, prod_to_del.id,))
            # merge product in invoice
            self.env.cr.execute(
                'UPDATE account_invoice_line SET product_id=%i where product_id=%i' % (prod_to_merge[0].id, prod_to_del.id,))
            # merge product in sale
            self.env.cr.execute(
                'UPDATE sale_order_line SET product_id=%i where product_id=%i' % (prod_to_merge[0].id, prod_to_del.id,))
            # merge product in purchase
            self.env.cr.execute(
                'UPDATE purchase_order_line SET product_id=%i where product_id=%i' % (prod_to_merge[0].id, prod_to_del.id,))
            loop += 1
            _logger.info(
                '== MERGE PROGRESS: %i%% ==' % int(loop / total * 100))

    def set_available_in_pos(self):
        total = len(self.search([('sale_ok', '=', True)]))
        loop = 0
        for prod_to_update in self.search([('sale_ok', '=', True)]):
            # find original variant from its template
            tmpl = prod_to_update.product_tmpl_id
            # set available in pos
            self.env.cr.execute(
                'UPDATE product_template SET available_in_pos=true where id=%i' % prod_to_update.product_tmpl_id.id)
            loop += 1
            _logger.info(
                '== UPDATE PROGRESS: %i%% ==' % int(loop / total * 100))
