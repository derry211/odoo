# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError


class AccountInvoiceImporPK(models.TransientModel):
    _name = "account.invoice.imporpk"

    @api.multi
    def invoice_imporpk(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        Invoice = self.env['account.invoice']
        invoices = Invoice.browse(active_ids)
        invoices_with_taxes = [
            inv.id for inv in invoices if inv.amount_tax > 0]
#         self.env['account.invoice'].browse(active_ids).generate_csv_imporpk()
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_imporpk?model=account.invoice&id=%s&filename=ImporPK.csv' % (str(invoices_with_taxes)),
            'target': 'new',
        }


class AccountInvoiceCancel(models.TransientModel):
    """
    This wizard will cancel the all the selected invoices.
    If in the journal, the option allow cancelling entry is not selected then it will give warning message.
    """

    _name = "account.invoice.cancel"
    _description = "Cancel the Selected Invoices"

    @api.multi
    def invoice_cancel(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['account.invoice'].browse(active_ids):
            if record.state in ('cancel', 'paid'):
                raise UserError(
                    _("Selected invoice(s) cannot be cancelled as they are already in 'Cancelled' or 'Done' state."))
            record.action_invoice_cancel()
        return {'type': 'ir.actions.act_window_close'}
