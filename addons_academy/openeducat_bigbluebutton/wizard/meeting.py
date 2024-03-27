# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, api, fields, _
from odoo.exceptions import AccessError, ValidationError

from . import bbb_api as bbb


class BbbMeeting(models.TransientModel):
    _name = "bbb.meeting"
    _description = "BBb Meeting"

    name = fields.Char("Name / Subject")
    user_id = fields.Many2one('res.users', 'User',
                              default=lambda self: self._uid)
    apw = fields.Char("Attendee password")
    mpw = fields.Char("Moderator password")
    welcome_str = fields.Char("Welcome String", help="welcome message to be \
                              displayed when a user logs in to the meeting")
    session_id = fields.Many2one("op.session", 'Session')

    @api.model
    def default_get(self, fields):
        res = super(BbbMeeting, self).default_get(fields)
        context = dict(self.env.context)
        active_id = context.get('active_id', False)
        session = self.env['op.session'].browse(active_id)
        res.update({
            'session_id': active_id,
            'name': session.subject_id.name,
            'welcome_str': "Welcome to " + session.subject_id.name
        })
        return res

    def create_meeting(self):
        res_param = self.env['ir.config_parameter']
        for record in self:
            url = res_param.search([
                ('key', '=', 'bigbluebutton.url')])
            salt = res_param.search([
                ('key', '=', 'bigbluebutton.secret')])
            if not url or not salt:
                raise AccessError(
                    _('Please Configure BigBlueButton Credentials'))
            url = url.value
            salt = salt.value
            base_url = res_param.search([
                ('key', '=', 'web.base.url')])
            if not base_url:
                raise AccessError(
                    _('Please Configure URL in System Parameters'))
            base_url = base_url.value
            apw = record.apw
            mpw = record.mpw
            meeting = bbb.createMeeting(
                record.user_id.name, record.id, record.welcome_str, mpw,
                apw, salt, url, base_url)
            if meeting:
                record.session_id.write({
                    'meeting_name': meeting['meetingID'],
                    'apw': apw,
                    'mpw': mpw,
                    'salt': salt,
                    'url': url,
                    'online_meeting': True,
                })
                return True
            else:
                raise ValidationError("Unable to reach server")
