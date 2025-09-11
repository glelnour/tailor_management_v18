# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2022-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Naveen K (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

"""Module Containing CRM lead and CheckList History Models"""
from datetime import datetime
from dateutil import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class LeadCheckList(models.Model):
    _inherit = "crm.lead"


    check_list_ids = fields.Many2many('stage.check.list',
                                      domain="['&',"
                                             " ('stage_id', '=', stage_id),"
                                             "'|',('s_team_id','=',team_id),"
                                             "('s_team_id', '=', False)]",
                                      string="Checklist", tracking=True)
    check_stage_ids = fields.One2many(related="stage_id.stage_check_list_lines")
    check_list_history = fields.One2many('crm.lead.check.history', 'lead_id',
                                         string="History")

    @api.depends('check_list_ids', 'check_list_history')
    def checklist_progress(self):
        """Method for Computing CheckList progress value based on selected
        checklist items """
        for rec in self:
            check_list = rec.check_list_history
            done_check_list = rec.check_list_history.filtered(lambda line: line.done == True)
            if rec.check_list_history:
                rec.checklist_progress = len(done_check_list) * 100 / len(check_list)
            else:
                rec.checklist_progress = 0
            deadline_checklist = rec.check_list_history.filtered(lambda line: line.done == False and line.deadline_date and line.deadline_date < datetime.now())
            if deadline_checklist:
                rec.is_deadline_record = True
            else:
                rec.is_deadline_record = False

            # for line in rec.check_list_history:
            #     if line.deadline_date and line.deadline_date < datetime.now() and line.done == False:
            #         channel = self.env['mail.channel'].channel_get(
            #             [line.user_id.partner_id.id])
            #         channel_obj = self.env['mail.channel'].browse(channel["id"])
            #         channel_obj.message_post(
            #             body=_(
            #                 "You have check list to complete %s.",
            #                 line.check_item.check_task),
            #             message_type='notification',
            #             subtype_xmlid='mail.mt_comment',
            #         )


            # total_len = rec.env['stage.check.list']. \
            #     search_count(['&', ('stage_id', '=', rec.stage_id.id), '|',
            #                   ('s_team_id', '=', rec.team_id.id),
            #                   ('s_team_id', '=', False)])
            # if total_len != 0:
            #     check_list_len = len(rec.check_list_ids.filtered(
            #         lambda r: r.s_team_id == rec.team_id or not r.s_team_id))
            #     rec.checklist_progress = (check_list_len * 100) / total_len
            # else:
            #     rec.checklist_progress = 0

    checklist_progress = fields.Float(compute=checklist_progress,
                                      string='Progress',
                                      default=0.0)
    is_deadline_record = fields.Boolean(string='Is there any deadline records')

    def write(self, vals_set):
        """Super the write method for data validation.Here we check
        Progression and regression of stages and based on checklist
        completion stage progression can be blocked from here """
        if 'stage_id' in vals_set.keys():
            new_stage_id = self.env['crm.stage'].browse([vals_set['stage_id']])
            if new_stage_id \
                    and self.stage_id.sequence < new_stage_id.sequence \
                    and not self.stage_id.pre_checking \
                    and self.stage_id.stage_check_list_lines \
                    and int(self.checklist_progress) != 100 \
                    and not self.env.user. \
                    has_group('crm_check_approve_limiter.'
                              'crm_check_approve_manager'):
                raise ValidationError("You cannot move this case forward until "
                                      "all the check list items are done for "
                                      "this "
                                      " stage.")
            self.check_list_ids = False
            for item in self.stage_id.stage_check_list_lines:
                if item.stage_recover:
                    history = self.check_list_history.search([(
                        'check_item', '=', item.id)], order='id desc',
                        limit=1) or False
                    if history and history.list_action == 'complete' \
                            and item not in self.check_list_ids:
                        self.check_list_ids += item
        if 'check_list_ids' in vals_set.keys():
            group_check = self.env.user. \
                has_group('crm_check_approve_limiter.'
                          'crm_check_approve_manager')
            user_groups = self.env.user.groups_id
            new_ids = self.env['stage.check.list']. \
                search([('id', 'in', vals_set['check_list_ids'][-1][-1])])
            old_ids = self.check_list_ids
            check_item = (old_ids - new_ids)
            check_item2 = (new_ids - old_ids)
            for ch_lst in check_item2:
                if ch_lst.approve_groups and not ch_lst. \
                        approve_groups.filtered(lambda f: f in user_groups) \
                        and not group_check:
                    grp_string_t = '\n'.join(map(str, ch_lst.approve_groups.
                                                 mapped('full_name')))
                    raise ValidationError(f'Only the below specified group'
                                          f' members can complete this task'
                                          f' : {grp_string_t}')
            for ch_lst in check_item:
                if ch_lst.approve_groups and not ch_lst. \
                        approve_groups.filtered(lambda f: f in user_groups) \
                        and not group_check:
                    grp_string_t = '\n'.join(map(str, ch_lst.approve_groups.
                                                 mapped('full_name')))
                    raise ValidationError(f'Only the below specified group'
                                          f' members can undo this task'
                                          f' : {grp_string_t}')
            # if 'stage_id' not in vals_set.keys() and check_item:
            #     for c_item in check_item:
            #         vals = {
            #             'lead_id': self.id,
            #             'check_item': c_item.id,
            #             'list_action': 'not_complete',
            #             'change_date': datetime.now(),
            #             'user_id': self.env.user.id,
            #             'stage_id': self.stage_id.id
            #         }
            #         self.env['crm.lead.check.history'].sudo().create(vals)
            # elif 'stage_id' not in vals_set.keys() and check_item2:
            #     for c_item in check_item2:
            #         vals = {
            #             'lead_id': self.id,
            #             'check_item': c_item.id,
            #             'list_action': 'complete',
            #             'change_date': datetime.now(),
            #             'user_id': self.env.user.id,
            #             'stage_id': self.stage_id.id
            #         }
            #         self.env['crm.lead.check.history'].sudo().create(vals)
        res = super().write(vals_set)
        return res

    @api.onchange('stage_id')
    def _onchange_state_id(self):
        old_stage_id = self._origin.stage_id
        if old_stage_id.sequence < self.stage_id.sequence \
                and not old_stage_id.pre_checking \
                and old_stage_id.stage_check_list_lines \
                and int(self.checklist_progress) != 100 :
                # and not self.env.user. \
                # has_group('crm_check_approve_limiter.'
                #           'crm_check_approve_manager')):
            raise ValidationError("You cannot move this case forward until "
                                  "all the check list items are done for this"
                                  " stage.")
        if old_stage_id.sequence > self.stage_id.sequence and self.stage_id.disable_regress:
                # and not self.env.user. \
                # has_group('crm_check_approve_limiter.'
                #           'crm_check_approve_manager')):
            raise ValidationError("Regression to the selected stage is "
                                  "blocked. "
                                  "Please contact Administrators for "
                                  "required permission")
        self.check_list_ids = False
        for item in self.stage_id.stage_check_list_lines:
            if item.stage_recover:
                history = self.check_list_history.search([(
                    'check_item', '=', item.id)], order='id desc',
                    limit=1) or False
                if history and history.list_action == 'complete' \
                        and item not in self.check_list_ids:
                    self.check_list_ids += item
        # To add all checklist
        for check_list in self.stage_id.stage_check_list_lines:
            self.check_list_history.sudo().create({
                'lead_id': self._origin.id,
                'check_item': check_list.id,
                'list_action': 'not_complete',
                'change_date': datetime.now(),
                'user_id': self.env.user.id,
                'stage_id': self.stage_id.id
            })


class StageCheckHistory(models.Model):
    _name = "crm.lead.check.history"
    _rec_name = "check_item"

    check_item = fields.Many2one('stage.check.list', string="Check Item", required=True)
    list_action = fields.Selection([
        ('complete', 'Complete'), ('not_complete', 'Not Complete')],
        string="Action", compute='_compute_list_action')
    user_id = fields.Many2one('res.users', string="User")
    change_date = fields.Datetime(string="Date")
    completed_date = fields.Datetime(string="Completed Date")
    deadline_date = fields.Datetime(string="Deadline")
    link = fields.Char(string="Link", help='To add link')
    stage_id = fields.Many2one('crm.stage', string="Stage")
    lead_id = fields.Many2one('crm.lead', string="Lead")
    partner_id = fields.Many2one('res.partner', related="lead_id.partner_id", string="Customer")
    done = fields.Boolean(string='Done')
    is_admin = fields.Boolean(string='Is admin', compute='_compute_is_admin')
    is_crm_manager = fields.Boolean(string='Is CRM Manager', compute='_compute_is_crm_manager')
    is_reminder_send = fields.Boolean(string='Is Reminder Send')
    deadline_days = fields.Integer(string="Deadline Days", compute='_compute_deadline_days')
    deadline_days_show = fields.Integer(string="Deadline Days", compute='_compute_deadline_days_show')

    def action_done(self):
        self.done = True


    def _compute_deadline_days(self):
        """To check user is admin or not"""
        for rec in self:
            if rec.deadline_date and datetime.now() > rec.deadline_date and rec.done == False:
                deadline_days = relativedelta.relativedelta(datetime.now(), rec.deadline_date)
                rec.deadline_days = deadline_days.days

            else:
                rec.deadline_days = 0

    def _compute_deadline_days_show(self):
        """To check user is admin or not"""
        for rec in self:
            if rec.deadline_date and datetime.now() > rec.deadline_date:
                deadline_days_show = relativedelta.relativedelta(datetime.now(), rec.deadline_date)
                rec.deadline_days_show = deadline_days_show.days

            else:
                rec.deadline_days_show = 0

    def _compute_is_crm_manager(self):
        """To check user is admin or not"""
        for rec in self:
            if self.env.user.has_group('crm_check_approve_limiter.crm_check_approve_manager'):
                rec.is_crm_manager = True
            else:
                rec.is_crm_manager = False

    @api.depends('done')
    def _compute_list_action(self):
        """To make action based on done field value"""
        for rec in self:
            if rec.done == True:
                rec.completed_date = datetime.now()
                rec.list_action = 'complete'
            else:
                rec.list_action = 'not_complete'

    def _compute_is_admin(self):
        """To check user is admin or not"""
        for rec in self:
            if self.env.user.has_group('sales_team.group_sale_manager'):
                rec.is_admin = True
            else:
                rec.is_admin = False


    def _check_checklist(self):
        """"To send notification to assigness after deadline"""
        check_list_ids = self.env['crm.lead.check.history'].search([('deadline_date', '<', datetime.now()), ('done', '=', False)])
        for line in check_list_ids:
            if not line.is_reminder_send:
                channel = self.env['mail.channel'].channel_get(
                    [line.user_id.partner_id.id])
                channel_obj = self.env['mail.channel'].browse(channel["id"])
                channel_obj.message_post(
                    body=_(
                        "You have check list to complete %s. <a href='/web#id=%s&view_type=form&model=crm.lead'>To view the checklist</a>") % (
                         line.check_item.check_task, line.lead_id.id),
                    message_type='notification',
                    subtype_xmlid='mail.mt_comment',
                )
                template = self.env.ref(
                    'crm_check_approve_limiter.check_list_mail_template').id
                email_values = {
                    'email_to': line.user_id.partner_id.email,
                    'email_from': self.env.company.email,
                }
                self.env['mail.template'].browse(template).send_mail(line.id, email_values=email_values,
                                                                     force_send=True)
            line.is_reminder_send = True

