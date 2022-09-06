from odoo.exceptions import ValidationError
from odoo import api, fields, models, _

class MrpProductProduce(models.TransientModel):
    _inherit = 'mrp.product.produce'

    @api.multi
    def do_produce(self):
        self.production_id.check_available_qty()
        return super(MrpProductProduce, self).do_produce()
