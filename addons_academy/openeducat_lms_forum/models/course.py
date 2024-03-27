# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OpCourse(models.Model):
    _inherit = "op.course"

    forum_id = fields.Many2one('forum.forum', 'Forum')
    forum_post_ids = fields.One2many('forum.post', 'course_id',
                                     string='Blog Post')

    def action_create_forum(self):
        for record in self:
            if self.env.user.karma < 7:
                raise ValidationError(
                    _('It appears your email has not been verified to \
                    participate in forum, Verify it from forum menu on \
                    homepage.'))
            if not record.forum_id:
                record.forum_id = self.env['forum.forum'].sudo().create(
                    {'name': record.name})
        return True
