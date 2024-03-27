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
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request


class GamificationOpenEduCatLms(OpenEduCatLms):

    @http.route()
    def enroll_course(self, course, **kwargs):
        r = super(GamificationOpenEduCatLms, self).enroll_course(
            course, **kwargs)
        for challenge in course.challenge_ids:
            current_challenge_users = challenge.user_ids.ids
            if request.env.uid not in current_challenge_users:
                current_challenge_users.append(request.env.uid)
                challenge.sudo().user_ids = [(6, 0, current_challenge_users)]
            challenge.sudo().action_start()
        return r

    @http.route()
    def get_course_material(self, course, section=None, material=None,
                            result=None, next=None, **kwargs):
        r = super(GamificationOpenEduCatLms, self).get_course_material(
            course, section, material, result, next, **kwargs)
        for challenge in course.challenge_ids:
            request.env['gamification.goal'].sudo().search(
                [('challenge_id', '=', challenge.id),
                 ('user_id', '=', request.env.uid),
                 ('state', '!=', 'reached')]).sudo().update_goal()
            challenge.sudo()._check_challenge_reward()
        return r

    @http.route(['/my/badges'], type='http', auth='public', website=True)
    def my_lms_badges(self, **post):
        badge_ids = request.env['gamification.badge.user'].search(
            [('user_id', '=', request.env.uid)])
        data = {'user': request.env.user}
        data['badge_ids'] = [x.badge_id for x in badge_ids]
        return request.render("openeducat_lms_gamification.my_badges", data)


class CustomerPortal(CustomerPortal):

    @http.route()
    def home(self, **kw):
        """ Add sales documents to main account page """
        response = super(CustomerPortal, self).home(**kw)
        badge_count = request.env[
            'gamification.badge.user'].sudo().search_count(
            [('user_id', '=', request.env.uid)])
        response.qcontext.update({
            'badge_count': badge_count
        })
        return response
