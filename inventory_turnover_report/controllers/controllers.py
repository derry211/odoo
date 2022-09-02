# -*- coding: utf-8 -*-
from odoo import http

# class InventoryTurnoverReport(http.Controller):
#     @http.route('/inventory_turnover_report/inventory_turnover_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/inventory_turnover_report/inventory_turnover_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('inventory_turnover_report.listing', {
#             'root': '/inventory_turnover_report/inventory_turnover_report',
#             'objects': http.request.env['inventory_turnover_report.inventory_turnover_report'].search([]),
#         })

#     @http.route('/inventory_turnover_report/inventory_turnover_report/objects/<model("inventory_turnover_report.inventory_turnover_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('inventory_turnover_report.object', {
#             'object': obj
#         })