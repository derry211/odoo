# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools


class PosSaleReport(models.Model):
    _inherit = "report.all.channels.sales"

    product_status_id = fields.Many2one('product.status', 'Product Status', ondelete='cascade')

    def get_main_request(self):
        request = """
            CREATE or REPLACE VIEW %s AS
                SELECT id AS id,
                    name,
                    partner_id,
                    product_id,
                    product_tmpl_id,
                    date_order,
                    user_id,
                    categ_id,
                    product_status_id,
                    company_id,
                    price_total,
                    pricelist_id,
                    analytic_account_id,
                    country_id,
                    team_id,
                    price_subtotal,
                    product_qty
                FROM %s
                AS foo""" % (self._table, self._from())
        return request

    def _so(self):
        so_str = """
            WITH currency_rate as (%s)
                SELECT sol.id AS id,
                    so.name AS name,
                    so.partner_id AS partner_id,
                    sol.product_id AS product_id,
                    pro.product_tmpl_id AS product_tmpl_id,
                    so.date_order AS date_order,
                    so.user_id AS user_id,
                    pt.categ_id AS categ_id,
                    pt.product_status_id AS product_status_id,
                    so.company_id AS company_id,
                    sol.price_total / COALESCE(cr.rate, 1.0) AS price_total,
                    so.pricelist_id AS pricelist_id,
                    rp.country_id AS country_id,
                    sol.price_subtotal / COALESCE (cr.rate, 1.0) AS price_subtotal,
                    (sol.product_uom_qty / u.factor * u2.factor) as product_qty,
                    so.analytic_account_id AS analytic_account_id,
                    so.team_id AS team_id

            FROM sale_order_line sol
                    JOIN sale_order so ON (sol.order_id = so.id)
                    LEFT JOIN product_product pro ON (sol.product_id = pro.id)
                    JOIN res_partner rp ON (so.partner_id = rp.id)
                    LEFT JOIN product_template pt ON (pro.product_tmpl_id = pt.id)
                    LEFT JOIN product_pricelist pp ON (so.pricelist_id = pp.id)
                    LEFT JOIN currency_rate cr ON (cr.currency_id = pp.currency_id AND
                        cr.company_id = so.company_id AND
                        cr.date_start <= COALESCE(so.date_order, now()) AND
                        (cr.date_end IS NULL OR cr.date_end > COALESCE(so.date_order, now())))
                    LEFT JOIN product_uom u on (u.id=sol.product_uom)
                    LEFT JOIN product_uom u2 on (u2.id=pt.uom_id)
            WHERE so.state != 'cancel'
        """ % self.env['res.currency']._select_companies_rates()
        return so_str

    def _from(self):
        return """(%s)""" % (self._so())
