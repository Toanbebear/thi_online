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


class OpenEduCatLmsSale(OpenEduCatLms):

    @http.route()
    def enroll_course(self, course, **kwargs):
        if course.type == 'free':
            super(OpenEduCatLmsSale, self).enroll_course(course, **kwargs)
            return request.redirect('/my-courses')
        else:
            super(OpenEduCatLmsSale, self).enroll_course(course, **kwargs)
            enrollment = request.env['op.course.enrollment'].sudo().search([
                ('user_id', '=', request.env.user.id),
                ('course_id', '=', course.id)])
            enrollment.sudo().state = 'draft'
            order = request.website.sale_get_order(force_create=1)
            order._cart_update(product_id=course.product_id.id, add_qty=1)
            enrollment.sudo().order_id = order
            return request.redirect('/shop/cart')
