from odoo import tools
from odoo import models, fields, api
from datetime import date, datetime

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    # price_total to comply with price_subtotal (Price Without Tax)
    price_total_signed = fields.Monetary(string='Total Amount Signed', currency_field='company_currency_id',
        store=True, readonly=True, compute='_compute_price_total',
        help="Total amount in the currency of the company, negative for credit note.")

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
        'invoice_id.date_invoice', 'invoice_id.date')
    def _compute_price_total(self):
        # res = super(AccountInvoiceLine, self)._compute_price()
        # if self.invoice_id.date_invoice and datetime.strptime(self.invoice_id.date_invoice, '%Y-%m-%d').date() > date(2019, 6, 30):
            price_total_signed = self.price_total
            if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
                price_total_signed = self.invoice_id.currency_id.with_context(date=self.invoice_id._get_currency_rate_date()).compute(price_total_signed, self.invoice_id.company_id.currency_id)
            sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
            self.price_total_signed = price_total_signed * sign