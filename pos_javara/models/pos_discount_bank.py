from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp

class PosDiscountBank(models.Model):
    _name = "pos.discount.bank"
    _description = "Discount Bank"

    name = fields.Char(required=True, string='Discount Bank')
    min_amount = fields.Float(
        string='Min Amount',
        digits=dp.get_precision('Product Price'),
        required=True)
    max_amount = fields.Float(
        string='Max Amount',
        digits=dp.get_precision('Product Price'),
        required=True)
    disc_amount = fields.Float(
        string='Disc Amount',
        digits=dp.get_precision('Product Price'),
        required=True)
    disc_percent = fields.Float(
        string='Disc Percent',
        digits=dp.get_precision('Discount'),
        required=True)
