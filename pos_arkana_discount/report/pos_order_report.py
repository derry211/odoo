from odoo import api, fields, models, tools

class PosOrderReportInherit(models.Model):
    _inherit ='report.pos.order'

    # header pos
    global_disc_amount = fields.Float(string='Global Disc Amount', readonly=True)
    name_bank_disc = fields.Char(string='Name Disc Bank', readonly=True)
    disc_bank_amount = fields.Float(string='Bank Disc Amount', readonly=True)

    def _select(self):
        select = super(PosOrderReportInherit, self)._select()
        new_select = select.replace(
                "SUM((l.qty * l.price_unit) * (100 - l.discount) / 100) AS price_total",
                "SUM(((l.qty * l.price_unit) - (l.global_disc_line + l.bank_disc_line)) * (100 - l.discount) / 100) AS price_total"
            )
        new_select = new_select.replace(
                "SUM((l.qty * l.price_unit) * (l.discount / 100)) AS total_discount",
                "SUM((l.qty * l.price_unit) - (((l.qty * l.price_unit) - (l.global_disc_line + l.bank_disc_line)) * (100 - l.discount) / 100)) AS total_discount"
            )
        # add global_disc_amount
        new_select += ', s.global_disc_amount, s.disc_bank_amount, s.name_bank_disc '
        return new_select

    def _group_by(self):
        res = super(PosOrderReportInherit, self)._group_by()
        res += ', s.global_disc_amount, s.disc_bank_amount, s.name_bank_disc '
        return res