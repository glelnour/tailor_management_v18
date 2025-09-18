# -*- coding: utf-8 -*-
from odoo import models, fields, api
import requests

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    fiserv_payment_link = fields.Char("Fiserv Payment Link")
    paymentLinkId = fields.Char()

    def check_payment_status(self):
        sale_orders = self.env['sale.order'].search([])
        for so in sale_orders:
            if so.paymentLinkId and so.state in ['approved']:
                url = "https://prod.emea.api.fiservapps.com/sandbox/exp/v1/payment-links/%s"%(so.paymentLinkId)
                API_KEY = so.company_id.fiserv_api_key
                headers = {
                    'Api-Key': API_KEY,
                    "accept": "application/json",
                    "content-type": "application/json"
                }
                print("===", url, headers)
                response = requests.get(url, headers=headers)
                data = response.json()
                transactionStatus = data.get('transactionStatus')
                if transactionStatus == 'APPROVED':
                    so.action_confirm()
                    so.message_post(
                        body="✅ Order confirmed via Fiserv Payment"
                    )