from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_compare
from datetime import datetime


class AccountInvoice(models.Model):
    _inherit = "account.invoice"
