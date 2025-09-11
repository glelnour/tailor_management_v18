# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    child_partner_ids = fields.Many2many('res.partner', 'invoice_res_partner_tailor_rel', 'move_id', 'partner_id', 'Related Customers', tracking=True)

    def _get_measurements(self, opportunity):
        measurement_fields = [
            'bust_cup_size', 'neck', 'accross_front', 'bust_fullest_part', 'under_bust',
            'waist_cric', 'hp_cric', 'thigh_cric', 'upper_arm_cric', 'elbow_cric',
            'wrist_cric', 'shoulder_to_waist', 'shoulder_to_floor', 'shoulder_to_shoulder',
            'back_neck_to_waist', 'across_back', 'inner_arm_length', 'ankle', 'total_length'
        ]

        result = {}
        for field in measurement_fields:
            values = []
            for suffix in ['', '_1', '_2']:
                value = getattr(opportunity, f"{field}{suffix}", None)
                if value:
                    values.append(value)

            result[field] = ', '.join(values)
        return result
