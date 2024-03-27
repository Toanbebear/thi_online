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

from odoo import models, api, fields


class OpExamResult(models.TransientModel):
    _name = "op.exam.result"
    _description = "Held Exam"

    attendees_line = fields.Many2many(
        'op.exam.attendees', string='Attendees')

    @api.model
    def default_get(self, fields):
        res = super(OpExamResult, self).default_get(fields)
        active_id = self.env.context.get('active_id', False)
        exam = self.env['op.exam'].browse(active_id)
        student_ids = []
        for record in exam.attendees_line:
            student_ids.append(record.id)
        res.update({
            'attendees_line': [(6, 0, student_ids)],
        })
        return res

    def update_result(self):
        active_id = self.env.context.get('active_id', False)
        exam = self.env['op.exam'].browse(active_id)
        exam.state = 'result_updated'
        return True
