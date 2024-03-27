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


class OpFaculty(models.Model):
    _inherit = "op.faculty"

    @api.model
    def create(self, vals):
        res = super(OpFaculty, self).create(vals)
        faculty = self.env['res.partner.category'].search(
            [('name', '=', 'Faculty')], limit=1)
        partner_id = res.partner_id
        partner_id.write({'category_id': [(6, 0, faculty.ids)]}),
        return res
