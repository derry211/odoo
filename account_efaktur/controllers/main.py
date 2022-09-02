from odoo import http, fields, _
from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception, content_disposition
import base64
import operator
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import csv
from odoo.tools import pycompat
from odoo.exceptions import ValidationError, UserError


class Binary(http.Controller):

    def from_data(self, fields, rows):
        fp = StringIO()
        writer = csv.writer(fp, delimiter=';', quoting=csv.QUOTE_NONE)

        for field in fields:
            writer.writerow([name for name in field])
            # writer.writerow([name.encode('utf-8') for name in field])

        for row in rows:
            for data in row:
                row = []
                for d in data:
                    if isinstance(d, bytes):
                        try:
                            d = d.encode('utf-8')
                        except UnicodeError:
                            pass

                    # Spreadsheet apps tend to detect formulas on leading =, +
                    # and -
                    if type(d) is str and d.startswith(('=', '-', '+')):
                        d = "'" + d

                    row.append(d)
                writer.writerow(row)

        fp.seek(0)
        data = fp.read()
        fp.close()
        return data

    @http.route('/web/binary/download_imporbarang', type='http', auth="user")
    @serialize_exception
    def download_imporbarang(self, model, id, filename=None, **kw):
        record = request.env[model].browse(int(id))

        headers = [['OB', 'KODE_OBJECT', 'NAMA', 'HARGA_SATUAN']]
        export_data = []
        for line in record.invoice_line_ids:
            export_data.append(
                [['OB', line.product_id.barcode, line.product_id.name, line.price_unit]])

        if not filename:
            filename = '%s_%s' % (model.replace('.', '_'), id)

        return request.make_response(self.from_data(headers, export_data),
                                     [('Content-Type', 'text/csv;charset=utf8'),
                                      ('Content-Disposition', content_disposition(filename))])

    @http.route('/web/binary/download_imporlawan', type='http', auth="user")
    @serialize_exception
    def download_imporlawan(self, model, id, filename=None, **kw):
        record = request.env[model].browse(int(id))

        headers = [
            [
                'LT', 'NPWP', 'NAMA', 'JALAN',
                'BLOK', 'NOMOR',
                'RT', 'RW',
                'KECAMATAN', 'KELURAHAN',
                'KABUPATEN', 'PROPINSI',
                'KODE_POS', 'NOMOR_TELEPON']]
        export_data = []
        export_data.append([
            [
                'LT', str(record.partner_id.npwp or ''),
                str(record.partner_id.name),
                str(record.partner_id.street or ''),
                str(record.partner_id.blok or ''),
                str(record.partner_id.nomor or ''),
                str(record.partner_id.rt or ''),
                str(record.partner_id.rw or ''),
                str(record.partner_id.kecamatan_id.name or ''),
                str(record.partner_id.kelurahan_id.name or ''),
                str(record.partner_id.city_id.name or ''),
                str(record.partner_id.state_id.name or ''),
                str(record.partner_id.zip or ''),
                str(record.partner_id.phone or ''),
            ]])

        if not filename:
            filename = '%s_%s' % (model.replace('.', '_'), id)
        return request.make_response(self.from_data(headers, export_data),
                                     [('Content-Type', 'text/csv;charset=utf8'),
                                      ('Content-Disposition', content_disposition(filename))])

    @http.route('/web/binary/download_imporpk', type='http', auth="user")
    @serialize_exception
    def download_imporpk(self, model, id, filename=None, **kw):
        records = request.env[model].browse(eval(id))

        headers = [
            [
                'FK', 'KD_JENIS_TRANSAKSI', 'FG_PENGGANTI', 'NOMOR_FAKTUR', 'MASA_PAJAK', 'TAHUN_PAJAK',
                'TANGGAL_FAKTUR', 'NPWP', 'NAMA', 'ALAMAT_LENGKAP', 'JUMLAH_DPP', 'JUMLAH_PPN',
                'JUMLAH_PPNBM', 'ID_KETERANGAN_TAMBAHAN', 'FG_UANG_MUKA', 'UANG_MUKA_DPP', 'UANG_MUKA_PPN',
                'UANG_MUKA_PPNBM', 'REFERENSI','KODE_DOKUMEN_PENDUKUNG'
            ],
            [
                'LT', 'NPWP', 'NAMA', 'JALAN', 'BLOK', 'NOMOR', 'RT', 'RW', 'KECAMATAN',
                'KELURAHAN', 'KABUPATEN', 'PROPINSI', 'KODE_POS', 'NOMOR_TELEPON'
            ],
            [
                'OF', 'KODE_OBJEK', 'NAMA', 'HARGA_SATUAN', 'JUMLAH_BARANG',
                'HARGA_TOTAL', 'DISKON', 'DPP', 'PPN', 'TARIF_PPNBM', 'PPNBM'
            ]
        ]
        export_data = []
        for inv in records:
            date_format = fields.Date.from_string(inv.date_invoice)
            partner_company = inv.partner_id.parent_id if inv.partner_id.parent_id else inv.partner_id
            row_data = [
                [
                    'FK', str('01'), '0', inv.no_faktur, date_format and date_format.month or '',
                    date_format and date_format.year or '',
                    date_format and date_format.strftime("%d/%m/%Y") or '',
                    inv.partner_id.parent_id.npwp or inv.partner_id.npwp or '', str.upper(inv.partner_id.parent_id.x_studio_field_ZUJ5E or inv.partner_id.x_studio_field_ZUJ5E or inv.partner_id.parent_id.name or inv.partner_id.name),
                    str.upper(inv.partner_id.x_studio_field_TCl1z or inv.partner_id.parent_id.x_studio_field_TCl1z or '') 
                    #+ 
                    #' Blok ' + str(partner_company.blok or '') + 
                    #' No.' + str(partner_company.nomor or '') + 
                    #' RT:' + str(partner_company.rt or '') + 
                    #' RW:' + str(partner_company.rw or '') + 
                    #' Kel.' + str(partner_company.kelurahan_id.name or '') + 
                    #' Kec.' + str(partner_company.kecamatan_id.name or '') + 
                    #' Kota/Kab.' + str(partner_company.city_id.name or '') + 
                    #str(partner_company.state_id.name or '') + 
                    #str(partner_company.zip or '')
                    ,
                    int(inv.amount_tax * 100/11), int(inv.amount_tax),
                    '0', '', '0', '0', '0', '0',  (inv.origin) + ' ' + (inv.number)
                ],
                [
                    'FAPR', str.upper(inv.company_id.partner_id.name or ''),
                    str(inv.company_id.partner_id.x_studio_field_TCl1z or '')  
                    
                    #' Blok ' + str(inv.company_id.partner_id.blok or '') + 
                    #' No.' + str(inv.company_id.partner_id.nomor or '') + 
                    #' RT:' + str(inv.company_id.partner_id.rt or '') + 
                    #' RW:' + str(inv.company_id.partner_id.rw or '') + 
                    #' Kel.' + str(inv.company_id.partner_id.kelurahan_id.name or '') + 
                    #' Kec.' + str(inv.company_id.partner_id.kecamatan_id.name or '') + 
                    #' Kota/Kab.' + str(inv.company_id.partner_id.city_id.name or '') + 
                    #str(inv.company_id.partner_id.state_id.name or '') + 
                    #str(inv.company_id.partner_id.zip or '')
                ],
            ]
            # catet jumlah isi list
            len_row_data = len(row_data)

            i = 1
            for line in inv.invoice_line_ids:
                if not line.invoice_line_tax_ids or \
                        sum([tax.amount for tax in line.invoice_line_tax_ids]) == 0:
                    continue
                row_data.append(['OF', line.product_id.barcode,(line.product_id.name[16:]), (line.price_unit), int(line.quantity), (line.price_unit * line.quantity),
                                 (line.price_unit * line.quantity * line.discount / 100), (line.price_subtotal), (line.price_subtotal * 11 / 100), '0', '0'])
                i += 1
            # jika tdk ada penambahan maka hapus 2 row terakhir
            if len(row_data) == len_row_data:
                del(row_data[len_row_data - 1])
                del(row_data[len_row_data - 2])
            # if not row_data:
            #     raise UserError(_("There is no taxable data to import."))
            export_data.append(row_data)

        if not filename:
            filename = '%s_%s' % (model.replace('.', '_'), id)
        return request.make_response(self.from_data(headers, export_data),
                                     [('Content-Type', 'text/csv;charset=utf8'),
                                      ('Content-Disposition', content_disposition(filename))])

    @http.route('/web/binary/download_imporpm', type='http', auth="user")
    @serialize_exception
    def download_imporpm(self, model, id, filename=None, **kw):
        records = request.env[model].browse(eval(id))

        headers = [
            ['FM', 'KD_JENIS_TRANSAKSI', 'FG_PENGGANTI', 'NOMOR_FAKTUR', 'MASA_PAJAK', 'TAHUN_PAJAK', 'TANGGAL_FAKTUR',
                'NPWP', 'NAMA', 'ALAMAT_LENGKAP', 'JUMLAH_DPP', 'JUMLAH_PPN', 'JUMLAH_PPNBM', 'IS_CREDITABLE'],
        ]
        export_data = []
        for inv in records:
            row_data = [
                ['FM', '01', '0', inv.number, '12', inv.date_invoice, inv.date_invoice, inv.company_id.partner_id.npwp, inv.company_id.partner_id.name, str(
                    inv.company_id.partner_id.street) + ' Blok ' + str(inv.company_id.partner_id.blok), inv.amount_total, inv.amount_tax, 0, 1],
            ]
            export_data.append(row_data)

        if not filename:
            filename = '%s_%s' % (model.replace('.', '_'), id)
        return request.make_response(self.from_data(headers, export_data),
                                     [('Content-Type', 'text/csv;charset=utf8'),
                                      ('Content-Disposition', content_disposition(filename))])
