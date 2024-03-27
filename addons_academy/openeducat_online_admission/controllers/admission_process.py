# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

import datetime

from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request


class AdmissionRegistration(http.Controller):

    @http.route(['/admissionregistration'], type='http',
                auth='public', website=True)
    def admission_registration(self, **post):
        register_ids = request.env['op.admission.register'].sudo().search(
            [('state', '=', 'application')])
        country_ids = request.env['res.country'].sudo().search([])
        post.update({
            'register_ids': register_ids,
            'countries': country_ids,
        })
        return request.render(
                "openeducat_online_admission.admission_registration", post)


class WebsiteSale(WebsiteSale):

    @http.route()
    def confirm_order(self, **post):
        val = post.copy()
        admission_id = False
        if val and val.get('register_id', False):
            register = request.env['op.admission.register'].sudo().search(
                [('id', '=', int(val['register_id']))])
            val.update({'register_id': register.id,
                        'course_id': register.course_id.id,
                        'application_date': datetime.datetime.today(),
                        'fees': register.product_id and
                        register.product_id.lst_price or 0.0,
                        'fees_term_id': register.course_id.fees_term_id.id,
                        'state': 'online'})
            admission_id = request.env['op.admission'].sudo().create(val)
            prod_id = False
            if register.course_id.reg_fees:
                prod_id = register.course_id.product_id.id
            else:
                return request.render(
                    "openeducat_online_admission.application_confirmed", post)
            add_qty = 1
            set_qty = 0
            request.website.sale_get_order(force_create=1)._cart_update(
                product_id=int(prod_id), add_qty=float(add_qty),
                set_qty=float(set_qty))
        order = request.website.sale_get_order()
        if not order:
            return request.redirect("/shop")
        if order and admission_id:
            admission_id.write({'order_id': order.id})
            if request.env.uid:
                user = request.env['res.users'].browse(request.env.uid)
                partner_id = user.partner_id.id
            else:
                partner_id = request.env['res.partner'].sudo().create(post).id
            order.wite({'partner_invoice_id': partner_id,
                        'partner_id': partner_id})
        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection
        order.onchange_partner_shipping_id()
        order.order_line._compute_tax_id()
        request.session['sale_last_order_id'] = order.id
        request.website.sale_get_order(update_pricelist=True)
        extra_step = request.env.ref('website_sale.extra_info_option')
        if extra_step.active:
            return request.redirect("/shop/extra_info")
        return request.redirect("/shop/payment")
