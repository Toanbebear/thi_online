# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, api, fields

from . import bbb_api as bbb


class MeetingLink(models.TransientModel):
    _name = "meeting.link"
    _description = "Meeting Link"

    name = fields.Char("Meeting Link", readonly=True)

    @api.model
    def default_get(self, fields):
        res = super(MeetingLink, self).default_get(fields)
        user = self.env['res.users'].browse(self.env.uid)
        context = dict(self.env.context)
        active_id = context.get('active_id', False)
        session = self.env['op.session'].browse(active_id)
        join_url = bbb.joinURL(session.meeting_name, user.name, session.apw,
                               session.salt, session.url)
        res.update({'name': join_url})
        return res
