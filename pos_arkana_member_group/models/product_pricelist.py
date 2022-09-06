from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Pricelist(models.Model):
    _inherit = 'product.pricelist'

    is_member = fields.Boolean(string='Pricelist Member',default= False)
    is_default_non_member = fields.Boolean(string='Pricelist Default For Non Member', default= False)

    @api.constrains('is_member', 'is_default_non_member')
    def _check_is_member(self):
        for record in self:
            if record.is_member and record.is_default_non_member:
                raise ValidationError("Pricelist Member not allowed for Pricelist Default For Non Member")