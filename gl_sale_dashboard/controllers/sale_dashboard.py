# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class SaleDashboardController(http.Controller):

    @http.route('/sale_dashboard/get_today_data', type='json', auth='user', csrf=False)
    def get_today_data(self):
        return request.env['sale.order'].get_today_data()

    @http.route('/sale_dashboard/get_data_based_date', type='json', auth='user', csrf=False)
    def get_data_based_date(self, from_date=None, to_date=None):
        # Expect from_date and to_date as 'YYYY-MM-DD' strings
        return request.env['sale.order'].get_data_based_date(from_date, to_date)
