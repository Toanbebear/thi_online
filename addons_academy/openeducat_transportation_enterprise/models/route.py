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


class OpRoute(models.Model):
    _name = "op.route"
    _description = "Transportation Route"

    name = fields.Char('Name', size=64, required=True)
    stop_ids = fields.One2many('op.stop', 'route_id', string='Stops')
    cost = fields.Float('Cost')
    vehicle_id = fields.Many2one('op.vehicle', 'Vehicle', required=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
