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
from datetime import date

class OpYear(models.Model):
    _name = "op.academic.year"
    _inherit = "mail.thread"
    _description = "Academic year"

    name = fields.Char('Code', size=16, required=True)
    start_date = fields.Date(
        'Start Date', required=True, default=date.today())
    end_date = fields.Date('End Date', required=True)
    student_ids = fields.One2many('op.student', 'academic_year', string='Students', readonly=True)
    batch_ids = fields.One2many('op.batch', 'academic_year', string='Batches', readonly=True)

    _sql_constraints = [
        ('unique_year_code',
         'unique(name)', 'Code should be unique per academic year!')]

    @api.constrains('start_date', 'end_date')
    def check_dates(self):
        for record in self:
            start_date = fields.Date.from_string(record.start_date)
            end_date = fields.Date.from_string(record.end_date)
            if start_date > end_date:
                raise ValidationError(
                    _("End Date cannot be set before Start Date."))

