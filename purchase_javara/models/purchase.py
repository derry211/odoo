from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare, float_round, float_is_zero
from odoo.exceptions import UserError
from datetime import datetime


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    delivery_status = fields.Selection([
            ('no', 'Not Delivered'),
            ('partial', 'Partially Delivered'),
            ('delivered', 'Fully Delivered')
        ], string='Delivery State', compute='_get_delivery', store='True')
    
    delivered_at = fields.Datetime('Delivered at', compute='_get_delivery', store='True')
    
    @api.depends('state', 'picking_ids.state')
    def _get_delivery(self):
        for order in self:
            delivered_at = False
            if order.state not in ('purchase', 'done'):
                delivery_state = 'no'
            elif all(picking.state != 'done' for picking in order.picking_ids):
                delivery_state = 'no'
            elif all(picking.state in ('done', 'cancel') for picking in order.picking_ids):
                delivery_state = 'delivered'
                last_picking = order.picking_ids.filtered(lambda p: p.picking_type_code == 'incoming').sorted(key=lambda p: p.create_date, reverse=True)[0] if order.picking_ids else False
                if last_picking:
                    delivered_at = last_picking.done_at or last_picking.x_studio_field_aixKm
            else:
                delivery_state = 'partial'

            order.update({
                'delivery_status': delivery_state,
                'delivered_at': delivered_at
            })