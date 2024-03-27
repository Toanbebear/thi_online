# -*- coding: utf-8 -*-
###############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech-Receptives(<http://www.techreceptives.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OpExam(models.Model):
    _name = "op.exam"
    _inherit = "mail.thread"
    _description = "Exam"

    session_id = fields.Many2one('op.exam.session', 'Exam Session',
                                 domain=[('state', 'not in',
                                          ['cancel', 'done'])])
    course_id = fields.Many2one('op.course', 'Course')
    batch_id = fields.Many2one('op.batch', 'Batch')
    subject_id = fields.Many2one('op.subject', 'Subject')
    exam_code = fields.Char('Exam Code')
    attendees_line = fields.One2many(
        'op.result.line', 'exam_id', 'Student')
    start_time = fields.Datetime('Start Time', required=True, default=fields.datetime.now())
    end_time = fields.Datetime('End Time', required=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('schedule', 'Scheduled'), ('held', 'Held'),
         ('result_updated', 'Result Updated'),
         ('cancel', 'Cancelled'), ('done', 'Done')], 'State',
        readonly=True, default='draft', track_visibility='onchange')
    note = fields.Text('Note')
    responsible_id = fields.Many2many('op.faculty', string='Responsible')
    name = fields.Char('Exam', size=256, required=True)
    total_marks = fields.Integer('Total Marks', required=True, default=10)
    min_marks = fields.Integer('Passing Marks', required=True, default=5)
    exam_type = fields.Many2one('op.exam.type', 'Type')

    _sql_constraints = [
        ('unique_exam_code',
         'unique(exam_code)', 'Code should be unique per exam!')]

    @api.onchange('total_marks')
    def onchange_total_marks(self):
        if self.total_marks < 0:
            raise ValidationError(_(
                "Score must not be less than 0"))


    @api.onchange('batch_id', 'exam_type')
    def onchange_exam_type(self):
        if self.exam_type:
            number = self.env['op.exam'].search_count([('batch_id', '=', self.batch_id.id),
                                                       ('exam_type', '=', self.exam_type.id)]) + 1
            self.exam_code = '-'.join([self.batch_id.code, self.exam_type.code, str(number)])
            self.name = ' '.join([self.exam_type.name, 'số', str(number)])

    def update_student(self):
        exist_attendees = [line.student_id.id for line in self.attendees_line]
        for record in self.batch_id.student_course:
            if record.student_id.id not in exist_attendees:
                self.env['op.result.line'].create({'exam_id': self.id,
                                                   'student_id': record.student_id.id,
                                                   'marks': 0})

    @api.constrains('total_marks', 'min_marks')
    def _check_marks(self):
        if self.total_marks <= 0.0 or self.min_marks <= 0.0:
            raise ValidationError(_('Enter proper marks!'))
        if self.min_marks > self.total_marks:
            raise ValidationError(_(
                "Passing Marks can't be greater than Total Marks"))

    @api.constrains('start_time', 'end_time')
    def _check_date_time(self):
        start_time = fields.Datetime.from_string(self.start_time)
        end_time = fields.Datetime.from_string(self.end_time)
        if start_time > end_time:
            raise ValidationError(_('End Time cannot be set \
            before Start Time.'))

    @api.onchange('session_id')
    def _onchange_session_id(self):
        self.subject_id = False

    @api.onchange('start_time')
    def _onchange_start_time(self):
        self.end_time = self.start_time + timedelta(hours=1)

    @api.onchange('batch_id')
    def _onchange_batch_id(self):
        self.course_id = self.batch_id.course_id

    def act_result_updated(self):
        for record in self:
            record.state = 'result_updated'

    def act_done(self):
        for record in self:
            record.state = 'done'

    def act_draft(self):
        for record in self:
            record.state = 'draft'

    def act_cancel(self):
        for record in self:
            record.state = 'cancel'
