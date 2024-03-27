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

import calendar
import datetime
import pytz
import time

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class GenerateSession(models.TransientModel):
    _name = "generate.time.table"
    _description = "Generate Sessions"
    _rec_name = "course_id"

    holidays = fields.Many2many('gen.time.table.holiday', string='Holidays')
    lesson_count = fields.Integer('Lesson count', default=1)
    tutor_fee = fields.Float('Tutor fee')
    currency_id = fields.Many2one(
        'res.currency', 'Currency',
        default=lambda self: self.env.user.company_id.currency_id.id,
        required=True)
    timing_id = fields.Many2one('op.timing', 'Timing')
    faculty_id = fields.Many2one('op.faculty', 'Faculty')
    classroom_id = fields.Many2one('op.classroom', 'Classroom')

    course_id = fields.Many2one('op.course', 'Course', required=True)
    batch_id = fields.Many2one('op.batch', 'Batch', required=True, domain=[('end_date', '>', fields.Date.today())])
    time_table_lines = fields.One2many(
        'gen.time.table.line', 'gen_time_table', 'Time Table Lines')
    time_table_lines_1 = fields.One2many(
        'gen.time.table.line', 'gen_time_table', 'Time Table Lines1',
        domain=[('day', '=', '0')])
    time_table_lines_2 = fields.One2many(
        'gen.time.table.line', 'gen_time_table', 'Time Table Lines2',
        domain=[('day', '=', '1')])
    time_table_lines_3 = fields.One2many(
        'gen.time.table.line', 'gen_time_table', 'Time Table Lines3',
        domain=[('day', '=', '2')])
    time_table_lines_4 = fields.One2many(
        'gen.time.table.line', 'gen_time_table', 'Time Table Lines4',
        domain=[('day', '=', '3')])
    time_table_lines_5 = fields.One2many(
        'gen.time.table.line', 'gen_time_table', 'Time Table Lines5',
        domain=[('day', '=', '4')])
    time_table_lines_6 = fields.One2many(
        'gen.time.table.line', 'gen_time_table', 'Time Table Lines6',
        domain=[('day', '=', '5')])
    time_table_lines_7 = fields.One2many(
        'gen.time.table.line', 'gen_time_table', 'Time Table Lines7',
        domain=[('day', '=', '6')])
    start_date = fields.Date(
        'Start Date', required=True, default=time.strftime('%Y-%m-01'))
    end_date = fields.Date('End Date')
    all_week = fields.Boolean('All week', help='Tue to Fri will be copied from Mon')

    @api.onchange('all_week', 'timing_id')
    def _onchange_all_week(self):
        if self.all_week and self.timing_id:
            for num in range(0, 5):
                self.time_table_lines = [(0, 0, {'day': str(num), 'timing_id': self.timing_id.id,
                                                 'faculty_id': self.batch_id.faculty_id.id,
                                                 'classroom_id': self.batch_id.classroom_id.id})]

    def cancel_session(self):
        self.ensure_one()
        current_session = self.env['op.session'].browse(self._context.get('active_id'))
        later_sessions = self.env['op.session'].search([('start_datetime', '>', current_session.start_datetime),
                                                        ('batch_id', '=', current_session.batch_id.id)],
                                                       order='start_datetime')
        if later_sessions and self.start_date < later_sessions[-1].date:
            raise ValidationError(_("Chosen date must be later than current last session's date."))
        duo_content_list = [current_session.session_content.id]
        for session in later_sessions:
            duo_content_list.append(session.session_content.id)
            session.session_content = duo_content_list[0]
            duo_content_list.remove(duo_content_list[0])

        hour = self.timing_id.hour
        if self.timing_id.am_pm == 'pm' and int(hour) != 12:
            hour = int(hour) + 12
        per_time = '%s:%s:00' % (hour, self.timing_id.minute)
        final_date = datetime.datetime.strptime(
            self.start_date.strftime('%Y-%m-%d ') +
            per_time, '%Y-%m-%d %H:%M:%S')
        local_tz = pytz.timezone(
            self.env.user.partner_id.tz or 'GMT')
        local_dt = local_tz.localize(final_date, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
        curr_start_date = datetime.datetime.strptime(
            utc_dt, "%Y-%m-%d %H:%M:%S")
        curr_end_date = curr_start_date + datetime.timedelta(
            hours=self.timing_id.duration)
        current_session.write({'start_datetime': curr_start_date,
                               'timing_id': self.timing_id.id,
                               'end_datetime': curr_end_date,
                               'session_content': duo_content_list[0]})
        current_session.batch_id.end_date = current_session.end_datetime.date()
        return {
            'name': _('Sessions'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,kanban,form',
            'res_model': 'op.session',
            'domain': [('batch_id', '=', self.batch_id.id)],
        }

    @api.onchange('batch_id')
    def _onchange_ad(self):
        if self.batch_id:
            self.tutor_fee = self.batch_id.tutor_fee
            self.start_date = self.batch_id.start_date
            self.end_date = self.batch_id.end_date
            self.faculty_id = self.batch_id.faculty_id
            self.classroom_id = self.batch_id.classroom_id

    # @api.constrains('start_date', 'end_date')
    # def check_dates(self):
    #     start_date = fields.Date.from_string(self.start_date)
    #     end_date = fields.Date.from_string(self.end_date)
    #     if start_date > end_date:
    #         raise ValidationError(_("End Date cannot be set before \
    #         Start Date."))

    @api.onchange('course_id')
    def onchange_course(self):
        if self.batch_id and self.course_id:
            if self.batch_id.course_id != self.course_id:
                self.batch_id = False

    def act_gen_time_table(self):
        for session in self:
            start_date = session.start_date
            # end_date = session.end_date
            # session_contents = self.env['op.session.content'].search([('course_id', '=', session.course_id.id)], order='sequence')
            session_contents = self.batch_id.mapped('session_contents').sorted('sequence')
            content_num = 0
            holidays = []
            for record in session.holidays:
                for i in range((record.end_date - record.start_date).days + 1):
                    holidays.append((record.start_date + datetime.timedelta(i)))
            # for n in range((end_date - start_date).days + 1):
            for n in range((len(session_contents) + 2) * 7):
                curr_date = start_date + datetime.timedelta(n)
                for line in session.time_table_lines:
                    if curr_date not in holidays and int(line.day) == curr_date.weekday() and content_num < len(
                            session_contents):
                        hour = line.timing_id.hour
                        if line.timing_id.am_pm == 'pm' and int(hour) != 12:
                            hour = int(hour) + 12
                        per_time = '%s:%s:00' % (hour, line.timing_id.minute)
                        final_date = datetime.datetime.strptime(
                            curr_date.strftime('%Y-%m-%d ') +
                            per_time, '%Y-%m-%d %H:%M:%S')
                        local_tz = pytz.timezone(
                            self.env.user.partner_id.tz or 'GMT')
                        local_dt = local_tz.localize(final_date, is_dst=None)
                        utc_dt = local_dt.astimezone(pytz.utc)
                        utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
                        curr_start_date = datetime.datetime.strptime(
                            utc_dt, "%Y-%m-%d %H:%M:%S")
                        curr_end_date = curr_start_date + datetime.timedelta(
                            hours=line.timing_id.duration)
                        session_vals = {
                            'faculty_id': line.faculty_id.id,
                            'subject_id': line.subject_id.id,
                            'tutor_fee': session.tutor_fee,
                            'lesson_count': session_contents[content_num].lesson_count,
                            'course_id': session.course_id.id,
                            'batch_id': session.batch_id.id,
                            'timing_id': line.timing_id.id,
                            'classroom_id': line.classroom_id.id,
                            'start_datetime':
                                curr_start_date.strftime("%Y-%m-%d %H:%M:%S"),
                            'end_datetime':
                                curr_end_date.strftime("%Y-%m-%d %H:%M:%S"),
                            'type': calendar.day_name[int(line.day)],
                        }
                        session_content_id = session_contents[content_num].id
                        exist_session = self.env['op.session'].search([('session_content', '=', session_content_id),
                                                                       ('batch_id', '=', session.batch_id.id)],
                                                                      limit=1)
                        if exist_session:
                            exist_session.write(session_vals)
                        else:
                            session_vals['session_content'] = session_content_id
                            self.env['op.session'].create(session_vals)
                        content_num += 1
                    elif content_num == len(session_contents):
                        break
            session_end_date = self.env['op.session'].search([('batch_id', '=', session.batch_id.id)],
                                                             order='id desc', limit=1)
            session.batch_id.end_date = session_end_date.end_datetime.date()
            session_start_date = self.env['op.session'].search([('batch_id', '=', session.batch_id.id)],
                                                               order='id asc', limit=1)
            session.batch_id.start_date = session_start_date.end_datetime.date()
            return {'type': 'ir.actions.act_window_close'}


class GenerateSessionLine(models.TransientModel):
    _name = 'gen.time.table.line'
    _description = 'Generate Time Table Lines'
    _rec_name = 'day'

    gen_time_table = fields.Many2one(
        'generate.time.table', 'Time Table', required=True)
    faculty_id = fields.Many2one('op.faculty', 'Faculty', required=True)
    subject_id = fields.Many2one('op.subject', 'Subject')
    timing_id = fields.Many2one('op.timing', 'Timing', required=True)
    classroom_id = fields.Many2one('op.classroom', 'Classroom')
    day = fields.Selection([
        ('0', calendar.day_name[0]),
        ('1', calendar.day_name[1]),
        ('2', calendar.day_name[2]),
        ('3', calendar.day_name[3]),
        ('4', calendar.day_name[4]),
        ('5', calendar.day_name[5]),
        ('6', calendar.day_name[6]),
    ], 'Day', required=True, copy=False)


class GenerateSessionHoliday(models.TransientModel):
    _name = 'gen.time.table.holiday'
    _description = 'Generate timetable holiday'

    name = fields.Char('name')
    start_date = fields.Date('Start from')
    end_date = fields.Date('End at')

    @api.onchange('start_date', 'end_date')
    def onchange_date(self):
        if self.start_date and not self.end_date:
            self.end_date = self.start_date
        elif self.start_date and self.end_date:
            start = str(fields.Date.from_string(self.start_date).strftime("%d/%m"))
            end = str(fields.Date.from_string(self.end_date).strftime("%d/%m"))
            self.name = (start + '-' + end, start)[start == end]

    @api.constrains('start_date', 'end_date')
    def check_dates(self):
        for record in self:
            start_date = fields.Date.from_string(record.start_date)
            end_date = fields.Date.from_string(record.end_date)
            if start_date > end_date:
                raise ValidationError(_("End Date cannot be set before \
                Start Date."))
