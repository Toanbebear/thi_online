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
import datetime


class OpTiming(models.Model):
    _name = "op.timing"
    _description = "Period"
    _order = "sequence"

    name = fields.Char('Name', size=16, compute='_get_timing_name')
    hour = fields.Selection(
        [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),
         ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'),
         ('11', '11'), ('12', '12')], 'Start hours', required=True)
    minute = fields.Selection(
        [('00', '00'), ('15', '15'), ('30', '30'), ('45', '45')], 'Start minute',
        required=True)
    duration = fields.Float('Duration')
    am_pm = fields.Selection(
        [('am', 'AM'), ('pm', 'PM')], 'AM/PM', required=True)
    sequence = fields.Integer('Sequence')

    @api.depends('hour', 'minute', 'duration', 'am_pm')
    def _get_timing_name(self):
        for record in self:
            if record.hour and record.minute and record.duration and record.am_pm:
                start_hour = int(record.hour)
                if record.am_pm == 'pm' and int(record.hour) != 12:
                    start_hour += 12
                end_time = datetime.datetime(2000, 1, 1, start_hour, int(record.minute)) + datetime.timedelta(hours=record.duration)
                record.name = '%s:%s - %s' % (start_hour, record.minute, end_time.strftime('%H:%M'))
            else:
                record.name = '/'
