# -*- coding: utf-8 -*-

import datetime, pytz
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SessionContent(models.Model):
    _name = 'op.session.content'
    _description = 'Session Content'

    name = fields.Char('Session number', compute='_get_name', store=True)
    sequence = fields.Integer('Sequence', required=True)
    content = fields.Char('Session content', required=True)
    course_id = fields.Many2one('op.course', string='Course')
    lesson_count = fields.Integer('Lesson Count', default=4)

    @api.constrains('lesson_count')
    def check_lesson_count(self):
        for record in self:
            if record.lesson_count:
                if record.lesson_count < 0:
                    raise ValidationError('Lessons cannot be less than 0 ')

    @api.depends('sequence')
    def _get_name(self):
        for record in self:
            if record.sequence and record.course_id:
                record.name = 'Bài ' + str(record.sequence)

    @api.onchange('course_id')
    def onchange_course_id(self):
        if self.course_id and not self.sequence:
            self.sequence = self.env['op.session.content'].search_count([('course_id', '=', self.course_id.id)]) + 1

    _sql_constraints = [
        ('content_course_uniq', 'unique(content, course_id)', 'Content must be unique per course!'),
    ]


class OpCourse(models.Model):
    _inherit = 'op.course'

    session_contents = fields.One2many('op.session.content', 'course_id', string='Content')
    contents_onchange_len = fields.Integer('Contents length plus one', compute='_get_len_content')
    num_lessons = fields.Integer('Tổng số tiết', compute="num_session_contents", default=4)

    @api.depends('session_contents')
    def num_session_contents(self):
        for rec in self:
            rec.num_lessons = sum([content.lesson_count for content in rec.session_contents])

    @api.depends('session_contents')
    def _get_len_content(self):
        for record in self:
            record.contents_onchange_len = len(record.session_contents) + 1


class OpBatch(models.Model):
    _inherit = 'op.batch'

    one_shot_batch = fields.Boolean('One shot', compute='_get_one_shot')
    # num_lessons = fields.Integer('Number of lessons', compute='get_num_session_contents')
    timing_id = fields.Many2one('op.timing', string='Time')
    session_contents = fields.Many2many('op.session.content', string='Session content')
    contents_onchange_len = fields.Integer('Contents length plus one', compute='_get_len_content')

    @api.constrains('num_lessons', 'session_contents')
    def constrain_number_lesson(self):
        for record in self:
            total_lessons = sum([content.lesson_count for content in self.session_contents])
            if record.num_lessons < total_lessons:
                raise ValidationError(_('Tổng số tiết học không được nhỏ hơn tổng số tiết của mỗi buổi học'))

    @api.onchange('session_contents')
    def get_num_session_contents(self):
        self.num_lessons = sum([content.lesson_count for content in self.session_contents])

    @api.depends('session_contents')
    def _get_len_content(self):
        for record in self:
            record.contents_onchange_len = len(record.session_contents) + 1

    @api.onchange('course_id')
    def _onchange_course(self):
        if self.course_id:
            self.session_contents = self.course_id.session_contents

    @api.depends('course_id.session_contents')
    def _get_one_shot(self):
        for record in self:
            if len(record.course_id.session_contents) < 2:
                record.one_shot_batch = True
            else:
                record.one_shot_batch = False

    @api.model
    def create(self, vals):
        res = super(OpBatch, self).create(vals)
        if res.internal and res.one_shot_batch:
            hour = res.timing_id.hour
            if res.timing_id.am_pm == 'pm' and int(hour) != 12:
                hour = int(hour) + 12
            per_time = '%s:%s:00' % (hour, res.timing_id.minute)
            final_date = datetime.datetime.strptime(
                res.start_date.strftime('%Y-%m-%d ') +
                per_time, '%Y-%m-%d %H:%M:%S')
            local_tz = pytz.timezone(
                self.env.user.partner_id.tz or 'GMT')
            local_dt = local_tz.localize(final_date, is_dst=None)
            utc_dt = local_dt.astimezone(pytz.utc)
            utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
            curr_start_date = datetime.datetime.strptime(
                utc_dt, "%Y-%m-%d %H:%M:%S")
            curr_end_date = curr_start_date + datetime.timedelta(
                hours=res.timing_id.duration)
            session_vals = {
                'faculty_id': res.faculty_id.id,
                'tutor_fee': res.tutor_fee,
                'lesson_count': res.num_lessons,
                'course_id': res.course_id.id,
                'batch_id': res.id,
                'timing_id': res.timing_id.id,
                'classroom_id': res.classroom_id.id,
                'start_datetime':
                    curr_start_date.strftime("%Y-%m-%d %H:%M:%S"),
                'end_datetime':
                    curr_end_date.strftime("%Y-%m-%d %H:%M:%S"),
                # 'type': calendar.day_name[int(line.day)],
            }
            self.env['op.session'].create(session_vals)
        return res

    def write(self, vals):
        res = super(OpBatch, self).write(vals)
        for record in self:
            if record.internal and record.one_shot_batch:
                hour = record.timing_id.hour
                if record.timing_id.am_pm == 'pm' and int(hour) != 12:
                    hour = int(hour) + 12
                per_time = '%s:%s:00' % (hour, record.timing_id.minute)
                final_date = datetime.datetime.strptime(
                    record.start_date.strftime('%Y-%m-%d ') +
                    per_time, '%Y-%m-%d %H:%M:%S')
                local_tz = pytz.timezone(
                    self.env.user.partner_id.tz or 'GMT')
                local_dt = local_tz.localize(final_date, is_dst=None)
                utc_dt = local_dt.astimezone(pytz.utc)
                utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
                curr_start_date = datetime.datetime.strptime(
                    utc_dt, "%Y-%m-%d %H:%M:%S")
                curr_end_date = curr_start_date + datetime.timedelta(
                    hours=record.timing_id.duration)
                session_vals = {
                    'faculty_id': record.faculty_id.id,
                    'tutor_fee': record.tutor_fee,
                    'lesson_count': record.num_lessons,
                    'course_id': record.course_id.id,
                    'batch_id': record.id,
                    'timing_id': record.timing_id.id,
                    'classroom_id': record.classroom_id.id,
                    'start_datetime':
                        curr_start_date.strftime("%Y-%m-%d %H:%M:%S"),
                    'end_datetime':
                        curr_end_date.strftime("%Y-%m-%d %H:%M:%S"),
                    # 'type': calendar.day_name[int(line.day)],
                }
                exist_session = self.env['op.session'].search([('batch_id', '=', record.id)], limit=1)
                if not exist_session:
                    self.env['op.session'].create(session_vals)
                else:
                    exist_session.write(session_vals)
        return res