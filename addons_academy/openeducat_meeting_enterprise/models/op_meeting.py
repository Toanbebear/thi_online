# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

import pytz
from datetime import timedelta
from odoo import api, fields, models


class OpMeeting(models.Model):
    _name = "op.meeting"
    _inherit = "mail.thread"
    _inherits = {"calendar.event": "meeting_id"}
    _description = "Meeting"

    meeting_id = fields.Many2one('calendar.event', 'Meeting',
                                 required=True, ondelete='cascade')
    start_datetime = fields.Datetime(
        'Start DateTime', compute='_compute_dates',
        inverse='_inverse_dates', store=True,
        states={'done': [('readonly', True)]},
        track_visibility='onchange')

    def _get_duration(self, start, stop):
        """ Get the duration value between the 2 given dates. """
        if start and stop:
            gap = fields.Datetime.from_string(
                stop) - fields.Datetime.from_string(start)
            if gap:
                duration = float(gap.days) * 24 + (float(gap.seconds) / 3600)
                return round(duration, 2)
        return 0.0

    @api.depends('allday', 'start', 'stop')
    def _compute_dates(self):
        for meeting in self:
            if meeting.allday:
                meeting.start_date = fields.Datetime.to_string(meeting.start)
                meeting.start_datetime = False
                meeting.stop_date = fields.Datetime.to_string(meeting.stop)
                meeting.stop_datetime = False
                meeting.duration = 0.0
            else:
                meeting.start_date = False
                meeting.start_datetime = meeting.start
                meeting.stop_date = False
                meeting.stop_datetime = meeting.stop
                meeting.duration = self._get_duration(
                    meeting.start, meeting.stop)

    def _inverse_dates(self):
        for meeting in self:
            if meeting.allday:
                tz = pytz.timezone(
                    self.env.user.tz) if self.env.user.tz else pytz.utc
                enddate = fields.Datetime.from_string(meeting.stop_date)
                enddate = tz.localize(enddate)
                enddate = enddate.replace(hour=18)
                enddate = enddate.astimezone(pytz.utc)
                meeting.stop = fields.Datetime.to_string(enddate)
                startdate = fields.Datetime.from_string(meeting.start_date)
                startdate = tz.localize(startdate)  # Add "+hh:mm" timezone
                startdate = startdate.replace(hour=8)  # Set 8 AM in localtime
                startdate = startdate.astimezone(pytz.utc)  # Convert to UTC
                meeting.start = fields.Datetime.to_string(startdate)
            else:
                meeting.start = meeting.start_datetime
                meeting.stop = meeting.stop_datetime

    @api.onchange('start_datetime', 'duration')
    def _onchange_duration(self):
        if self.start_datetime:
            start = fields.Datetime.from_string(self.start_datetime)
            self.start = self.start_datetime
            self.stop = fields.Datetime.to_string(
                start + timedelta(hours=self.duration))

    def unlink(self, can_be_deleted=True):
        events = self.search([('id', 'in', self.ids),
                              ('alarm_ids', '!=', False)])
        partner_ids = events.mapped('partner_ids').ids
        records_to_unlink = self.env['op.meeting']
        for meeting in self:
            records_to_unlink |= self.browse(int(meeting.id))
        if records_to_unlink:
            result = super(OpMeeting, records_to_unlink).unlink()
        self.env['calendar.alarm_manager'].notify_next_alarm(partner_ids)
        return result

    def action_sendmail(self):
        email = self.env.user.email
        if email:
            for meeting in self:
                meeting.attendee_ids._send_mail_to_attendees(
                    'calendar.calendar_template_meeting_invitation')
        return True
