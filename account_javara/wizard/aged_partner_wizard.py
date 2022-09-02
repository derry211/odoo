from odoo import fields, models, api


class AccountAgedPartnerWizard(models.TransientModel):
    _name = "account.aged.partner.wizard"
    _description = 'Aged Partner Wizard'

    ttf = fields.Boolean(string='Based on TTF')

    @api.multi
    def generate(self):
        if self._context.get('type') == 'R':
            action = self.env.ref(
                'account_reports.action_account_report_ar').read()[0]
            if self.ttf:
                action['context'] = "{'model': 'account.aged.receivable.ttf'}"
        else:
            action = self.env.ref(
                'account_reports.action_account_report_ap').read()[0]
            if self.ttf:
                action['context'] = "{'model': 'account.aged.payable.ttf'}"
        return action
