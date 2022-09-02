# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, _
from odoo.tools.misc import format_date


class report_account_aged_receivable_ttf(models.AbstractModel):
    _name = "account.aged.receivable.ttf"
    _description = "Aged Receivable TTF"
    _inherit = "account.aged.partner"

    def set_context(self, options):
        ctx = super(report_account_aged_receivable_ttf, self).set_context(options)
        ctx['account_type'] = 'receivable'
        ctx['ttf'] = True
        return ctx

    def get_report_name(self):
        return _("Aged Receivable")

    def get_templates(self):
        templates = super(report_account_aged_receivable_ttf, self).get_templates()
        templates['main_template'] = 'account_reports.template_aged_receivable_report'
        templates['line_template'] = 'account_reports.line_template_aged_receivable_report'
        return templates


class report_account_aged_payable_ttf(models.AbstractModel):
    _name = "account.aged.payable.ttf"
    _description = "Aged Payable TTF"
    _inherit = "account.aged.partner"

    def set_context(self, options):
        ctx = super(report_account_aged_payable_ttf, self).set_context(options)
        ctx['account_type'] = 'payable'
        ctx['aged_balance'] = True
        ctx['ttf'] = True
        return ctx

    def get_report_name(self):
        return _("Aged Payable")

    def get_templates(self):
        templates = super(report_account_aged_payable_ttf, self).get_templates()
        templates['main_template'] = 'account_reports.template_aged_payable_report'
        templates['line_template'] = 'account_reports.line_template_aged_payable_report'
        return templates
