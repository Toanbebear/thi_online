# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, api, fields

from ..wizard import bbb_api as bbb


class OpSession(models.Model):
    _inherit = "op.session"

    online_meeting = fields.Boolean("Online Meeting", copy=False)
    salt = fields.Char("Salt")
    url = fields.Char("URL")
    apw = fields.Char("Attendee Password")
    mpw = fields.Char("Moderator Password")
    meeting_name = fields.Char("Meeting ID")

    def get_meeting_url(self):
        user = self.env.user
        join_url = bbb.joinURL(
            self.meeting_name, user.name, self.apw, self.salt, self.url)
        bbb.getMeetingsURL(self.url, self.salt)
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'name': 'Redirection',
            'url': join_url
        }
