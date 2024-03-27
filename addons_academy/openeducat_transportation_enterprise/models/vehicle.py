# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OpVehicle(models.Model):
    _name = "op.vehicle"
    _inherits = {"fleet.vehicle": "vehicle_id"}
    _description = "Transportation Vehicle"

    capacity = fields.Integer('Capacity', required=True)
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle',
                                 required=True, ondelete="cascade")
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)

    @api.constrains('capacity')
    def check_capacity(self):
        for record in self:
            if record.capacity <= 0:
                raise ValidationError(_('Enter proper Capacity.'))
