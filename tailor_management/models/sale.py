# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.tools import (
    create_index,
    float_is_zero,
    format_amount,
    format_date,
    is_html_empty,
    SQL,
)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    child_partner_ids = fields.Many2many('res.partner', 'sale_res_partner_tailor_rel', 'order_id', 'partner_id', 'Related Customers', tracking=True)

    def _get_invoiceable_lines(self, final=False):
        """Return the invoiceable lines for order `self`."""
        down_payment_line_ids = []
        invoiceable_line_ids = []
        pending_section = None
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        for line in self.order_line:
            if line.display_type == 'line_section':
                # Only invoice the section if one of its lines is invoiceable
                pending_section = line
                continue
            if line.display_type != 'line_note' and float_is_zero(line.qty_to_invoice, precision_digits=precision):
                continue
            if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final) or line.display_type == 'line_note':
                if line.is_downpayment:
                    # Keep down payment lines separately, to put them together
                    # at the end of the invoice, in a specific dedicated section.
                    down_payment_line_ids.append(line.id)
                    continue
                if pending_section:
                    invoiceable_line_ids.append(pending_section.id)
                    pending_section = None
                if line.product_id.is_main_product:
                    invoiceable_line_ids.append(line.id)
        return self.env['sale.order.line'].browse(invoiceable_line_ids + down_payment_line_ids)


    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['child_partner_ids'] = [(6, 0, self.child_partner_ids.ids)]
        return invoice_vals


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def _prepare_invoice_values(self, order, name, amount, so_line):
        invoice_vals = super(SaleAdvancePaymentInv, self)._prepare_invoice_values(order, name, amount, so_line)
        invoice_vals['child_partner_ids'] = [(6, 0, order.child_partner_ids.ids)]
        return invoice_vals


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    set_scheduled_date = fields.Boolean(compute='set_scheduled_date')

    @api.depends('sale_id.opportunity_id.expected_delivery')
    def set_scheduled_date(self):
        for rec in self:
            expected_delivery = rec.sale_id.opportunity_id.expected_delivery
            if expected_delivery:
                rec.set_scheduled_date = True
                rec.scheduled_date = expected_delivery

    @api.depends('move_ids.state', 'move_ids.date', 'move_type', 'sale_id')
    def _compute_scheduled_date(self):
        for picking in self:
            if picking.sale_id.opportunity_id.expected_delivery:
                picking.scheduled_date = picking.sale_id.opportunity_id.expected_delivery
            else:
                moves_dates = picking.move_ids.filtered(lambda move: move.state not in ('done', 'cancel')).mapped(
                    'date')
                if picking.move_type == 'direct':
                    picking.scheduled_date = min(moves_dates, default=picking.scheduled_date or fields.Datetime.now())
                else:
                    picking.scheduled_date = max(moves_dates, default=picking.scheduled_date or fields.Datetime.now())


