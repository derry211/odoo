import xlsxwriter
import base64
from odoo import fields, models, api
from io import BytesIO
from datetime import datetime, timedelta, date
from pytz import timezone
import pytz
import calendar

class InventoryTurnoverReportWizard(models.TransientModel):
    _name = "inventory.turnover.report.wizard"
    _description = "Inventory Turnover Report Wizard"

    @api.model
    def _get_default_start_date(self):
        current_date = self.get_default_date_model()
        return current_date.strftime('%Y-%m-01')

    @api.model
    def _get_default_end_date(self):
        current_date = self.get_default_date_model()
        end_of_month = str(calendar.monthrange(current_date.year, current_date.month)[1])
        return current_date.strftime('%Y-%m-'+end_of_month)

    @api.model
    def get_default_date_model(self):
        return pytz.UTC.localize(datetime.now()).astimezone(timezone(self.env.user.tz or 'UTC'))

    datas = fields.Binary('File', readonly=True)
    datas_fname = fields.Char('Filename', readonly=True)
    product_ids = fields.Many2many('product.product', 'inventory_turnover_report_product_rel', 'inventory_turnover_report_id',
                                   'product_id', 'Products')
    categ_ids = fields.Many2many('product.category', 'inventory_turnover_report_categ_rel', 'inventory_turnover_report_id',
                                 'categ_id', 'Categories')
    start_date = fields.Date(
        string='Start Date',
        default=_get_default_start_date,
        required=True)
    end_date = fields.Date(
        string='End Date',
        default=_get_default_end_date,
        required=True)

    def print_excel_report(self):
        start_date = self.start_date + ' 17:00:00'
        end_date = self.end_date + ' 17:00:00'
        datetime_string = self.get_default_date_model().strftime("%Y-%m-%d %H:%M:%S")
        date_string = self.get_default_date_model().strftime("%Y-%m-%d")
        report_name = 'Inventory Turnover Report'
        filename = '%s %s' % (report_name, date_string)

        columns = [
            ('Product', 50, 'char', 'char'),
            ('Quantity On Hand', 20, 'float', 'float'),
            ('Quantity Ordered', 20, 'float', 'float'),
            ('Turn Over', 20, 'float', 'float'),
        ]

        datetime_format = '%Y-%m-%d %H:%M:%S'
        utc = datetime.now().strftime(datetime_format)
        utc = datetime.strptime(utc, datetime_format)
        tz = self.get_default_date_model().strftime(datetime_format)
        tz = datetime.strptime(tz, datetime_format)
        duration = tz - utc
        hours = duration.seconds / 60 / 60
        if hours > 1 or hours < 1:
            hours = str(hours) + ' hours'
        else:
            hours = str(hours) + ' hour'

        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        wbf, workbook = self.add_workbook_format(workbook)

        worksheets = {
            'Turnover FG': ['FG%'],
            'Turnover RM-PM': ['RM%','PM%'],
        }
        for title, categ_names in worksheets.items():
            worksheet = workbook.add_worksheet(title)
            worksheet.merge_range('A2:D3', report_name, wbf['title_doc'])
            worksheet.write('A5', 'Period %s s/d %s'%(self.start_date, self.end_date), wbf['content_datetime'])

            row = 7

            col = 0
            for column in columns:
                column_name = column[0]
                column_width = column[1]
                column_type = column[2]
                worksheet.set_column(col, col, column_width)
                worksheet.write(row - 1, col, column_name, wbf['header_orange'])

                col += 1
            # worksheet.set_row(4, 40)

            row += 1
            row1 = row
            no = 1

            column_float_number = {}
            domain = []
            if self.product_ids :
                domain.append(('id','in',self.product_ids.ids))
            if self.categ_ids :
                domain.append(('categ_id','child_of',self.categ_ids.ids))
            # filter sesuai klasifikasi sheet
            categ_ids = categ_obj = self.env['product.category']
            for categ_name in categ_names :
                categ_ids += categ_obj.search([('name','ilike',categ_name)])
            domain.append(('categ_id','child_of',categ_ids.ids))
            product_ids = self.env['product.product'].search(domain)
            for product_id in product_ids :
                query = """
                    SELECT
                        product_name,
                        onhand_qty,
                        ordered_qty,
                        case when ordered_qty != 0 then onhand_qty/ordered_qty else 0 end
                    FROM (
                        SELECT 
                            product_name,
                            sum(onhand_qty) as onhand_qty,
                            sum(ordered_qty) as ordered_qty
                        FROM (
                            SELECT
                                pt.name as product_name,
                                sm.product_qty as onhand_qty,
                                0 as ordered_qty
                            FROM 
                                stock_move sm
                            LEFT JOIN 
                                product_product prod on prod.id=sm.product_id
                            LEFT JOIN 
                                product_template pt on pt.id=prod.product_tmpl_id
                            LEFT JOIN 
                                stock_location sl on sl.id=sm.location_id
                            LEFT JOIN 
                                stock_location dl on dl.id=sm.location_dest_id
                            WHERE
                                sm.state = 'done'
                                and sm.product_id = %s
                                and sl.usage != 'internal'
                                and dl.usage = 'internal'
                                and sm.date >= '%s'
                                and sm.date < '%s'
                                
                            UNION ALL
                            
                            SELECT
                                pt.name as product_name,
                                0 as onhand_qty,
                                sm.product_qty as ordered_qty
                            FROM 
                                stock_move sm
                            LEFT JOIN 
                                product_product prod on prod.id=sm.product_id
                            LEFT JOIN 
                                product_template pt on pt.id=prod.product_tmpl_id
                            LEFT JOIN 
                                stock_location sl on sl.id=sm.location_id
                            LEFT JOIN 
                                stock_location dl on dl.id=sm.location_dest_id
                            WHERE
                                sm.state = 'done'
                                and sm.product_id = %s
                                and sl.usage = 'internal'
                                and dl.usage != 'internal'
                                and sm.date >= '%s'
                                and sm.date < '%s'
                        ) as inventory_report
                        WHERE
                            onhand_qty != 0 or ordered_qty != 0
                        GROUP BY
                            product_name
                    ) as final_inventory_report
                """%(product_id.id, start_date, end_date, product_id.id, start_date, end_date)

                self._cr.execute(query)
                result = self._cr.fetchall()

                for res in result:
                    col = 0
                    for column in columns:
                        column_name = column[0]
                        column_width = column[1]
                        column_type = column[2]
                        if column_type == 'char':
                            col_value = res[col] if res[col] else ''
                            wbf_value = wbf['content']
                        elif column_type == 'no':
                            col_value = no
                            wbf_value = wbf['content']
                        elif column_type == 'datetime':
                            col_value = res[col].strftime('%Y-%m-%d %H:%M:%S') if res[col] else ''
                            wbf_value = wbf['content']
                        else:
                            col_value = res[col] if res[col] else 0
                            if column_type == 'float':
                                wbf_value = wbf['content_float']
                            else:  # number
                                wbf_value = wbf['content_number']
                            column_float_number[col] = column_float_number.get(col, 0) + col_value

                        worksheet.write(row - 1, col, col_value, wbf_value)

                        col += 1

                    row += 1
                    no += 1

            worksheet.write('A%s' % (row), 'Grand Total', wbf['total_orange'])
            total_onhand = 0
            total_order = 0
            for x in range(len(columns)):
                if x == 0:
                    continue
                column_type = columns[x][3]
                if column_type == 'char':
                    worksheet.write(row - 1, x, '', wbf['total_orange'])
                else:
                    if column_type == 'float':
                        wbf_value = wbf['total_float_orange']
                    else:  # number
                        wbf_value = wbf['total_number_orange']
                    if x in column_float_number:
                        if x == 3 :
                            value = column_float_number[1]/column_float_number[2] if column_float_number[2] else 0.0
                        else :
                            value = column_float_number[x]
                        worksheet.write(row - 1, x, value, wbf_value)
                    else:
                        worksheet.write(row - 1, x, 0, wbf_value)

            worksheet.write('A%s' % (row + 2), 'Date %s (%s)' % (datetime_string, self.env.user.tz or 'UTC'),
                            wbf['content_datetime'])
        workbook.close()
        out = base64.encodestring(fp.getvalue())
        self.write({'datas': out, 'datas_fname': filename})
        fp.close()
        filename += '%2Exlsx'

        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': 'web/content/?model=' + self._name + '&id=' + str(
                self.id) + '&field=datas&download=true&filename=' + filename,
        }

    def add_workbook_format(self, workbook):
        colors = {
            'white_orange': '#FFFFDB',
            'orange': '#FFC300',
            'red': '#FF0000',
            'yellow': '#F6FA03',
        }

        wbf = {}
        wbf['header'] = workbook.add_format(
            {'bold': 1, 'align': 'center', 'bg_color': '#FFFFDB', 'font_color': '#000000', 'font_name': 'Georgia'})
        wbf['header'].set_border()

        wbf['header_orange'] = workbook.add_format(
            {'bold': 1, 'align': 'center', 'valign': 'vcenter', 'bg_color': colors['orange'], 'font_color': '#000000',
             'font_name': 'Georgia'})
        wbf['header_orange'].set_border()
        wbf['header_orange'].set_text_wrap()

        wbf['header_yellow'] = workbook.add_format(
            {'bold': 1, 'align': 'center', 'bg_color': colors['yellow'], 'font_color': '#000000',
             'font_name': 'Georgia'})
        wbf['header_yellow'].set_border()

        wbf['header_no'] = workbook.add_format(
            {'bold': 1, 'align': 'center', 'bg_color': '#FFFFDB', 'font_color': '#000000', 'font_name': 'Georgia'})
        wbf['header_no'].set_border()
        wbf['header_no'].set_align('vcenter')

        wbf['footer'] = workbook.add_format({'align': 'left', 'font_name': 'Georgia'})

        wbf['content_datetime'] = workbook.add_format({'num_format': 'yyyy-mm-dd hh:mm:ss', 'font_name': 'Georgia'})
        wbf['content_datetime'].set_left()
        # wbf['content_datetime'].set_right()

        wbf['content_date'] = workbook.add_format({'num_format': 'yyyy-mm-dd', 'font_name': 'Georgia'})
        wbf['content_date'].set_left()
        wbf['content_date'].set_right()

        wbf['title_doc'] = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 20,
            'font_name': 'Georgia',
        })

        wbf['company'] = workbook.add_format({'align': 'left', 'font_name': 'Georgia'})
        wbf['company'].set_font_size(11)

        wbf['content'] = workbook.add_format()
        wbf['content'].set_left()
        wbf['content'].set_right()

        wbf['content_float'] = workbook.add_format({'align': 'right', 'num_format': '#,##0.00', 'font_name': 'Georgia'})
        wbf['content_float'].set_right()
        wbf['content_float'].set_left()

        wbf['content_number'] = workbook.add_format({'align': 'right', 'num_format': '#,##0', 'font_name': 'Georgia'})
        wbf['content_number'].set_right()
        wbf['content_number'].set_left()

        wbf['content_percent'] = workbook.add_format({'align': 'right', 'num_format': '0.00%', 'font_name': 'Georgia'})
        wbf['content_percent'].set_right()
        wbf['content_percent'].set_left()

        wbf['total_float'] = workbook.add_format(
            {'bold': 1, 'bg_color': colors['white_orange'], 'align': 'right', 'num_format': '#,##0.00',
             'font_name': 'Georgia'})
        wbf['total_float'].set_top()
        wbf['total_float'].set_bottom()
        wbf['total_float'].set_left()
        wbf['total_float'].set_right()

        wbf['total_number'] = workbook.add_format(
            {'align': 'right', 'bg_color': colors['white_orange'], 'bold': 1, 'num_format': '#,##0',
             'font_name': 'Georgia'})
        wbf['total_number'].set_top()
        wbf['total_number'].set_bottom()
        wbf['total_number'].set_left()
        wbf['total_number'].set_right()

        wbf['total'] = workbook.add_format(
            {'bold': 1, 'bg_color': colors['white_orange'], 'align': 'center', 'font_name': 'Georgia'})
        wbf['total'].set_left()
        wbf['total'].set_right()
        wbf['total'].set_top()
        wbf['total'].set_bottom()

        wbf['total_float_yellow'] = workbook.add_format(
            {'bold': 1, 'bg_color': colors['yellow'], 'align': 'right', 'num_format': '#,##0.00',
             'font_name': 'Georgia'})
        wbf['total_float_yellow'].set_top()
        wbf['total_float_yellow'].set_bottom()
        wbf['total_float_yellow'].set_left()
        wbf['total_float_yellow'].set_right()

        wbf['total_number_yellow'] = workbook.add_format(
            {'align': 'right', 'bg_color': colors['yellow'], 'bold': 1, 'num_format': '#,##0', 'font_name': 'Georgia'})
        wbf['total_number_yellow'].set_top()
        wbf['total_number_yellow'].set_bottom()
        wbf['total_number_yellow'].set_left()
        wbf['total_number_yellow'].set_right()

        wbf['total_yellow'] = workbook.add_format(
            {'bold': 1, 'bg_color': colors['yellow'], 'align': 'center', 'font_name': 'Georgia'})
        wbf['total_yellow'].set_left()
        wbf['total_yellow'].set_right()
        wbf['total_yellow'].set_top()
        wbf['total_yellow'].set_bottom()

        wbf['total_float_orange'] = workbook.add_format(
            {'bold': 1, 'bg_color': colors['orange'], 'align': 'right', 'num_format': '#,##0.00',
             'font_name': 'Georgia'})
        wbf['total_float_orange'].set_top()
        wbf['total_float_orange'].set_bottom()
        wbf['total_float_orange'].set_left()
        wbf['total_float_orange'].set_right()

        wbf['total_number_orange'] = workbook.add_format(
            {'align': 'right', 'bg_color': colors['orange'], 'bold': 1, 'num_format': '#,##0', 'font_name': 'Georgia'})
        wbf['total_number_orange'].set_top()
        wbf['total_number_orange'].set_bottom()
        wbf['total_number_orange'].set_left()
        wbf['total_number_orange'].set_right()

        wbf['total_orange'] = workbook.add_format(
            {'bold': 1, 'bg_color': colors['orange'], 'align': 'center', 'font_name': 'Georgia'})
        wbf['total_orange'].set_left()
        wbf['total_orange'].set_right()
        wbf['total_orange'].set_top()
        wbf['total_orange'].set_bottom()

        wbf['header_detail_space'] = workbook.add_format({'font_name': 'Georgia'})
        wbf['header_detail_space'].set_left()
        wbf['header_detail_space'].set_right()
        wbf['header_detail_space'].set_top()
        wbf['header_detail_space'].set_bottom()

        wbf['header_detail'] = workbook.add_format({'bg_color': '#E0FFC2', 'font_name': 'Georgia'})
        wbf['header_detail'].set_left()
        wbf['header_detail'].set_right()
        wbf['header_detail'].set_top()
        wbf['header_detail'].set_bottom()

        return wbf, workbook
