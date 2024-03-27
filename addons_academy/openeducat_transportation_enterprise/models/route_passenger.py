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


class OpRoutePssenger(models.Model):
    _name = "op.route.passenger"
    _description = "Transportation Route Passenger"

    stop_id = fields.Many2one('op.stop', 'Stop', required=True)
    route_line_id = fields.Many2one(
        'op.route.line', 'Route Line', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', 'Passenger', required=True)
    present = fields.Boolean('Present/Absent')
