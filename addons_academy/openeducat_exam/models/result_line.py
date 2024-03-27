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

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OpResultLine(models.Model):
    _name = "op.result.line"
    _rec_name = "marks"
    _description = "Result Line"

    marksheet_line_id = fields.Many2one(
        'op.marksheet.line', 'Marksheet Line', ondelete='cascade')
    exam_id = fields.Many2one('op.exam', 'Exam', required=True)
    evaluation_type = fields.Selection(
        related='exam_id.session_id.evaluation_type', store=True)
    marks = fields.Integer('Marks', required=True, group_operator='avg')
    grade = fields.Char('Grade', readonly=True, compute='_compute_grade')
    student_id = fields.Many2one('op.student', 'Student', required=True)
    user_id = fields.Many2one('res.users', 'User', related='student_id.emp_id.user_id', store=True)
    status = fields.Selection([('pass', 'Pass'), ('fail', 'Fail')], 'Status',
                              compute='_compute_status', store=True)

    student_course_id = fields.Many2one('op.student.course', 'Student course', compute='_get_student_course',
                                        store=True)
    retest_date = fields.Date('Retest date')
    batch_id = fields.Many2one('op.batch', 'Batch', related='exam_id.batch_id', store=True)
    exam_type = fields.Many2one('op.exam.type', 'Exam type', related='exam_id.exam_type', store=True)

    @api.depends('exam_id.course_id', 'exam_id.batch_id', 'student_id')
    def _get_student_course(self):
        for record in self:
            student_course = self.env['op.student.course'].search([('course_id', '=', record.exam_id.course_id.id),
                                                                   ('batch_id', '=', record.exam_id.batch_id.id),
                                                                   ('student_id', '=', record.student_id.id)], limit=1)
            record.student_course_id = student_course

    @api.constrains('marks', 'exam_id.total_marks')
    def _check_marks(self):
        for record in self:
            if record.marks < 0.0 or record.marks > record.exam_id.total_marks:
                raise ValidationError(_("Enter proper Marks or Percentage!"))

    @api.depends('marks')
    def _compute_grade(self):
        for record in self:
            if record.evaluation_type == 'grade':
                grades = record.marksheet_line_id.marksheet_reg_id. \
                    result_template_id.grade_ids
                for grade in grades:
                    if grade.min_per <= record.marks and grade.max_per > record.marks:
                        record.grade = grade.result
            else:
                record.grade = False

    @api.depends('marks')
    def _compute_status(self):
        for record in self:
            record.status = 'pass'
            if record.marks < record.exam_id.min_marks:
                record.status = 'fail'
