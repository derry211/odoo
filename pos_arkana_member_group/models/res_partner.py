from odoo import api, fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    active_member_id = fields.Many2one(comodel_name='res.partner.member',
        string='Active Group Member', readonly=True,
        )
    