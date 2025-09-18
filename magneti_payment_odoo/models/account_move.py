# -*- coding: utf-8 -*-
from odoo import models, fields, api
import requests

class AccountMove(models.Model):
    _inherit = 'account.move'

    fiserv_payment_link = fields.Char("Fiserv Payment Link")
    paymentLinkId = fields.Char()

    # def check_payment_status(self):
    #     invoices = self.env['account.move'].search([('move_type','=', 'out_invoice')])
    #     for invoice in invoices:
    #         if invoice.paymentLinkId and invoice.state in ['draft']:
    #             url = "https://prod.emea.api.fiservapps.com/sandbox/exp/v1/payment-links/%s"%(so.paymentLinkId)
    #             API_KEY = so.company_id.fiserv_api_key
    #             headers = {
    #                 'Api-Key': API_KEY,
    #                 "accept": "application/json",
    #                 "content-type": "application/json"
    #             }
    #             print("===", url, headers)
    #             response = requests.get(url, headers=headers)
    #             data = response.json()
    #             transactionStatus = data.get('transactionStatus')
    #             if transactionStatus == 'APPROVED':
    #                 so.action_confirm()
    #                 so.message_post(
    #                     body="✅ Order confirmed via Fiserv Payment"
    #                 )