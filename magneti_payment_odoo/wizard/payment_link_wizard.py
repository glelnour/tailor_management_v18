# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from werkzeug import urls
from odoo.exceptions import UserError
import requests
import json
import uuid
import time
import hmac
import hashlib
import base64
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class PaymentLinkWizard(models.TransientModel):
    _inherit = 'payment.link.wizard'

    @api.depends('amount', 'currency_id', 'partner_id', 'company_id')
    def _compute_link(self):
        for payment_link in self:
            related_document = self.env[payment_link.res_model].browse(payment_link.res_id)
            if payment_link.res_model == 'sale.order':
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                sale_order = related_document
                company = sale_order.company_id

                store_id = company.fiserv_store_id
                API_SECRET = company.fiserv_shared_secret
                API_KEY = company.fiserv_api_key

                if not store_id or not API_SECRET or not API_KEY:
                    raise UserError(
                        _("Fiserv Store ID, API Key and Shared Secret must be configured in the company settings.")
                    )

                expiry_datetime = (datetime.utcnow() + timedelta(days=7)).isoformat("T") + "Z"

                # Basket lines
                line_vals = []
                for line in sale_order.order_line:
                    line_vals.append({
                        "itemIdentifier": line.product_id.default_code or "",
                        "name": line.product_id.name,
                        "price": line.price_unit,
                        "quantity": line.product_uom_qty,
                        "shippingCost": 0,
                        "valueAddedTax": 0,
                        "miscellaneousFee": 0,
                        "total": line.price_subtotal,
                    })

                url = "https://prod.emea.api.fiservapps.com/sandbox/exp/v1/payment-links"

                payload = {
                    "storeId": store_id,
                    "merchantTransactionId": sale_order.name,
                    "transactionOrigin": "ECOM",
                    "transactionType": "SALE",
                    "transactionAmount": {
                        "components": {
                            "subtotal": sale_order.amount_untaxed,
                            "vatAmount": sale_order.amount_tax,
                            "shipping": 0,
                        },
                        "total": payment_link.amount,
                        "currency": payment_link.currency_id.name
                    },
                    "order": {
                        "shipping": {
                            "person": {
                                "firstName": sale_order.partner_id.name or "",
                                "lastName": "",
                                "dateOfBirth": ""
                            },
                            "contact": {
                                "phone": sale_order.partner_id.phone or "",
                                "mobilePhone": sale_order.partner_id.mobile or "",
                                "email": sale_order.partner_id.email or "",
                                "fax": ""
                            },
                            "address": {
                                "address1": sale_order.partner_id.street or "",
                                "address2": sale_order.partner_id.street2 or "",
                                "city": sale_order.partner_id.city or "",
                                "company": sale_order.partner_id.company_name or "",
                                "country": sale_order.partner_id.country_id.name or "",
                                "postalCode": sale_order.partner_id.zip or "",
                                "region": ""
                            }
                        },
                        "billing": {
                            "person": {
                                "firstName": sale_order.partner_id.name or "",
                                "lastName": "",
                                "dateOfBirth": ""
                            },
                            "contact": {
                                "phone": sale_order.partner_id.phone or "",
                                "mobilePhone": sale_order.partner_id.mobile or "",
                                "email": sale_order.partner_id.email or "",
                                "fax": ""
                            },
                            "address": {
                                "address1": sale_order.partner_id.street or "",
                                "address2": sale_order.partner_id.street2 or "",
                                "city": sale_order.partner_id.city or "",
                                "company": sale_order.partner_id.company_name or "",
                                "country": sale_order.partner_id.country_id.name or "",
                                "postalCode": sale_order.partner_id.zip or "",
                                "region": ""
                            }
                        },
                        "orderDetails": {
                            "customerId": sale_order.partner_id.ref or "",
                            "dynamicMerchantName": company.name,
                            "invoiceNumber": sale_order.name,
                            "purchaseOrderNumber": sale_order.client_order_ref or ""
                        },
                        "basket": {"lineItems": line_vals}
                    },
                    "checkoutSettings": {
                        "locale": "en_GB",
                        "redirectBackUrls": {
                            "successUrl": "%s/payment/fiserv/success" % base_url,
                            "failureUrl": "%s/payment/fiserv/failure" % base_url
                        },
                        "preSelectedPaymentMethod": "cards",
                        "webHooksUrl": "%s/fiserv/payment/success" % base_url
                    },
                    "paymentMethodDetails": {
                        "cards": {
                            "authenticationPreferences": {
                                "authenticateTransaction": True,
                                "challengeIndicator": "01",
                                "skipTra": False,
                                "scaExemptionType": "LOW_VALUE_EXEMPTION"
                            }
                        },
                    },
                    "paymentLinkDetails": {"expiryDateTime": expiry_datetime},
                }

                try:
                    json_payload = json.dumps(payload, separators=(",", ":"))

                    clientRequestId = str(uuid.uuid4())

                    timestamp = str(int(time.time() * 1000))

                    message = '{}{}{}{}'.format(API_KEY, clientRequestId, timestamp, str(json_payload))

                    signature = hmac.new(API_SECRET.encode(), message.encode(), hashlib.sha256).digest()
                    b64_sig = base64.b64encode(signature).decode()

                    headers = {
                        'Content-Type': "application/json",
                        'Api-Key': API_KEY,
                        'Timestamp': timestamp,
                        'Client-Request-Id': clientRequestId,
                        'Message-Signature': b64_sig
                    }

                    response = requests.post(url, headers=headers, data=json_payload)
                    print("======", response, response.json())
                    response.raise_for_status()
                    data = response.json()

                    link = data['paymentLink'].get('paymentLinkUrl')
                    if not link:
                        raise UserError(_("Fiserv response missing payment link: %s") % response.text)

                    payment_link.link = link
                    sale_order.fiserv_payment_link = link
                    sale_order.paymentLinkId = data['paymentLink'].get('paymentLinkId')
                    sale_order.message_post(
                        body=_("Fiserv Payment Link: <a href='%s' target='_blank'>Copy Link</a>") % link
                    )

                except requests.exceptions.RequestException as e:
                    raise UserError(_("Failed to generate Fiserv payment link: %s") % str(e))
            elif payment_link.res_model == 'account.move':
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                account_move = related_document
                company = account_move.company_id

                store_id = company.fiserv_store_id
                API_SECRET = company.fiserv_shared_secret
                API_KEY = company.fiserv_api_key

                if not store_id or not API_SECRET or not API_KEY:
                    raise UserError(
                        _("Fiserv Store ID, API Key and Shared Secret must be configured in the company settings.")
                    )

                expiry_datetime = (datetime.utcnow() + timedelta(days=7)).isoformat("T") + "Z"

                # Basket lines
                line_vals = []
                for line in account_move.invoice_line_ids:
                    line_vals.append({
                        "itemIdentifier": line.product_id.default_code or "",
                        "name": line.product_id.name,
                        "price": line.price_unit,
                        "quantity": line.quantity,
                        "shippingCost": 0,
                        "valueAddedTax": 0,
                        "miscellaneousFee": 0,
                        "total": line.price_subtotal,
                    })

                url = "https://prod.emea.api.fiservapps.com/sandbox/exp/v1/payment-links"

                payload = {
                    "storeId": store_id,
                    "merchantTransactionId": account_move.name or 'INVOICE',
                    "transactionOrigin": "ECOM",
                    "transactionType": "SALE",
                    "transactionAmount": {
                        "components": {
                            "subtotal": account_move.amount_untaxed,
                            "vatAmount": account_move.amount_tax,
                            "shipping": 0,
                        },
                        "total": payment_link.amount,
                        "currency": payment_link.currency_id.name
                    },
                    "order": {
                        "shipping": {
                            "person": {
                                "firstName": account_move.partner_id.name or "",
                                "lastName": "",
                                "dateOfBirth": ""
                            },
                            "contact": {
                                "phone": account_move.partner_id.phone or "",
                                "mobilePhone": account_move.partner_id.mobile or "",
                                "email": account_move.partner_id.email or "",
                                "fax": ""
                            },
                            "address": {
                                "address1": account_move.partner_id.street or "",
                                "address2": account_move.partner_id.street2 or "",
                                "city": account_move.partner_id.city or "",
                                "company": account_move.partner_id.company_name or "",
                                "country": account_move.partner_id.country_id.name or "",
                                "postalCode": account_move.partner_id.zip or "",
                                "region": ""
                            }
                        },
                        "billing": {
                            "person": {
                                "firstName": account_move.partner_id.name or "",
                                "lastName": "",
                                "dateOfBirth": ""
                            },
                            "contact": {
                                "phone": account_move.partner_id.phone or "",
                                "mobilePhone": account_move.partner_id.mobile or "",
                                "email": account_move.partner_id.email or "",
                                "fax": ""
                            },
                            "address": {
                                "address1": account_move.partner_id.street or "",
                                "address2": account_move.partner_id.street2 or "",
                                "city": account_move.partner_id.city or "",
                                "company": account_move.partner_id.company_name or "",
                                "country": account_move.partner_id.country_id.name or "",
                                "postalCode": account_move.partner_id.zip or "",
                                "region": ""
                            }
                        },
                        "orderDetails": {
                            "customerId": account_move.partner_id.ref or "",
                            "dynamicMerchantName": company.name,
                            "invoiceNumber": account_move.name or 'INVOICE',
                            "purchaseOrderNumber": account_move.ref or ""
                        },
                        "basket": {"lineItems": line_vals}
                    },
                    "checkoutSettings": {
                        "locale": "en_GB",
                        "redirectBackUrls": {
                            "successUrl": "%s/payment/fiserv/success" % base_url,
                            "failureUrl": "%s/payment/fiserv/failure" % base_url
                        },
                        "preSelectedPaymentMethod": "cards",
                        "webHooksUrl": "%s/fiserv/payment/success" % base_url
                    },
                    "paymentMethodDetails": {
                        "cards": {
                            "authenticationPreferences": {
                                "authenticateTransaction": True,
                                "challengeIndicator": "01",
                                "skipTra": False,
                                "scaExemptionType": "LOW_VALUE_EXEMPTION"
                            }
                        },
                    },
                    "paymentLinkDetails": {"expiryDateTime": expiry_datetime},
                }

                try:
                    json_payload = json.dumps(payload, separators=(",", ":"))

                    clientRequestId = str(uuid.uuid4())

                    timestamp = str(int(time.time() * 1000))

                    message = '{}{}{}{}'.format(API_KEY, clientRequestId, timestamp, str(json_payload))

                    signature = hmac.new(API_SECRET.encode(), message.encode(), hashlib.sha256).digest()
                    b64_sig = base64.b64encode(signature).decode()

                    headers = {
                        'Content-Type': "application/json",
                        'Api-Key': API_KEY,
                        'Timestamp': timestamp,
                        'Client-Request-Id': clientRequestId,
                        'Message-Signature': b64_sig
                    }

                    response = requests.post(url, headers=headers, data=json_payload)
                    print("======", response, response.json())
                    response.raise_for_status()
                    data = response.json()

                    link = data['paymentLink'].get('paymentLinkUrl')
                    if not link:
                        raise UserError(_("Fiserv response missing payment link: %s") % response.text)

                    payment_link.link = link
                    account_move.fiserv_payment_link = link
                    account_move.paymentLinkId = data['paymentLink'].get('paymentLinkId')
                    account_move.message_post(
                        body=_("Fiserv Payment Link: <a href='%s' target='_blank'>Copy Link</a>") % link
                    )

                except requests.exceptions.RequestException as e:
                    raise UserError(_("Failed to generate Fiserv payment link: %s") % str(e))

            else:
                base_url = related_document.get_base_url()
                url = self._prepare_url(base_url, related_document)
                query_params = self._prepare_query_params(related_document)
                anchor = self._prepare_anchor()
                if '?' in url:
                    payment_link.link = f'{url}&{urls.url_encode(query_params)}{anchor}'
                else:
                    payment_link.link = f'{url}?{urls.url_encode(query_params)}{anchor}'
