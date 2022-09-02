from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from datetime import datetime, timedelta, date
from calendar import monthrange
from dateutil.relativedelta import relativedelta

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.onchange('date_invoice')
    def get_date(self):
        user = self.env.user
        if not user.has_group('account.group_account_manager'):
            start_of_month = date.today().replace(day=1)
            date_to_use = datetime.strptime(self.date_invoice, '%Y-%m-%d') if self.date_invoice else datetime.today()
            date_invoice = date_to_use.replace(hour=0,minute=0,second=0).date()
            if date_invoice < start_of_month:
                raise UserError('Tidak boleh input dokumen bulan lalu! Hubungi Admin untuk info selengkapnya')
    
    @api.multi
    def action_invoice_draft(self):
        user = self.env.user
        if not user.has_group('account.group_account_manager'):
            start_of_month = date.today().replace(day=1)
            date_to_use = datetime.strptime(self.date_invoice, '%Y-%m-%d') if self.date_invoice else datetime.today()
            date_invoice = date_to_use.replace(hour=0,minute=0,second=0).date()
            if date_invoice < start_of_month:
                raise UserError('Tidak boleh input dokumen bulan lalu! Hubungi Admin untuk info selengkapnya')
        return super(AccountInvoice, self).action_invoice_draft()

class AccountInvoiceRefund(models.TransientModel):
    _inherit = "account.invoice.refund"

    @api.onchange('date_invoice')
    def get_date(self):
        user = self.env.user
        if not user.has_group('account.group_account_manager'):
            start_of_month = date.today().replace(day=1)
            date_to_use = self.date_invoice or datetime.today()
            date_invoice = datetime.strptime(str(date_to_use), '%Y-%m-%d').replace(hour=0,minute=0,second=0).date()
            if date_invoice < start_of_month:
                raise UserError('Tidak boleh input dokumen bulan lalu! Hubungi Admin untuk info selengkapnya')


