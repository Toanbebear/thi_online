# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, fields


class OpFacilityLine(models.Model):
    _inherit = "op.facility.line"

    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
