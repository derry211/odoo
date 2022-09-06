# -*- coding: utf-8 -*-
from odoo import http

# class MrpCheckAvailableStock(http.Controller):
#     @http.route('/mrp_check_available_stock/mrp_check_available_stock/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mrp_check_available_stock/mrp_check_available_stock/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mrp_check_available_stock.listing', {
#             'root': '/mrp_check_available_stock/mrp_check_available_stock',
#             'objects': http.request.env['mrp_check_available_stock.mrp_check_available_stock'].search([]),
#         })

#     @http.route('/mrp_check_available_stock/mrp_check_available_stock/objects/<model("mrp_check_available_stock.mrp_check_available_stock"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mrp_check_available_stock.object', {
#             'object': obj
#         })