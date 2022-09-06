from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class ResPartnerMemberInherit(models.Model):
    _inherit = 'res.partner.member'

    icon = fields.Binary(string='icon')
    # override
    partner_ids = fields.Many2many(
        comodel_name='res.partner',
        domain=[('customer','=',True)],
        copy=False,
        string='Customer')
    
    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string='Pricelist',domain="[('is_member','=',True)]",
        required=False)

    # override on create & write, karena field many2many tdk ada inverse field
    @api.model
    def create(self, vals):
        res = super(ResPartnerMemberInherit, self).create(vals)
        if res.pricelist_id and res.partner_ids:
            # update pricelist property partner
            res.partner_ids.write({
                'property_product_pricelist': res.pricelist_id.id,
                'active_member_id': res.id,
                })
        return res
    
    def _get_default_pricelist_non_member(self):
        pl = self.env['product.pricelist'].sudo().search([
            ('currency_id', '=', self.env.user.company_id.currency_id.id),
            # ('is_member', '=', False),
            ('is_default_non_member', '=', True),
            ], limit=1)
        return pl and pl.id or False
    
    @api.multi
    def write(self, values):
        # archive
        res = super(ResPartnerMemberInherit, self).write(values)
        if 'active' in values and len(values) == 1:
            for rec in self:
                if values['active'] is False:
                    active_member_id = False
                    # pl diset kemana setelah archive? set 1 from non member pl
                    property_product_pricelist_id = self._get_default_pricelist_non_member()
                else:
                    # active, use self id
                    active_member_id = rec.id
                    property_product_pricelist_id = rec.pricelist_id.id

                rec.partner_ids.write({
                    'property_product_pricelist': property_product_pricelist_id,
                    'active_member_id': active_member_id,
                    })

        elif values.get('pricelist_id') or values.get('partner_ids'):
            for rec in self:
                rec.partner_ids.write({
                    'property_product_pricelist': rec.pricelist_id.id,
                    'active_member_id': rec.id,
                    })
                if values.get('partner_ids'):
                    # values example : {'partner_ids': [[6, False, [9127]]]}
                    excl_id = values['partner_ids'][0][2]
                    # partner with this member and removed
                    partner_to_update = self.env['res.partner'].sudo().search([
                        ('active_member_id', '=', rec.id),
                        ('id', 'not in', excl_id)
                    ])
                    if partner_to_update.exists():
                        partner_to_update.write({
                            'property_product_pricelist': self._get_default_pricelist_non_member(),
                            'active_member_id': False,
                        })
        return res