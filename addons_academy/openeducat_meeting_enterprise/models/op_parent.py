# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, api


class OpParent(models.Model):
    _inherit = "op.parent"

    @api.model
    def create(self, vals):
        res = super(OpParent, self).create(vals)
        parent = self.env['res.partner.category'].search(
            [('name', '=', 'Parent')])
        partner_id = res.name
        partner_id.write({'category_id': [(6, 0, parent.ids)]}),
        return res
