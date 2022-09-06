from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ResPartnerMember(models.Model):
    _name = "res.partner.member"
    _description = 'ResPartnerMember'
    _order = 'id desc'

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Member name already exists !"),
    ]

    name = fields.Char('Member Name', required=True, copy=False, default='New')
    active = fields.Boolean(
        string='Active', 
        default=True)
    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string='Pricelist',
        required=False)
    partner_ids = fields.Many2many(
        comodel_name='res.partner',
        domain=[('customer','=',True)],
        copy=False,
        string='Customer')

    @api.constrains('partner_ids')
    def _check_partner(self):
        for rec in self :
            if rec.partner_ids :
                other_members = self.search([
                    ('partner_ids','in',rec.partner_ids.ids),
                    ('id','!=',rec.id),
                ])
                if other_members :
                    raise ValidationError(_('Some customers/members was added in other member.'))
