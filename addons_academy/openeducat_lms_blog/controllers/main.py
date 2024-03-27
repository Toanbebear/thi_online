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
from odoo.addons.openeducat_lms.controllers.main import OpenEduCatLms
from odoo.http import request


class OpenEduCatLmsForum(OpenEduCatLms):

    @http.route()
    def course(self, course, **kw):
        r = super(OpenEduCatLmsForum, self).course(course, **kw)
        blog_post_ids = request.env['blog.post'].search([
            ('blog_id', '=', course.blog_id.id)])
        r.qcontext.update({
            'blog_post_ids': blog_post_ids,
        })
        return r
