from odoo import api, fields, models


class PosDiscountBank(models.Model):
    _inherit = 'pos.discount.bank'
    
    product_disc_bank_id = fields.Many2one(comodel_name='product.product', string='Discount Bank')
    bank_id = fields.Many2one(comodel_name='res.bank', string='Bank', required=False)
