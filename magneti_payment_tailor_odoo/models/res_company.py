# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    fiserv_store_id = fields.Char("Fiserv Store ID")
    fiserv_shared_secret = fields.Char("Fiserv Shared Secret")
    fiserv_api_key = fields.Char("Fiserv API Key")
    # fiserv_api_sece