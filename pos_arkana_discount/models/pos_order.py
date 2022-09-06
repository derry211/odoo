from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PosOrderDiscount(models.Model):
    _inherit = 'pos.order'

    choose_disc = fields.Char(string='Choose Discount')
   
    disc_type = fields.Selection(string='Global Discount Type', 
        selection=[('fix', 'Fix'), ('percent', 'Percent'),],
        default=False,)
    
    global_disc = fields.Float(string='Global Discount', help="Dalam persen atau fixed")

    global_disc_amount = fields.Float(string='Global Discount Fixed', help="Dalam fixed", readonly=True,)

    name_bank_disc = fields.Char(string='Discount Bank', readonly=True)

    disc_bank_amount = fields.Float(string='Bank Discount Amount', help="Dalam Fixed", readonly=True)

    @api.multi
    def refund(self):
        res = super(PosOrderDiscount, self).refund()
        order_to_update = self.browse(res['res_id'])
        if order_to_update:
            # nilai set - karena harusnya dari pos (js)
            if order_to_update.disc_bank_amount:
                order_to_update.disc_bank_amount = -1 * order_to_update.disc_bank_amount
            if order_to_update.global_disc_amount:
                order_to_update.global_disc_amount = -1 * order_to_update.global_disc_amount
            # order line
            for line in order_to_update.lines:
                if line.global_disc_line:
                    line.global_disc_line = -1 * line.global_disc_line
                if line.bank_disc_line:
                    line.bank_disc_line = -1 * line.bank_disc_line
        return res

    @api.model
    def _order_fields(self, ui_order):
        fields = super(PosOrderDiscount, self)._order_fields(ui_order)
        fields['disc_type'] = ui_order.get('disc_type', False)
        fields['global_disc'] = ui_order.get('global_disc', 0.0)
        fields['global_disc_amount'] = ui_order.get('global_disc_amount', 0.0)
        fields['name_bank_disc'] = ui_order.get('name_bank_disc', " ")
        fields['disc_bank_amount'] = ui_order.get('disc_bank_amount', 0.0)
        return fields
    
    # override
    @api.model
    def _amount_line_tax(self, line, fiscal_position_id):
        taxes = line.tax_ids.filtered(lambda t: t.company_id.id == line.order_id.company_id.id)
        if fiscal_position_id:
            taxes = fiscal_position_id.map_tax(taxes, line.product_id, line.order_id.partner_id)
        if line.global_disc_line:
            price = (line.price_unit - (line.global_disc_line / line.qty)) * (1 - (line.discount or 0.0) / 100.0)
        elif line.bank_disc_line:
            price = (line.price_unit - (line.bank_disc_line / line.qty)) * (1 - (line.discount or 0.0) / 100.0)
        else:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
        taxes = taxes.compute_all(price, line.order_id.pricelist_id.currency_id, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)['taxes']
        return sum(tax.get('amount', 0.0) for tax in taxes)

    # override
    def _action_create_invoice_line(self, line=False, invoice_id=False):
        InvoiceLine = super(PosOrderDiscount, self)._action_create_invoice_line(line=line, invoice_id=invoice_id)
        # addjust price_unit if global discount line exist, POS Discount Global!
        # update after create
        if line.global_disc_line:
            InvoiceLine.write({
                'price_unit': line.price_unit - (line.global_disc_line / line.qty)
            })
        elif line.bank_disc_line:
            InvoiceLine.write({
                'price_unit': line.price_unit - (line.bank_disc_line / line.qty)
            })
        return InvoiceLine
    
    # override
    def _create_account_move_line(self, session=None, move=None):
        def _flatten_tax_and_children(taxes, group_done=None):
            children = self.env['account.tax']
            if group_done is None:
                group_done = set()
            for tax in taxes.filtered(lambda t: t.amount_type == 'group'):
                if tax.id not in group_done:
                    group_done.add(tax.id)
                    children |= _flatten_tax_and_children(tax.children_tax_ids, group_done)
            return taxes + children

        # Tricky, via the workflow, we only have one id in the ids variable
        """Create a account move line of order grouped by products or not."""
        IrProperty = self.env['ir.property']
        ResPartner = self.env['res.partner']

        if session and not all(session.id == order.session_id.id for order in self):
            raise UserError(_('Selected orders do not have the same session!'))

        grouped_data = {}
        have_to_group_by = session and session.config_id.group_by or False
        rounding_method = session and session.config_id.company_id.tax_calculation_rounding_method

        def add_anglosaxon_lines(grouped_data):
            Product = self.env['product.product']
            Analytic = self.env['account.analytic.account']
            for product_key in list(grouped_data.keys()):
                if product_key[0] == "product":
                    line = grouped_data[product_key][0]
                    product = Product.browse(line['product_id'])
                    # In the SO part, the entries will be inverted by function compute_invoice_totals
                    price_unit = self._get_pos_anglo_saxon_price_unit(product, line['partner_id'], line['quantity'])
                    account_analytic = Analytic.browse(line.get('analytic_account_id'))
                    res = Product._anglo_saxon_sale_move_lines(
                        line['name'], product, product.uom_id, line['quantity'], price_unit,
                            fiscal_position=order.fiscal_position_id,
                            account_analytic=account_analytic)
                    if res:
                        line1, line2 = res
                        line1 = Product._convert_prepared_anglosaxon_line(line1, order.partner_id)
                        insert_data('counter_part', {
                            'name': line1['name'],
                            'account_id': line1['account_id'],
                            'credit': line1['credit'] or 0.0,
                            'debit': line1['debit'] or 0.0,
                            'partner_id': line1['partner_id']

                        })

                        line2 = Product._convert_prepared_anglosaxon_line(line2, order.partner_id)
                        insert_data('counter_part', {
                            'name': line2['name'],
                            'account_id': line2['account_id'],
                            'credit': line2['credit'] or 0.0,
                            'debit': line2['debit'] or 0.0,
                            'partner_id': line2['partner_id']
                        })

        for order in self.filtered(lambda o: not o.account_move or o.state == 'paid'):
            current_company = order.sale_journal.company_id
            account_def = IrProperty.get(
                'property_account_receivable_id', 'res.partner')
            order_account = order.partner_id.property_account_receivable_id.id or account_def and account_def.id
            partner_id = ResPartner._find_accounting_partner(order.partner_id).id or False
            if move is None:
                # Create an entry for the sale
                journal_id = self.env['ir.config_parameter'].sudo().get_param(
                    'pos.closing.journal_id_%s' % current_company.id, default=order.sale_journal.id)
                move = self._create_account_move(
                    order.session_id.start_at, order.name, int(journal_id), order.company_id.id)

            def insert_data(data_type, values):
                # if have_to_group_by:
                values.update({
                    'partner_id': partner_id,
                    'move_id': move.id,
                })

                key = self._get_account_move_line_group_data_type_key(data_type, values, {'rounding_method': rounding_method})
                if not key:
                    return

                grouped_data.setdefault(key, [])

                if have_to_group_by:
                    if not grouped_data[key]:
                        grouped_data[key].append(values)
                    else:
                        current_value = grouped_data[key][0]
                        current_value['quantity'] = current_value.get('quantity', 0.0) + values.get('quantity', 0.0)
                        current_value['credit'] = current_value.get('credit', 0.0) + values.get('credit', 0.0)
                        current_value['debit'] = current_value.get('debit', 0.0) + values.get('debit', 0.0)
                        if 'currency_id' in values:
                            current_value['amount_currency'] = current_value.get('amount_currency', 0.0) + values.get('amount_currency', 0.0)
                        if key[0] == 'tax' and rounding_method == 'round_globally':
                            if current_value['debit'] - current_value['credit'] > 0:
                                current_value['debit'] = current_value['debit'] - current_value['credit']
                                current_value['credit'] = 0
                            else:
                                current_value['credit'] = current_value['credit'] - current_value['debit']
                                current_value['debit'] = 0

                else:
                    grouped_data[key].append(values)

            # because of the weird way the pos order is written, we need to make sure there is at least one line,
            # because just after the 'for' loop there are references to 'line' and 'income_account' variables (that
            # are set inside the for loop)
            # TOFIX: a deep refactoring of this method (and class!) is needed
            # in order to get rid of this stupid hack
            assert order.lines, _('The POS order must have lines when calling this method')
            # Create an move for each order line
            cur = order.pricelist_id.currency_id
            cur_company = order.company_id.currency_id
            amount_cur_company = 0.0
            date_order = (order.date_order or fields.Datetime.now())[:10]
            for line in order.lines:
                if cur != cur_company:
                    amount_subtotal = cur.with_context(date=date_order).compute(line.price_subtotal, cur_company)
                else:
                    amount_subtotal = line.price_subtotal

                # Search for the income account
                if line.product_id.property_account_income_id.id:
                    income_account = line.product_id.property_account_income_id.id
                elif line.product_id.categ_id.property_account_income_categ_id.id:
                    income_account = line.product_id.categ_id.property_account_income_categ_id.id
                else:
                    raise UserError(_('Please define income '
                                      'account for this product: "%s" (id:%d).')
                                    % (line.product_id.name, line.product_id.id))

                name = line.product_id.name
                if line.notice:
                    # add discount reason in move
                    name = name + ' (' + line.notice + ')'

                # Create a move for the line for the order line
                # Just like for invoices, a group of taxes must be present on this base line
                # As well as its children
                base_line_tax_ids = _flatten_tax_and_children(line.tax_ids_after_fiscal_position).filtered(lambda tax: tax.type_tax_use in ['sale', 'none'])
                data = {
                    'name': name,
                    'quantity': line.qty,
                    'product_id': line.product_id.id,
                    'account_id': income_account,
                    'analytic_account_id': self._prepare_analytic_account(line),
                    'credit': ((amount_subtotal > 0) and amount_subtotal) or 0.0,
                    'debit': ((amount_subtotal < 0) and -amount_subtotal) or 0.0,
                    'tax_ids': [(6, 0, base_line_tax_ids.ids)],
                    'partner_id': partner_id
                }
                if cur != cur_company:
                    data['currency_id'] = cur.id
                    data['amount_currency'] = -abs(line.price_subtotal) if data.get('credit') else abs(line.price_subtotal)
                    amount_cur_company += data['credit'] - data['debit']
                insert_data('product', data)

                # Create the tax lines
                taxes = line.tax_ids_after_fiscal_position.filtered(lambda t: t.company_id.id == current_company.id)
                if not taxes:
                    continue
                # change price_unit if global_discount_line not 0
                if line.global_disc_line:
                    price = (line.price_unit - (line.global_disc_line / line.qty)) * (1 - (line.discount or 0.0) / 100.0)
                elif line.bank_disc_line:
                    price = (line.price_unit - (line.bank_disc_line / line.qty)) * (1 - (line.discount or 0.0) / 100.0)
                else:
                    price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                for tax in taxes.compute_all(price, cur, line.qty)['taxes']:
                    if cur != cur_company:
                        round_tax = False if rounding_method == 'round_globally' else True
                        amount_tax = cur.with_context(date=date_order).compute(tax['amount'], cur_company, round=round_tax)
                    else:
                        amount_tax = tax['amount']
                    data = {
                        'name': _('Tax') + ' ' + tax['name'],
                        'product_id': line.product_id.id,
                        'quantity': line.qty,
                        'account_id': tax['account_id'] or income_account,
                        'credit': ((amount_tax > 0) and amount_tax) or 0.0,
                        'debit': ((amount_tax < 0) and -amount_tax) or 0.0,
                        'tax_line_id': tax['id'],
                        'partner_id': partner_id,
                        'order_id': order.id
                    }
                    if cur != cur_company:
                        data['currency_id'] = cur.id
                        data['amount_currency'] = -abs(tax['amount']) if data.get('credit') else abs(tax['amount'])
                        amount_cur_company += data['credit'] - data['debit']
                    insert_data('tax', data)

            # round tax lines per order
            if rounding_method == 'round_globally':
                for group_key, group_value in grouped_data.items():
                    if group_key[0] == 'tax':
                        for line in group_value:
                            line['credit'] = cur_company.round(line['credit'])
                            line['debit'] = cur_company.round(line['debit'])
                            if line.get('currency_id'):
                                line['amount_currency'] = cur.round(line.get('amount_currency', 0.0))

            # counterpart
            if cur != cur_company:
                # 'amount_cur_company' contains the sum of the AML converted in the company
                # currency. This makes the logic consistent with 'compute_invoice_totals' from
                # 'account.invoice'. It ensures that the counterpart line is the same amount than
                # the sum of the product and taxes lines.
                amount_total = amount_cur_company
            else:
                amount_total = order.amount_total
            data = {
                'name': _("Trade Receivables"),  # order.name,
                'account_id': order_account,
                'credit': ((amount_total < 0) and -amount_total) or 0.0,
                'debit': ((amount_total > 0) and amount_total) or 0.0,
                'partner_id': partner_id
            }
            if cur != cur_company:
                data['currency_id'] = cur.id
                data['amount_currency'] = -abs(order.amount_total) if data.get('credit') else abs(order.amount_total)
            insert_data('counter_part', data)

            order.write({'state': 'done', 'account_move': move.id})

        if self and order.company_id.anglo_saxon_accounting:
            add_anglosaxon_lines(grouped_data)

        all_lines = []
        for group_key, group_data in grouped_data.items():
            for value in group_data:
                all_lines.append((0, 0, value),)
        if move:  # In case no order was changed
            move.sudo().write({'line_ids': all_lines})
            move.sudo().post()
        return True


class PosOrderLineDiscount(models.Model):
    _inherit = 'pos.order.line'

    flag_disc = fields.Char(string='Flag Disc Bank')

    global_disc_line = fields.Float(string='Global Disc Amount', default=0.0, readonly=True,)

    bank_disc_line = fields.Float(string='Bank Disc Amount', default=0.0, readonly=True,)

    @api.depends('price_unit', 'tax_ids', 'qty', 'discount', 'product_id', 'global_disc_line', 'bank_disc_line')
    def _compute_amount_line_all(self):
        for line in self:
            fpos = line.order_id.fiscal_position_id
            tax_ids_after_fiscal_position = fpos.map_tax(line.tax_ids, line.product_id, line.order_id.partner_id) if fpos else line.tax_ids
            if line.global_disc_line:
                price = (line.price_unit - (line.global_disc_line /line.qty))  * (1 - (line.discount or 0.0) / 100.0)
            elif line.bank_disc_line:
                price = (line.price_unit - (line.bank_disc_line /line.qty))  * (1 - (line.discount or 0.0) / 100.0)
            else:
                price = line.price_unit  * (1 - (line.discount or 0.0) / 100.0)

            taxes = tax_ids_after_fiscal_position.compute_all(price, line.order_id.pricelist_id.currency_id, line.qty, product=line.product_id, partner=line.order_id.partner_id)
            line.update({
                'price_subtotal_incl': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
