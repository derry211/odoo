from odoo import fields, api, models, _
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.multi
    @api.depends('statement_ids.journal_id')
    def _get_payment_journal(self):
        for rec in self :
            rec.payment_journal_id = rec.statement_ids[:1].journal_id.id

    tender_type_id = fields.Many2one(
        comodel_name='pos.tender.type',
        string='Tender Type',
        required=False)
    payment_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Payment Method',
        compute='_get_payment_journal',
        store=True)

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    price_subtotal = fields.Float(store=True, string='Total UnTax')
