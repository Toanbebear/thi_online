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

import calendar, datetime, pytz
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

week_days = [(calendar.day_name[0], _(calendar.day_name[0])),
             (calendar.day_name[1], _(calendar.day_name[1])),
             (calendar.day_name[2], _(calendar.day_name[2])),
             (calendar.day_name[3], _(calendar.day_name[3])),
             (calendar.day_name[4], _(calendar.day_name[4])),
             (calendar.day_name[5], _(calendar.day_name[5])),
             (calendar.day_name[6], _(calendar.day_name[6]))]


class OpSession(models.Model):
    _name = "op.session"
    _inherit = ["mail.thread"]
    _description = "Sessions"

    name = fields.Char(compute='_compute_name', string='Name', store=True)
    timing_id = fields.Many2one(
        'op.timing', 'Timing', required=True, track_visibility="onchange")
    start_datetime = fields.Datetime(
        'Start Time', required=True,
        default=lambda self: fields.Datetime.now())
    end_datetime = fields.Datetime(
        'End Time', required=True)
    course_id = fields.Many2one(
        'op.course', 'Course', required=True)
    faculty_id = fields.Many2one(
        'op.faculty', 'Faculty', required=True)
    batch_id = fields.Many2one(
        'op.batch', 'Batch', required=True,)
    subject_id = fields.Many2one(
        'op.subject', 'Subject')
    classroom_id = fields.Many2one(
        'op.classroom', 'Classroom')
    color = fields.Integer('Color Index')
    type = fields.Char(compute='_compute_day', string='Day', store=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirmed'),
         ('done', 'Done'), ('cancel', 'Canceled')],
        'Status', default='draft')
    user_ids = fields.Many2many(
        'res.users', compute='_compute_batch_users',
        store=True, string='Users')

    session_content = fields.Many2one('op.session.content', string='Lesson')
    session_content_content = fields.Char('Content', related='session_content.content')
    lesson_count = fields.Integer('Lesson count', default=1)
    date = fields.Date('Date', compute="_compute_day", store=True)
    paid = fields.Boolean('Paid')
    tutor_fee = fields.Float('Tutor fee')
    currency_id = fields.Many2one(
        'res.currency', 'Currency',
        default=lambda self: self.env.user.company_id.currency_id.id,
        required=True)

    def open_cancel_session_wizard(self):
        self.ensure_one()
        return {
            'name': _('Cancel session'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'generate.time.table',
            'view_id': self.env.ref('openeducat_timetable.view_cancel_session_form').id,
            'target': 'new',
            'context': {'default_course_id': self.course_id.id,
                        'default_batch_id': self.batch_id.id},
        }

    @api.onchange('session_content')
    def _onchange_content(self):
        for record in self:
            record.lesson_count = record.session_content.lesson_count

    @api.onchange('batch_id')
    def _onchange_batch(self):
        for record in self:
            if record.batch_id:
                record.tutor_fee = record.batch_id.tutor_fee
                record.faculty_id = record.batch_id.faculty_id
                record.classroom_id = record.batch_id.classroom_id
                if not record.course_id:
                    record.course_id = record.batch_id.course_id
                if not self._context.get('session_name_date'):
                    exist_sessions = self.env['op.session'].search([('batch_id', '=', record.batch_id.id)])
                    exist_contents = exist_sessions.mapped('session_content.id')
                    batch_contents = record.batch_id.mapped('session_contents.id')
                    record.session_content = self.env['op.session.content'].search([('id', 'not in', exist_contents),
                                                                                    ('id', 'in', batch_contents),
                                                                           ('course_id', '=', record.course_id.id)],
                                                                                   order='sequence asc', limit=1)

    @api.depends('start_datetime')
    def _compute_day(self):
        for record in self:
            record.type = fields.Datetime.from_string(
                record.start_datetime).strftime("%A")
            record.date = fields.Datetime.from_string(
                record.start_datetime).strftime("%Y-%m-%d")

    @api.depends('session_content', 'start_datetime', 'batch_id', 'timing_id')
    def _compute_name(self):
        for session in self:
            if session.batch_id:
                if not session.session_content:
                    session.name = session.batch_id.name + '/' + \
                                   str(fields.Datetime.from_string(session.start_datetime).strftime("%d%m%y")) + '/' + \
                                   str(session.timing_id.name)
                elif session.start_datetime and session.timing_id and session.batch_id:
                    session.name = session.batch_id.name + '/' + \
                                   session.session_content.name + '/' + \
                                   str(fields.Datetime.from_string(session.start_datetime).strftime("%d%m%y")) + '/' + \
                                   str(session.timing_id.name)

    # For record rule on student and faculty dashboard
    @api.depends('batch_id', 'faculty_id', 'user_ids.child_ids')
    def _compute_batch_users(self):
        student_obj = self.env['op.student']
        users_obj = self.env['res.users']
        for session in self:
            student_ids = student_obj.search(
                [('course_detail_ids.batch_id', '=', session.batch_id.id)])
            user_list = [student_id.user_id.id for student_id
                         in student_ids if student_id.user_id]
            if session.faculty_id.user_id:
                user_list.append(session.faculty_id.user_id.id)
            user_ids = users_obj.search([('child_ids', 'in', user_list)])
            if user_ids:
                user_list.extend(user_ids.ids)
            session.user_ids = user_list

    def lecture_draft(self):
        for record in self:
            record.state = 'draft'

    def lecture_confirm(self):
        for record in self:
            record.state = 'confirm'

    def lecture_done(self):
        for record in self:
            record.state = 'done'

    def lecture_cancel(self):
        for record in self:
            record.state = 'cancel'

    @api.constrains('start_datetime', 'end_datetime')
    def _check_date_time(self):
        for record in self:
            if record.start_datetime > record.end_datetime:
                raise ValidationError(_(
                    'End Time cannot be set before Start Time.'))

    @api.model
    def create(self, values):
        res = super(OpSession, self).create(values)
        mfids = res.message_follower_ids
        partner_val = []
        partner_ids = []
        for val in mfids:
            partner_val.append(val.partner_id.id)
        if res.faculty_id and res.faculty_id.user_id:
            partner_ids.append(res.faculty_id.user_id.partner_id.id)
        if res.batch_id and res.course_id:
            course_val = self.env['op.student.course'].search([
                ('batch_id', '=', res.batch_id.id),
                ('course_id', '=', res.course_id.id)
            ])
            for val in course_val:
                if val.student_id.user_id:
                    partner_ids.append(val.student_id.user_id.partner_id.id)
        subtype_id = self.env['mail.message.subtype'].sudo().search([
            ('name', '=', 'Discussions')])
        if partner_ids and subtype_id:
            for partner in list(set(partner_ids)):
                if partner in partner_val:
                    continue
                val = self.env['mail.followers'].sudo().create({
                    'res_model': res._name,
                    'res_id': res.id,
                    'partner_id': partner,
                    'subtype_ids': [[6, 0, [subtype_id[0].id]]]
                })
        attendance_register = self.env['op.attendance.register'].search(
            [('course_id', '=', res.course_id.id), ('batch_id', '=', res.batch_id.id)])
        if attendance_register:
            attendance_register_id = attendance_register
        else:
            attendance_register_id = self.env['op.attendance.register'].create({
                'name': res.course_id.name + '/' + res.batch_id.name,
                'code': res.course_id.code + '/' + res.batch_id.code,
                'course_id': res.course_id.id,
                'batch_id': res.batch_id.id,
            })
        self.env['op.attendance.sheet'].create({
            'name': res.batch_id.name + '-' + str(res.date),
            'register_id': attendance_register_id.id,
            'session_id': res.id,
            'attendance_date': res.date,
        })
        return res

    @api.onchange('course_id')
    def onchange_course(self):
        if not self._context.get('default_batch_id'):
            self.batch_id = False
            self.faculty_id = False
            self.session_content = False
            self.lesson_count = 1
            self.classroom_id = False

    @api.onchange('session_content')
    def onchange_content(self):
        self.lesson_count = self.session_content.lesson_count

    @api.onchange('timing_id', 'start_datetime')
    def onchange_timing(self):
        if self.timing_id:
            hour = self.timing_id.hour
            if self.timing_id.am_pm == 'pm' and int(hour) != 12:
                hour = int(hour) + 12
            per_time = '%s:%s:00' % (hour, self.timing_id.minute)
            final_date = datetime.datetime.strptime(
                self.start_datetime.strftime('%Y-%m-%d ') +
                per_time, '%Y-%m-%d %H:%M:%S')
            local_tz = pytz.timezone(
                self.env.user.partner_id.tz or 'GMT')
            local_dt = local_tz.localize(final_date, is_dst=None)
            utc_dt = local_dt.astimezone(pytz.utc)
            utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
            self.start_datetime = datetime.datetime.strptime(
                utc_dt, "%Y-%m-%d %H:%M:%S")
            self.end_datetime = self.start_datetime + datetime.timedelta(
                hours=self.timing_id.duration)

    def notify_user(self):
        for session in self:
            template = self.env.ref(
                'openeducat_timetable.session_details_changes',
                raise_if_not_found=False)
            template.send_mail(session.id)

    def get_emails(self, follower_ids):
        email_ids = ''
        for user in follower_ids:
            if email_ids:
                email_ids = email_ids + ',' + str(user.sudo().partner_id.email)
            else:
                email_ids = str(user.sudo().partner_id.email)
        return email_ids

    def get_subject(self):
        return 'lecture of ' + self.faculty_id.name + \
               ' for ' + self.session_content.name + ' is ' + self.state

    def write(self, vals):
        data = super(OpSession,
                     self.with_context(check_move_validity=False)).write(vals)
        for session in self:
            if session.state not in ('draft', 'done'):
                session.notify_user()
            attendance_register = self.env['op.attendance.register'].search(
                [('course_id', '=', session.course_id.id), ('batch_id', '=', session.batch_id.id)])
            if attendance_register:
                attendance_register_id = attendance_register
            else:
                attendance_register_id = self.env['op.attendance.register'].create({
                    'name': session.course_id.name + '/' + session.batch_id.name,
                    'code': session.course_id.code + '/' + session.batch_id.code,
                    'course_id': session.course_id.id,
                    'batch_id': session.batch_id.id,
                })
            attendance_sheet = self.env['op.attendance.sheet'].search([('session_id', '=', session.id)])
            attendance_sheet.write({
                'name': session.batch_id.name + '-' + str(session.date),
                'register_id': attendance_register_id.id,
                'attendance_date': session.date,
            })
        return data

    def unlink(self):
        for record in self:
            session_ids = self.env['op.attendance.sheet'].search([('session_id', '=', record.id)])
            for session in session_ids:
                session.unlink()
            attendance_register_ids = self.env['op.attendance.register'].search([])
            for attendance_register in attendance_register_ids:
                if self.env['op.attendance.sheet'].search_count([('register_id', '=', attendance_register.id)]) == 0:
                    attendance_register.unlink()
        return super(OpSession, self).unlink()

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Sessions'),
            'template': '/openeducat_timetable/static/xls/op_session.xls'
        }]

    def name_get(self):
        if self._context.get('session_name_date'):
            return [(session.id, session.start_datetime) for session in self]
        else:
            return [(session.id, session.name) for session in self]
