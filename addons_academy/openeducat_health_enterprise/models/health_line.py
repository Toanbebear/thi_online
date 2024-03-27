# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, fields


class OpHealthLine(models.Model):
    _name = "op.health.line"
    _description = "Health Line"

    health_id = fields.Many2one('op.health', 'Health')
    date = fields.Date('Date', default=lambda self: fields.Date.today())
    name = fields.Text('Checkup Detail', required=True)
    recommendation = fields.Text('Checkup Recommendation')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
