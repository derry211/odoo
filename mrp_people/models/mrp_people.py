# from odoo import models, fields, api, _
# from odoo.tools.float_utils import float_compare, float_round, float_is_zero
# from odoo.exceptions import UserError
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_compare
from datetime import datetime

class MrpPeople(models.Model):
    _name = 'mrp.people'

    name = fields.Char('Name', required=True)
    # order_ids = fields.Many2many('mrp.production', string='Manufacture Orders')


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    people_ids = fields.Many2many('mrp.people', string='Workers')
    people_count = fields.Float(compute='_get_people_count', store=True, string='Total Worker', group_operator="avg", digits=(4, 1))
    done_at =  fields.Datetime(string='Done At')
    days = fields.Float(compute='_get_date', digits=(4, 1), store=True, string='Lead Time', group_operator="avg")

    @api.multi
    @api.depends('people_ids.name') 
    def _get_people_count(self): 
        for record in self:   
            record.people_count = len(record.people_ids)

    @api.multi
    def button_mark_done(self):
        if not self.people_ids:
            raise UserError('Worker harus diisi!')
        if datetime.now() <= datetime.strptime(self.date_planned_start, '%Y-%m-%d %H:%M:%S'):
            raise UserError('Deadline Start harus lebih awal daripada waktu selesai!')
        res = super(MrpProduction, self).button_mark_done()
        self.done_at = datetime.now()
        return res

    @api.multi
    @api.depends('done_at')
    def _get_date(self):
        for record in self:
            if not record.done_at:
                record.done_at = False
            else:
                from_date = datetime.strptime(str(record.date_planned_start), '%Y-%m-%d %H:%M:%S')
                to_date = datetime.strptime(str(record.done_at), '%Y-%m-%d %H:%M:%S')
                timedelta = to_date - from_date
                diff_day = timedelta.days
                record.days = diff_day
            

    
    


    
