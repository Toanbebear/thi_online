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


class OpAdmission(models.Model):
    _inherit = "op.admission"

    state = fields.Selection([
        ('draft', 'Draft'), ('online', 'Online Admission'),
        ('submit', 'Submitted'), ('confirm', 'Confirmed'),
        ('admission', 'Admission Confirm'), ('reject', 'Rejected'),
        ('pending', 'Pending'), ('cancel', 'Cancelled'), ('done', 'Done')],
        'State', default='draft', track_visibility='onchange')
    order_id = fields.Many2one('sale.order', 'Registration Fees Ref')


class OpAdmissionRegister(models.Model):
    _inherit = 'op.admission.register'

    @api.onchange('course_id')
    def _onchange_course_id(self):
        if self.course_id:
            self.product_id = self.course_id.product_id
