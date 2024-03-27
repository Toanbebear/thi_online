# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, fields, api, _


class AchievementCategory(models.Model):
    _name = "achievement.category"
    _description = "Achievement Category"

    name = fields.Char('Name', required=True)


class StudentAchieversLine(models.Model):
    _name = "student.achievers.line"
    _description = "Student Achievers Line"

    student_id = fields.Many2one('op.student', 'Student Name',
                                 required=True)
    remark = fields.Char('Remark', required=True)
    student_achievers_id = fields.Many2one('student.achievers',
                                           string='Class',
                                           ondelete="cascade")
    achievement_category_id = fields.Many2one('achievement.category',
                                              string="Achievement Category")
    achievers_date = fields.Date(string="Date", store=True)
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 default=lambda s: s.env.user.company_id)


class StudentAchievers(models.Model):
    _name = "student.achievers"
    _description = "Student Achievers Details"
    _rec_name = "course_id"

    @api.model
    def _get_faculty(self):
        return self.env['op.faculty'].search([
            ('emp_id.address_home_id', '=', self.env.user.partner_id.id)
        ], limit=1) or False

    course_id = fields.Many2one('op.course', 'Course', required=True)
    faculty_id = fields.Many2one(
        'op.faculty', 'Faculty',
        default=_get_faculty,
        required=True)
    achievers_date = fields.Date('Date', copy=False,
                                 default=fields.Date.today())
    achievement_category_id = fields.Many2one(
        'achievement.category', 'Achievement Category', required=True)
    student_achievers_line_ids = fields.One2many(
        'student.achievers.line', 'student_achievers_id', 'Select Student')
    state = fields.Selection(
        [('draft', 'Draft'), ('done', 'Done')],
        'State', default='draft', track_visibility='onchange')
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 default=lambda self: self.env.user.company_id)

    def send_students_list(self):
        self.ensure_one()
        template = self.env.ref(
            'openeducat_discipline.email_student_achievers_list_template',
            False)
        compose_form = self.env.ref(
            'mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model='student.achievers',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            force_email=True
        )
        self.state = 'done'
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }


class OpStudent(models.Model):
    _inherit = "op.student"

    achievement_line_ids = fields.One2many(
        'student.achievers.line', 'student_id', 'Achievement Details')
