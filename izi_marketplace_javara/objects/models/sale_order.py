# -*- coding: utf-8 -*-
# Copyright 2021 IZI PT Solusi Usaha Mudah

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _finish_mapping_raw_data(self, sanitized_data, values):
        sanitized_data, values = super(SaleOrder, self)._finish_mapping_raw_data(sanitized_data, values)
        mp_account = self.get_mp_account_from_context()
        if mp_account.payment_term_id:
            values.update({
                'payment_term_id': mp_account.payment_term_id.id,
            })
        if mp_account.pricelist_id:
            values.update({
                'pricelist_id': mp_account.pricelist_id.id,
            })

        if values['mp_delivery_carrier_name']:
            note = '<b>%s - %s</b>' % (values['mp_recipient_address_name'], values['mp_delivery_carrier_name'])
        else:
            note = '<b>%s - %s</b>' % (values['mp_recipient_address_name'], values['mp_delivery_carrier_type'])

        values.update({
            # 'purchase_number_tada': values['mp_invoice_number'],
            'x_studio_field_rH54Z': values['mp_invoice_number'],
            'note': note
        })
        return sanitized_data, values
