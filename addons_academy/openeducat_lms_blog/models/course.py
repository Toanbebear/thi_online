# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, fields, api


class OpCourse(models.Model):
    _inherit = 'op.course'

    blog_id = fields.Many2one('blog.blog', 'Blog')
    blog_post_ids = fields.One2many('blog.post', 'course_id',
                                    string='Blog Post')

    def action_create_blog(self):
        for record in self:
            if not record.blog_id:
                record.blog_id = self.env['blog.blog'].sudo().create(
                    {'name': record.name})
        return True
