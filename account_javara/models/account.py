from odoo import models, api, fields, _
from odoo.tools.misc import format_date
from dateutil.relativedelta import relativedelta
from datetime import datetime
import pytz

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    date_maturity_ttf = fields.Date(
        string='Date Maturity TTF', compute='_compute_date_maturity_ttf', store=True)
    team_id = fields.Many2one(string='Sales Channel (false)',
                              related='partner_id.team_id', store=True)

    @api.multi
    @api.depends('invoice_id', 'date_maturity', 'invoice_id.date_ttf', 'invoice_id.date_invoice')
    def _compute_date_maturity_ttf(self):
        for aml in self:
            if aml.invoice_id and aml.invoice_id.date_ttf:
                date_invoice_df = fields.Date.from_string(
                    aml.invoice_id.date_invoice)
                date_ttf_df = fields.Date.from_string(aml.invoice_id.date_ttf)
                diff = date_ttf_df - date_invoice_df
                date_maturity_df = fields.Date.from_string(aml.date_maturity)
                date_maturity_ttf_df = date_maturity_df + diff
                aml.date_maturity_ttf = fields.Date.to_string(
                    date_maturity_ttf_df)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.depends('date_invoice')
    @api.multi
    def _compute_is_cancelable(self):
        for rec in self :
            is_cancelable = True
            admin_user_id = self.env.ref('base.user_root')
            if rec.state not in ('draft','open'):
                is_cancelable = False
            elif rec.date_invoice :
                date_invoice = datetime.strptime(rec.date_invoice, '%Y-%m-%d').date()
                current_date = datetime.now().date()
                if date_invoice.month < current_date.month and date_invoice < current_date:
                    if self.env.user != admin_user_id :
                        is_cancelable = False
            rec.is_cancelable = is_cancelable

    @api.multi
    @api.depends('invoice_line_ids.sale_line_ids.order_id.commitment_date')
    def _compute_commitment_date(self):
        for rec in self :
            order_ids = rec.mapped('invoice_line_ids.sale_line_ids.order_id').filtered(lambda sale: sale.commitment_date)
            if order_ids :
                commitment_date = order_ids[0].commitment_date
            else :
                commitment_date = False
            rec.commitment_date = commitment_date

    date_ttf = fields.Date(string='Date TTF')
    is_cancelable = fields.Boolean(
        string='Is Cancelable',
        compute='_compute_is_cancelable')
    commitment_date = fields.Datetime(compute='_compute_commitment_date', string='Commitment Date', store=True,
                                      help="Date by which the products are sure to be delivered. This is "
                                           "a date that you can promise to the customer, based on the "
                                           "Product Lead Times.")

    def get_commitment_date(self):
        self.ensure_one()
        if not self.commitment_date :
            return ''
        return pytz.UTC.localize(datetime.strptime(self.commitment_date, '%Y-%m-%d %H:%M:%S')).astimezone(pytz.timezone(self.env.user.tz or 'Asia/Jakarta')).strftime('%Y-%m-%d %H:%M:%S')
