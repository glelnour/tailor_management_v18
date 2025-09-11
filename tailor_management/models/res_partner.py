# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    is_vip_customer = fields.Boolean('VIP Customer?', tracking=True)
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
    customer = fields.Boolean("Customer")
    vendor = fields.Boolean("Vendor")
    owner = fields.Boolean("Owner")

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        if name:
            args += ['|', '|', ('name', operator, name), ('mobile', operator, name),
                                 ('phone', operator, name)]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)
