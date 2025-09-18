# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    child_partner_ids = fields.Many2many('res.partner', 'sale_res_partner_tailor_rel', 'order_id', 'partner_id', 'Related Customers', tracking=True)

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


