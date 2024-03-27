# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, api


class OpStudent(models.Model):
    _inherit = "op.student"

    @api.model
    def create(self, vals):
        res = super(OpStudent, self).create(vals)
        students = self.env['res.partner.category'].search(
            [('name', '=', 'Student')])
        partner_id = res.partner_id
        partner_id.write({'category_id': [(6, 0, students.ids)]}),
        return res
