# -*- coding: utf-8 -*-

from odoo import fields, models


class Payment(models.Model):
    _inherit = 'account.payment'

    lead_id = fields.Many2one('crm.lead', 'Related Lead', index=True)
