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

from odoo import models, fields


class OpCertificate(models.Model):
    _name = "op.certificate"
    _description = "Certificate for students"

    name = fields.Char('Number', required=True)
    code = fields.Char('Code in certificate openacademy')
    student_id = fields.Many2one('op.student', string="Student")
    batch_id = fields.Many2one('op.batch', string="Batch")
    course_id = fields.Many2one('op.course', string="Course", related='batch_id.course_id', store=True)
    date = fields.Date('Granted date')
    state = fields.Char('State')

    _sql_constraints = [
        ('unique_student_course',
         'unique(student_id, course_id)', 'Certificate for a student should be unique per course!')]
