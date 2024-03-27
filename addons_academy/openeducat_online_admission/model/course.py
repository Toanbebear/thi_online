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

    reg_fees = fields.Boolean('Registration Fees')
    product_id = fields.Many2one('product.product', 'Fees')
