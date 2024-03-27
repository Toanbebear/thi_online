# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import api, models


class Partner(models.Model):
    _inherit = "res.partner"

    def get_attendee_detail(self, meeting_id):
        """ Return a list of tuple (id, name, status)
        Used by web_calendar.js : Many2ManyAttendee
        """
        datas = []
        for partner in self:
            data = partner.name_get()[0]
            datas.append([data[0], data[1], False, partner.color])
        return datas
