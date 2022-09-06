from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class PosTenderType(models.Model):
    _name = "pos.tender.type"
    _description = "Tender Type"

    name = fields.Char(required=True, string='Tender Type')
