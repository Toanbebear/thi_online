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

from odoo import models, fields, api


class OpAllStudentWizard(models.TransientModel):
    _name = "op.all.student"
    _description = "All Student Wizard"

    @api.model
    def _default_student(self):
        batch = self.env['op.batch'].browse(self._context.get('active_id'))
        return [(6, 0, [student.student_id.id for student in batch.student_course])]

    student_ids = fields.Many2many('op.student', string='Add Student(s)', domain=[], default=_default_student)

    def confirm_student(self):
        self.ensure_one()
        batch = self.env['op.batch'].browse(self._context.get('active_id'))
        attendance_sheet = self.env['op.attendance.sheet'].search([('batch_id', '=', self._context.get('active_id'))],
                                                                  limit=1)
        all_students = [student.student_id for student in batch.student_course]
        for student in all_students:
            student_course = self.env['op.student.course'].search([('student_id', '=', student.id),
                                                                   ('batch_id', '=', self._context.get('active_id'))])
            attendance_line = self.env['op.attendance.line'].search([('attendance_id', '=', attendance_sheet.id),
                                                                     ('student_id', '=', student.id)])
            if not attendance_line:
                attendance_line = self.env['op.attendance.line'].create({'student_id': student.id,
                                                                         'attendance_id': attendance_sheet.id})
            total_attendance = sum(
                line.sudo().attendance_id.session_id.lesson_count for line in attendance_line)
            student_course.attendance = str(total_attendance) + '/' + str(batch.num_lessons)
            if student not in self.student_ids:
                attendance_line.present = False
                student_course.status = 'not'
            else:
                attendance_line.present = True
            if total_attendance == batch.num_lessons:
                student_course.status = 'finish'

    # @api.multi
    # def confirm_student(self):
    #     for record in self:
    #         for sheet in self.env.context.get('active_ids', []):
    #             sheet_browse = self.env['op.attendance.sheet'].browse(sheet)
    #             absent_list = [
    #                 x.student_id for x in sheet_browse.attendance_line]
    #             all_student_search = self.env['op.student'].search(
    #                 [('course_detail_ids.course_id', '=',
    #                   sheet_browse.register_id.course_id.id),
    #                  ('course_detail_ids.batch_id', '=',
    #                   sheet_browse.register_id.batch_id.id)])
    #             all_student_search = list(
    #                 set(all_student_search) - set(absent_list))
    #             for student_data in all_student_search:
    #                 vals = {'student_id': student_data.id, 'present': True,
    #                         'attendance_id': sheet}
    #                 if student_data.id in record.student_ids.ids:
    #                     vals.update({'present': False})
    #                 self.env['op.attendance.line'].create(vals)
