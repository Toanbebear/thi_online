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
from datetime import date


class SCIFaculty(models.Model):
    _inherit = "op.faculty"

    session_ids = fields.One2many('op.session', 'faculty_id', 'Sessions')
    batch_line_ids = fields.One2many('op.batch.line', 'faculty_id', 'Sessions', compute='_get_batch_line')

    @api.depends('session_ids')
    def _get_batch_line(self):
        for record in self:
            batch_ids = []
            lines = self.env['op.batch.line']
            for session in record.session_ids:
                if session.batch_id not in batch_ids:
                    batch_ids.append(session.batch_id)
            for batch in batch_ids:
                batch_sessions = self.env['op.session'].search([('batch_id', '=', batch.id),
                                                                ('faculty_id', '=', record.id)])
                num_sessions = 0
                unpaid_sessions = 0
                tutor_fee = 0
                for session in batch_sessions:
                    if session.end_datetime < fields.Datetime.now():
                        num_sessions += session.lesson_count
                        tutor_fee += session.batch_id.course_id.tutor_fee * session.lesson_count
                        if not session.paid:
                            unpaid_sessions += session.lesson_count
                line = lines.search([('faculty_id', '=', record.id), ('batch_id', '=', batch.id)])
                if line:
                    line.write({'num_sessions': num_sessions,
                                'tutor_fee': tutor_fee,
                                'unpaid_sessions': unpaid_sessions})
                else:
                    lines.create({'faculty_id': record.id,
                                  'batch_id': batch.id,
                                  'tutor_fee': tutor_fee,
                                  'num_sessions': num_sessions,
                                  'unpaid_sessions': unpaid_sessions})
            record.batch_line_ids = lines.search([('faculty_id', '=', record.id)])


class SCIAdmissionLine(models.Model):
    _name = 'op.batch.line'

    faculty_id = fields.Many2one('op.faculty')
    batch_id = fields.Many2one('op.batch', string='Batches')
    batch_code = fields.Char('Batch code', related='batch_id.code', store=True)
    batch_status = fields.Selection([('ongoing', 'Ongoing'), ('closed', 'Closed')], string='Status', compute='_get_batch_status')
    batch_num_students = fields.Integer('Students', compute='_get_num_students', store=True)
    tutor_fee = fields.Float('Tutor fee')
    currency_id = fields.Many2one(
        'res.currency', 'Currency',
        default=lambda self: self.env.user.company_id.currency_id.id,
        required=True)
    num_sessions = fields.Integer('Lessons taught')
    unpaid_sessions = fields.Integer('Lessons unpaid')

    @api.depends('batch_id.student_course')
    def _get_num_students(self):
        for record in self:
            record.batch_num_students = len(record.batch_id.student_course)

    @api.depends('batch_id')
    def _get_batch_status(self):
        for record in self:
            if record.batch_id and record.batch_id.end_date:
                if record.batch_id.end_date >= date.today():
                    record.batch_status = 'ongoing'
                else:
                    record.batch_status = 'closed'
            else:
                record.batch_status = False
