from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from datetime import datetime, timedelta, date
from calendar import monthrange
from dateutil.relativedelta import relativedelta

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    # date_orders = fields.Datetime('Order Date', default=datetime.today())
    date_invoices_old = fields.Date(string='Invoice Date', default=datetime.today())

    @api.multi
    @api.onchange('date_invoice')
    def _get_date(self):
        for record in self:
            user = self.env['res.users'].browse(self.env.uid)
            if not user.has_group('account.group_account_manager'):
                dates_new = datetime.strptime(str(record.date_invoice), '%Y-%m-%d').strftime('%Y-%m')
                dates_new_day = datetime.strptime(str(record.date_invoice), '%Y-%m-%d').strftime('%d')
                dates_new_month = datetime.strptime(str(record.date_invoice), '%Y-%m-%d').strftime('%m')
                dates_new_year = datetime.strptime(str(record.date_invoice), '%Y-%m-%d').strftime('%Y')
                dates_old = datetime.strptime(str(record.date_invoices_old), '%Y-%m-%d').strftime('%Y-%m')
                dates_old_day = datetime.strptime(str(record.date_invoices_old), '%Y-%m-%d').strftime('%d')
                dates_old_month = datetime.strptime(str(record.date_invoices_old), '%Y-%m-%d').strftime('%m')
                dates_old_year = datetime.strptime(str(record.date_invoices_old), '%Y-%m-%d').strftime('%Y')
                dates_old_full = datetime.strptime(str(record.date_invoices_old), '%Y-%m-%d').strftime('%Y-%m-%d')
                if dates_new < dates_old:
                    if  dates_old_day < '08':
                        day = monthrange(int(dates_new_year), int(dates_new_month))[1]
                        cal_day = day - 7
                        if dates_new_day < str(cal_day):
                            record.date_invoice = record.date_invoices_old
                            raise UserError('Tidak boleh memilih bulan sebelumnya dari bulan' + dates_old_month + ' dan tahun ' + dates_old_year)
                    else :
                        if dates_new_month < dates_old_month:
                            record.date_invoice = record.date_invoices_old
                            raise UserError('Tidak boleh memilih bulan sebelumnya dari bulan' + dates_old_month + ' dan tahun ' + dates_old_year)

    # @api.multi
    # def create(self,values):
    #     account_invoice_create = super(AccountInvoice,self).create(values)
    #     if self.date_invoices_old == False:
    #         self.date_invoices_old = self.date_invoice
    #         return account_invoice_create

    @api.multi
    def write(self,values):
        account_invoice_write = super(AccountInvoice,self).write(values)
        if self.date_invoices_old != self.date_invoice:
            self.date_invoices_old = self.date_invoice
        return account_invoice_write
                        


                    # if dates_new < dates_old and dates_old_days <= '7':
                    #     dates_new_month = datetime.date(dates_new_year, dates_new_month, monthrange((dates_new_year), int(dates_new_month))[-1])
                    #     dates_new_month_day = mdays[datetime.record.dates_new.month]
                    #     dates_old = dates_old_s - timedelta(days=14) 
                    #     if dates_new < dates_old:
                    #         raise UserError('Tidak boleh memilih bulan sebelumnya dari bulan sekarang!')
                    #         record.date_orders = record.date_orders_old
                  



