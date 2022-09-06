from odoo import models, api, fields, _
from datetime import datetime

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    saleschannel_id = fields.Many2one('crm.team','Sales Channel',
                              compute='_compute_saleschannel', store=True)

    # to add saleschannel in PoS transactions
    # used in reporting
    
    @api.multi
    @api.depends('partner_id.team_id', 'ref')
    def _compute_saleschannel(self):
        for record in self:
            if datetime.strptime(record.date, '%Y-%m-%d') > datetime(2019,1,1):
                if record.partner_id and record.partner_id.team_id:
                    record.saleschannel_id = record.partner_id.team_id
                elif not record.partner_id and record.journal_id.type == 'sale' and 'POS' in record.ref:
                    # mestinya pos_session cukup self.env['pos.session'].search([('name','=', record.ref)])
                    # abis itu if len(pos_session) > 0
                    # tapi coba kasih domain dulu di self
                    pos_session = self.env['pos.session'].search([('name','=', record.ref)])
                    if len(pos_session) > 0:
                        record.saleschannel_id = pos_session.crm_team_id                
                else:
                    continue