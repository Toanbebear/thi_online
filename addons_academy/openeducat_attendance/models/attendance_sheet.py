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


class OpAttendanceSheet(models.Model):
    _name = "op.attendance.sheet"
    _inherit = ["mail.thread"]
    _description = "Attendance Sheet"
    _order = "attendance_date desc"

    @api.depends('attendance_line.present')
    def _compute_total_present(self):
        for record in self:
            record.total_present = self.env['op.attendance.line'].search_count(
                [('present', '=', True), ('attendance_id', '=', record.id)])

    @api.depends('attendance_line.present')
    def _compute_total_absent(self):
        for record in self:
            record.total_absent = self.env['op.attendance.line'].search_count(
                [('present', '=', False), ('attendance_id', '=', record.id)])

    name = fields.Char('Name', required=True, size=32)
    register_id = fields.Many2one(
        'op.attendance.register', 'Register', required=True,
        track_visibility="onchange")
    course_id = fields.Many2one(
        'op.course', related='register_id.course_id', store=True,
        readonly=True)
    batch_id = fields.Many2one(
        'op.batch', 'Batch', related='register_id.batch_id', store=True,
        readonly=True)
    session_id = fields.Many2one('op.session', 'Session')
    attendance_date = fields.Date(
        'Date', required=True, default=lambda self: fields.Date.today(),
        track_visibility="onchange")
    attendance_line = fields.One2many(
        'op.attendance.line', 'attendance_id', 'Attendance Line')
    total_present = fields.Integer(
        'Total Present', compute='_compute_total_present',
        track_visibility="onchange")
    total_absent = fields.Integer(
        'Total Absent', compute='_compute_total_absent',
        track_visibility="onchange")
    faculty_id = fields.Many2one('op.faculty', 'Faculty')

    session_content = fields.Char('Session content', related='session_id.session_content.content')

    def update_student(self):
        exist_attendees = [line.student_id.id for line in self.attendance_line]
        for record in self.batch_id.student_course:
            if record.student_id.id not in exist_attendees and int(str(record.attendance).split('/')[0]) < record.batch_id.num_lessons:
                self.env['op.attendance.line'].create({'attendance_id': self.id,
                                                       'student_id': record.student_id.id,
                                                       'student_detail': record.id,
                                                       'present': True})

    _sql_constraints = [
        ('unique_register_sheet',
         'unique(session_id)',
         'Sheet must be unique per Session.'),
    ]


class OpSession(models.Model):
    _inherit = 'op.session'

    def open_attendance_sheet(self):
        return {
            'name': _('Attendance sheet'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'op.attendance.sheet',
            'res_id': self.env['op.attendance.sheet'].search([('session_id', '=', self.id)], limit=1).id
        }
