# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, fields


class OpCourse(models.Model):
    _inherit = "op.course"

    type = fields.Selection([('free', 'Free'), ('paid', 'Paid')],
                            'Type', default='free')
    price = fields.Float('Price')
    product_id = fields.Many2one('product.product', 'Product',
                                 track_visibility='onchange')

    def action_confirm(self):
        self.ensure_one()
        if self.type == 'paid' and self.price and not self.product_id:
            product = self.env['product.product'].create(
                {'name': self.name,
                 'type': 'service',
                 'lst_price': self.price})
            self.product_id = product
        elif self.type == 'paid' and self.price and self.product_id:
            self.product_id.lst_price = self.price
        return super(OpCourse, self).action_confirm()
