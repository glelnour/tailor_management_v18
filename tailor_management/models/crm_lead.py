# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import UserError
from datetime import timedelta


class Lead(models.Model):
    _inherit = 'crm.lead'

    def _get_payment_count(self):
        for lead in self:
            lead.lead_payment_count = len(lead.payment_ids)

    lead_payment_count = fields.Integer(compute='_get_payment_count', store=False)
    payment_ids = fields.One2many('account.payment', 'lead_id', 'Payments')
    child_partner_ids = fields.Many2many('res.partner', 'crm_lead_res_partner_tailor_rel', 'lead_id', 'partner_id', 'Related Customers', tracking=True)
    product_id = fields.Many2one('product.product', string='Product', tracking=True)
    product_ids = fields.Many2many('product.product', string='Products')
    design_method_id = fields.Many2one('tailor.design.method', string='Design Method', tracking=True)
    pack_line_ids = fields.One2many('crm.product.pack.line', 'lead_id', string='Pack Lines')
    bust_cup_size = fields.Char(string='Bust Cup Size', tracking=True)
    neck = fields.Char(string='Neck', tracking=True)
    accross_front = fields.Char(string='Across Front', tracking=True)
    bust_fullest_part = fields.Char(string='Bust Fullest Part', tracking=True)
    under_bust = fields.Char(string='Under Bust', tracking=True)
    waist_cric = fields.Char(string='Waist Cric.', tracking=True)
    hp_cric = fields.Char(string='HP Cric. (Fullest Part)', tracking=True)
    thigh_cric = fields.Char(string='Thigh Cric. (Fullest Part)', tracking=True)
    upper_arm_cric = fields.Char(string='Upper Arm Cric. (Fullest Part)', tracking=True)
    elbow_cric = fields.Char(string='Elbow Cric.', tracking=True)
    wrist_cric = fields.Char(string='Wrist Cric.', tracking=True)
    shoulder_to_waist = fields.Char(string='Shoulder to Waist', tracking=True)
    shoulder_to_floor = fields.Char(string='Shoulder to Floor', tracking=True)
    shoulder_to_shoulder = fields.Char(string='Shoulder to Shoulder', tracking=True)
    back_neck_to_waist = fields.Char(string='Back Neck to Waist', tracking=True)
    across_back = fields.Char(string='Across Back', tracking=True)
    inner_arm_length = fields.Char(string='Inner Arm Length (Armhole to Wrist)', tracking=True)
    ankle = fields.Char(string='Ankle', tracking=True)
    total_length = fields.Char(string='Total Length', tracking=True)
    ind_comp = fields.Selection([('individual', 'Individual'),
                                 ('company', 'Company')], string='Individual / Company', default='individual')
    is_vip_customer = fields.Boolean('VIP Customer?')
    partner_id = fields.Many2one(
        'res.partner', string='Customer', check_company=True, index=True, tracking=10,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="Linked partner (optional). Usually created when converting the lead. You can find a partner by its Name, TIN, Email or Internal Reference.")
    expected_delivery = fields.Datetime(string='Expected Delivery Date')
    actual_delivery = fields.Datetime(string='Actual Delivery Date',compute='_compute_delivery_dates')
    prova_date = fields.Datetime(string="Prova Date")
    # First set of fields
    bust_cup_size_1 = fields.Char(string='Bust Cup Size', tracking=True)
    neck_1 = fields.Char(string='Neck', tracking=True)
    accross_front_1 = fields.Char(string='Across Front', tracking=True)
    bust_fullest_part_1 = fields.Char(string='Bust Fullest Part', tracking=True)
    under_bust_1 = fields.Char(string='Under Bust', tracking=True)
    waist_cric_1 = fields.Char(string='Waist Cric.', tracking=True)
    hp_cric_1 = fields.Char(string='HP Cric. (Fullest Part)', tracking=True)
    thigh_cric_1 = fields.Char(string='Thigh Cric. (Fullest Part)', tracking=True)
    upper_arm_cric_1 = fields.Char(string='Upper Arm Cric. (Fullest Part)', tracking=True)
    elbow_cric_1 = fields.Char(string='Elbow Cric.', tracking=True)
    wrist_cric_1 = fields.Char(string='Wrist Cric.', tracking=True)
    shoulder_to_waist_1 = fields.Char(string='Shoulder to Waist', tracking=True)
    shoulder_to_floor_1 = fields.Char(string='Shoulder to Floor', tracking=True)
    shoulder_to_shoulder_1 = fields.Char(string='Shoulder to Shoulder', tracking=True)
    back_neck_to_waist_1 = fields.Char(string='Back Neck to Waist', tracking=True)
    across_back_1 = fields.Char(string='Across Back', tracking=True)
    inner_arm_length_1 = fields.Char(string='Inner Arm Length (Armhole to Wrist)', tracking=True)
    ankle_1 = fields.Char(string='Ankle', tracking=True)
    total_length_1 = fields.Char(string='Total Length', tracking=True)

    # Second set of fields
    bust_cup_size_2 = fields.Char(string='Bust Cup Size', tracking=True)
    neck_2 = fields.Char(string='Neck', tracking=True)
    accross_front_2 = fields.Char(string='Across Front', tracking=True)
    bust_fullest_part_2 = fields.Char(string='Bust Fullest Part', tracking=True)
    under_bust_2 = fields.Char(string='Under Bust', tracking=True)
    waist_cric_2 = fields.Char(string='Waist Cric.', tracking=True)
    hp_cric_2 = fields.Char(string='HP Cric. (Fullest Part)', tracking=True)
    thigh_cric_2 = fields.Char(string='Thigh Cric. (Fullest Part)', tracking=True)
    upper_arm_cric_2 = fields.Char(string='Upper Arm Cric. (Fullest Part)', tracking=True)
    elbow_cric_2 = fields.Char(string='Elbow Cric.', tracking=True)
    wrist_cric_2 = fields.Char(string='Wrist Cric.', tracking=True)
    shoulder_to_waist_2 = fields.Char(string='Shoulder to Waist', tracking=True)
    shoulder_to_floor_2 = fields.Char(string='Shoulder to Floor', tracking=True)
    shoulder_to_shoulder_2 = fields.Char(string='Shoulder to Shoulder', tracking=True)
    back_neck_to_waist_2 = fields.Char(string='Back Neck to Waist', tracking=True)
    across_back_2 = fields.Char(string='Across Back', tracking=True)
    inner_arm_length_2 = fields.Char(string='Inner Arm Length (Armhole to Wrist)', tracking=True)
    ankle_2 = fields.Char(string='Ankle', tracking=True)
    total_length_2 = fields.Char(string='Total Length', tracking=True)
    total_customers = fields.Integer(compute='get_no_of_customers', store=True)
    invoice_id = fields.Many2one('account.move', string='Related Invoice')

    def create_invoice_wizard(self):
        return {
            'name': ("GL"),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'invoice.confirmation.wizard',
            'view_id': self.env.ref('tailor_management.view_invoice_confirmation_wizard').id,
            'target': 'new',
            'context': {
                'default_lead_id': self.id,
            },
        }

    @api.model
    def _cron_send_prova_reminders(self):
        """Send reminder 1 day before prova_date."""
        today = fields.Date.today()
        reminder_date = today + timedelta(days=1)

        leads = self.search([("prova_date", "=", reminder_date)])
        for lead in leads:
            # Example: send internal activity to the salesperson
            lead.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=lead.user_id.id or self.env.user.id,
                summary="Prova Reminder",
                note=f"Reminder: Prova scheduled on {lead.prova_date} for {lead.name}.",
            )

        @api.model
        def _cron_send_delivery_reminders(self):
            """Send reminder 1 day before delivery_date."""
            today = fields.Date.today()
            reminder_date = today + timedelta(days=1)

            leads = self.search([("expected_delivery", "=", reminder_date)])
            for lead in leads:
                if not lead.stage_id.is_won:
                    # Example: send internal activity to the salesperson
                    lead.activity_schedule(
                        'mail.mail_activity_data_todo',
                        user_id=lead.user_id.id or self.env.user.id,
                        summary="Expected Delivery Date Reminder",
                        note=f"Reminder: Expected Delivery Date scheduled on {lead.expected_delivery} for {lead.name}.",
                    )

    def advance_payment(self):
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.payment',
            'view_id': self.env.ref('account.view_account_payment_form').id,
            'target': 'current',
            'context': {
                'default_lead_id': self.id,
                'default_partner_id': self.partner_id.id
            },
        }


    @api.depends('child_partner_ids')
    def get_no_of_customers(self):
        for rec in self:
            rec.total_customers = len(rec.child_partner_ids)
            if rec.partner_id:
                rec.total_customers += 1

    @api.depends('order_ids')
    def _compute_delivery_dates(self):
        for rec in self:
            if rec.order_ids:
                # if rec.order_ids[0] and rec.order_ids[0].commitment_date:
                #     rec.expected_delivery = rec.order_ids[0].commitment_date
                # else:
                #     rec.expected_delivery = False
                if rec.order_ids[0] and rec.order_ids[0].picking_ids[0].date_done:
                    rec.actual_delivery = rec.order_ids[0].picking_ids[0].date_done
                else:
                    rec.actual_delivery = False
            else:
                # rec.expected_delivery = False
                rec.actual_delivery = False

    @api.onchange('is_vip_customer')
    def onchange_is_vip_customer(self):
        self.partner_id.is_vip_customer = self.is_vip_customer

    @api.onchange('partner_id')
    def add_measurements(self):
        self.is_vip_customer = self.partner_id.is_vip_customer
        self.bust_cup_size = self.partner_id.bust_cup_size
        self.neck = self.partner_id.neck
        self.accross_front = self.partner_id.accross_front
        self.bust_fullest_part = self.partner_id.bust_fullest_part
        self.under_bust = self.partner_id.under_bust
        self.waist_cric = self.partner_id.waist_cric
        self.hp_cric = self.partner_id.hp_cric
        self.thigh_cric = self.partner_id.thigh_cric
        self.upper_arm_cric = self.partner_id.upper_arm_cric
        self.elbow_cric = self.partner_id.elbow_cric
        self.wrist_cric = self.partner_id.wrist_cric
        self.shoulder_to_waist = self.partner_id.shoulder_to_waist
        self.shoulder_to_floor = self.partner_id.shoulder_to_floor
        self.shoulder_to_shoulder = self.partner_id.shoulder_to_shoulder
        self.back_neck_to_waist = self.partner_id.back_neck_to_waist
        self.across_back = self.partner_id.across_back
        self.inner_arm_length = self.partner_id.inner_arm_length
        self.ankle = self.partner_id.ankle
        self.total_length = self.partner_id.total_length

    @api.constrains('product_ids')
    def _check_limited_edition(self):
        for lead in self:
            products = lead.product_ids.filtered(lambda p: p.is_limited_edition)
            for product in products:
                if lead.search_count([('product_id', '=', product.id), ('id', '!=', lead.id)]) > product.allowed_editions:
                    raise UserError("Selected product is a limited edition.\nCan't create more orders for this.")

    def action_view_payments(self):
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_account_payments")
        action['context'] = {
            'default_partner_id': self.partner_id.id,
            'default_lead_id': self.id
        }
        action['domain'] = [('lead_id', '=', self.id)]
        return action

    @api.onchange('design_method_id')
    def _onchange_design_method(self):
        if self.design_method_id:
            return {'domain': {'stage_id': [('id', 'in', self.design_method_id.crm_stage_ids.ids)]}}
        else:
            return {'domain': {'stage_id': []}}

    @api.onchange('product_ids')
    def onchange_product_id(self):
        self.pack_line_ids = False
        pack_lines = []

        for product in self.product_ids.filtered(lambda p: p.pack_ok and p.pack_line_ids):
            pack_lines.append((0, 0, {
                'display_type': 'line_section',
                'section_description': product.name,
                'name': product.name,
                'quantity': 0.0
            }))
            for line in product.pack_line_ids:
                pack_lines.append((0, 0, {
                    'display_type': False,
                    'parent_product_id': product.id,
                    'product_id': line.product_id.id,
                    'quantity': line.quantity
                }))
        self.pack_line_ids = pack_lines

    def action_new_quotation(self):
        action = super(Lead, self).action_new_quotation()
        if not self.partner_id.is_vip_customer and not self.payment_ids:
            raise UserError("Please add some advance payment before creating a quotation.")

        order_lines = []
        for product in self.product_ids:
            order_lines.append((0, 0, {
                'display_type': False,
                'product_id': product.id,
                'name': product.name,
                'product_uom': product.uom_id.id,
                'price_unit': product.list_price,
                'product_uom_qty': 1.0}))
        for line in self.pack_line_ids.filtered(lambda l: l.product_id):
            order_lines.append((0, 0, {
                'display_type': False,
                'product_id': line.product_id.id,
                'name': line.product_id.name,
                'product_uom': line.product_id.uom_id.id,
                'price_unit': 0,
                'product_uom_qty': line.quantity
            }))
        action['context']['default_child_partner_ids'] = [(6, 0, self.child_partner_ids.ids)]
        action['context']['default_order_line'] = order_lines
        return action

class ProductPackLine(models.Model):
    _name = 'crm.product.pack.line'
    _description = 'Lead Product Pack Line'

    @api.depends('quantity', 'cost')
    def _compute_total_cost(self):
        for rec in self:
            if rec.cost and rec.quantity:
                rec.total_cost = rec.cost * rec.quantity
            else:
                rec.total_cost = 0.00

    @api.depends('product_id', 'section_description')
    def get_line_description(self):
        for line in self:
            if line.display_type == 'line_section':
                line.name = line.section_description
            else:
                line.name = line.product_id.name

    name = fields.Char('Description', compute='get_line_description', store=True)
    display_type = fields.Selection([('line_section', 'Section'), ('line_product', 'Product')], help="Technical field for UX purpose.")
    section_description = fields.Text('Section Description')
    parent_product_id = fields.Many2one('product.product', 'Parent Product')
    lead_id = fields.Many2one('crm.lead', string='Lead')
    quantity = fields.Float(string='Quantity', default=1.0, digits="Product UoS")
    product_id = fields.Many2one('product.product', 'Product', ondelete="cascade", index=True)
    uom_id = fields.Many2one('uom.uom', string="Unit of Measure", related='product_id.uom_id')
    list_price = fields.Float(string='Sale Price', related='product_id.list_price', readonly='True', store=True)
    cost = fields.Float(string="Cost", related='product_id.standard_price')
    total_cost = fields.Float(string="Total Cost", compute='_compute_total_cost')
