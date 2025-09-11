# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_limited_edition = fields.Boolean('Limited Edition')
    allowed_editions = fields.Integer('No. Of Pieces')
    is_main_product = fields.Boolean('Is Main Product')

