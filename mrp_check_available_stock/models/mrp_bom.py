from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    stock_rule = fields.Selection(
        string='Stock Rule',
        selection=[
            ('not_less', 'Can not Consume Less Than BoM'),
            ('less', 'Can Consume Less Than BoM'),
            ('less_approval', 'Can Consume Less Than BoM With Approval'),
        ], required=True, default='not_less')
