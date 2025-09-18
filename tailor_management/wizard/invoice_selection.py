# -*- coding: utf-8 -*-
from odoo import models, fields, _
from odoo.exceptions import UserError

class InvoiceConfirmationWizard(models.TransientModel):
    _name = "invoice.confirmation.wizard"
    _description = "Invoice Confirmation Wizard"

    type_invoice_selection = fields.Selection([
        ('without_link', 'Create Invoice'),
        ('with_link', 'Create Invoice with Payment Link'),
    ], string='Type')
    lead_id = fields.Many2one('crm.lead')

    def action_create_invoice(self):
        active_id = self.env.context.get('active_id')
        lead = self.env['crm.lead'].browse(active_id)
        lead_id = self.lead_id
        order_lines = []
        for product in lead_id.product_ids:
            order_lines.append((0, 0, {
                'display_type': False,
                'product_id': product.id,
                'name': product.name,
                'product_uom': product.uom_id.id,
                'price_unit': product.list_price,
                'product_uom_qty': 1.0}))
        for line in lead_id.pack_line_ids.filtered(lambda l: l.product_id):
            order_lines.append((0, 0, {
                'display_type': False,
                'product_id': line.product_id.id,
                'name': line.product_id.name,
                'product_uom': line.product_id.uom_id.id,
                'price_unit': 0,
                'product_uom_qty': line.quantity
            }))
        so = self.env['sale.order'].create({
            'partner_id': lead_id.partner_id.id,
            'opportunity_id': lead_id.id,
            'origin': lead_id.name,
            'order_line': order_lines,
        })
        so.action_confirm()
        generated_invoices = self.env['account.move']
        for order in so:
            wizard = self.env['sale.advance.payment.inv'].create({
                'advance_payment_method': 'delivered',
            })
            # private method that returns invoices
            invoices = wizard._create_invoices(order)
            generated_invoices |= invoices

        if not generated_invoices:
            raise UserError(_("No invoices were generated."))

        # Example: take the latest invoice from the set
        invoice = generated_invoices.sorted('id')[-1]

        # If you want payment link conditionally
        if self.type_invoice_selection == 'with_link':
            link_wizard = self.env['payment.link.wizard'].with_context(active_model="account.move",
                                                                       active_id=invoice.id).create({
                'res_model': 'account.move',
                'res_id': invoice.id,
            })
            link_wizard._compute_link()
        lead_id.invoice_id = invoice.id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
        }
