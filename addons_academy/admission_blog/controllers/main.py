# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import http
from odoo.addons.admission_web.controllers.main import AdmissionWeb
from odoo.http import request


class AdmissionForum(AdmissionWeb):

    @http.route()
    def course(self, course, **kw):
        r = super(AdmissionForum,self).course(course, **kw)
        blog_post_ids = request.env['blog.post'].search([
            ('blog_id', '=', course.blog_id.id)])
        r.qcontext.update({
            'blog_post_ids': blog_post_ids,
        })
        return r
