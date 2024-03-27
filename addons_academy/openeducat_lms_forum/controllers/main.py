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
        post_ids = request.env['forum.post'].search([
            ('forum_id', '=', course.forum_id.id),
            ('parent_id', '=', False)])
        r.qcontext.update({
            'post_ids': post_ids,
        })
        return r
