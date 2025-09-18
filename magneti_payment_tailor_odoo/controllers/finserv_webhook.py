# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class FinservWebhook(http.Controller):

    @http.route(['/fiserv/payment/success'], type='json', auth='public', csrf=False, methods=['POST'])
    def fiserv_payment_callback(self, **post):
        _logger.info("Fiserv Callback Received: %s", post)

        event = post[0] if isinstance(post, list) and post else {}

        order_id = event.get('merchantTransactionId')
        status = event.get('ipgTransactionStatus')
        transaction_id = event.get('ipgTransactionId')
        _logger.info("DATAAAAAAA", order_id, status, transaction_id)

        if not order_id:
            return {'error': 'Missing merchantTransactionId'}

        sale_order = request.env['sale.order'].sudo().search([
            ('name', '=', order_id)
        ], limit=1)
        _logger.info("SO: %s", sale_order)

        if not sale_order:
            return {'error': 'Sale Order not found for orderId: %s' % order_id}

        if status == 'APPROVED' and sale_order.state in ['draft', 'sent', 'approved']:
            sale_order.action_confirm()
            sale_order.message_post(
                body="✅ Order confirmed via Fiserv.<br/>💳 Transaction ID: <b>%s</b>" % transaction_id
            )
            return {'status': 'confirmed', 'order_name': sale_order.name}
        else:
            sale_order.message_post(
                body="❌ Fiserv payment failed or status not APPROVED.<br/>Status: %s<br/>Transaction ID: %s" % (
                    status, transaction_id
                )
            )
            return {'status': 'not confirmed', 'reason': status}

    @http.route(['/payment/fiserv/success'], type='http', auth="public", website=True)
    def fiserv_payment_success(self, **post):
        return request.render("magneti_payment_odoo.payment_success_template", {})

    @http.route(['/payment/fiserv/failure'], type='http', auth="public", website=True)
    def fiserv_payment_failure(self, **post):
        return request.render("magneti_payment_odoo.payment_failure_template", {})
