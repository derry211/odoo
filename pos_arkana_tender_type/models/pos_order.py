from odoo import api, fields, models


class PosOrderTenderType(models.Model):
    _inherit = 'pos.order'

    # NOTE : field tender_type_id sudah didefined di addons arkana (pos_javara)
    @api.model
    def _order_fields(self, ui_order):
        fields = super(PosOrderTenderType, self)._order_fields(ui_order)
        tender = ui_order.get('tender_type_id', False)
        fields['tender_type_id'] = tender and tender or False
        return fields