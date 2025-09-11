# -*- coding: utf-8 -*-

from odoo import fields, models, api


class TailorDesignMethod(models.Model):
    _name = 'tailor.design.method'
    _description = 'Tailor Design Method'

    name = fields.Char('Design Type Name')
    crm_stage_ids = fields.Many2many('crm.stage', string='Stages')
