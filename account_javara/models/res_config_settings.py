from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    account_move_diff = fields.Many2one(
        string='Diff Account', config_parameter='account.diff')
