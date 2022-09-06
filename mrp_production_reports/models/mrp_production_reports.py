from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_compare
from datetime import datetime


class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    count_len = fields.Integer('Count Len', compute='get_len')

    @api.multi
    def get_len(self):
        for rec in self:
            self.count_len = len(rec.active_move_line_ids)
            
