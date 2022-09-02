from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from datetime import datetime, timedelta, date
from calendar import monthrange
from dateutil.relativedelta import relativedelta

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange('date_order')
    def get_date(self):
        user = self.env.user
        if not user.has_group('account.group_account_manager'):
            start_of_month = date.today().replace(day=1)
            date_order = datetime.strptime(self.date_order, '%Y-%m-%d %H:%M:%S').replace(hour=0,minute=0,second=0).date()
            if date_order < start_of_month:
                raise UserError('Tidak boleh input dokumen bulan lalu! Hubungi Admin untuk info selengkapnya')
    
    @api.multi
    def action_draft(self):
        user = self.env.user
        if not user.has_group('account.group_account_manager'):
            start_of_month = date.today().replace(day=1)
            date_order = datetime.strptime(self.date_order, '%Y-%m-%d %H:%M:%S').replace(hour=0,minute=0,second=0).date()
            if date_order < start_of_month:
                raise UserError('Tidak boleh input dokumen bulan lalu! Hubungi Admin untuk info selengkapnya')
        return super(SaleOrder, self).action_draft()

