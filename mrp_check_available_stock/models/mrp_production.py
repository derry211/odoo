# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _compute_unreserve_visible(self):
        super(MrpProduction, self)._compute_unreserve_visible()
        for order in self:
            already_reserved = order.is_locked and order.state not in ('done', 'cancel') and order.mapped('move_raw_ids.move_line_ids') and any(raw.reserved_availability for raw in order.move_raw_ids)
            order.unreserve_visible = already_reserved

    state = fields.Selection(selection_add=[('to_approve','To Approve')])
    action = fields.Selection(
        string='Action',
        selection=[
            ('post', 'post'),
            ('done', 'done'),
        ], copy=False, default='post')

    def check_available_qty(self):
        if self.availability not in ('assigned','none'):
            raise ValidationError(_('Not enough material stock for MO %s or please click CHECK AVAILABILITY button before PRODUCE'%(self.display_name)))
        return True

    def check_material_consume(self):
        to_approve = self.env['mrp.production']
        if self.bom_id.stock_rule != 'less':
            bom_qty = 0
            consumed_qty = 0
            for line in self.move_raw_ids.filtered(lambda raw: raw.state not in ('done','cancel')):
                bom_qty += line.product_uom_qty
                consumed_qty += line.quantity_done
            if bom_qty > consumed_qty :
                if self.bom_id.stock_rule == 'not_less':
                    raise ValidationError(_('Can not consume qty less than to consume qty for MO %s' % (self.display_name)))
                elif self.bom_id.stock_rule == 'less_approval' :
                    self.state = 'to_approve'
                    to_approve += self
        return to_approve

    @api.multi
    def open_produce_product(self):
        self.check_available_qty()
        return super(MrpProduction, self).open_produce_product()

    @api.multi
    def post_inventory(self):
        to_approve = self.env['mrp.production']
        for rec in self :
            if not self._context.get('force_post'):
                to_approve += rec.check_material_consume()
        if to_approve :
            to_approve.write({'action':'post'})
        return super(MrpProduction, self-to_approve).post_inventory()

    @api.multi
    def button_mark_done(self):
        if not self._context.get('force_done'):
            to_approve = self.check_material_consume()
            if to_approve :
                return to_approve.write({'action':'done'})
        self = self.with_context(force_post=True)
        return super(MrpProduction, self).button_mark_done()

    @api.multi
    def action_reject(self):
        for rec in self :
            if rec.state != 'to_approve' :
                continue
            rec.state = 'progress'

    @api.multi
    def action_approve(self):
        for rec in self :
            if rec.state != 'to_approve' :
                continue
            if rec.action == 'post' :
                rec.with_context(force_post=True).post_inventory()
            else :
                rec.with_context(force_done=True).button_mark_done()
            if rec.state == 'to_approve' :
                rec.write({'state':'progress'})

    @api.multi
    def action_assign(self):
        moves_draft = self.mapped('move_raw_ids').filtered(lambda move: move.state == 'draft')
        if moves_draft :
            moves_draft.write({'state':'confirmed'})
        return super(MrpProduction, self).action_assign()
