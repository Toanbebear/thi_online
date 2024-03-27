# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from datetime import datetime
from odoo import models, fields, api


class OpRouteLine(models.Model):
    _name = "op.route.line"
    _inherit = ["mail.thread"]
    _description = "Transportation Route Line"

    name = fields.Char('Name', size=64, readonly=True)
    route_id = fields.Many2one('op.route', 'Route', required=True)
    route_type = fields.Selection(
        [('pickup', 'Pickup'), ('drop', 'Drop')],
        string='Route Type', required=True)
    route_stop_ids = fields.One2many(
        'op.route.stop.line', 'route_line_id', string='Stops')
    route_passenger_ids = fields.One2many(
        'op.route.passenger', 'route_line_id', string='Passenger')
    route_date = fields.Date(
        'Date', required=True, default=lambda self: fields.Date.today())
    start_time = fields.Float(
        'Start Time', required=True, track_visibility='always')
    driver_id = fields.Many2one(
        'res.partner', related='route_id.vehicle_id.driver_id',
        required=True, string='Driver', track_visibility='always')
    state = fields.Selection(
        [('draft', 'Draft'), ('start', 'Start'), ('end', 'End')],
        string='State', default='draft')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)

    @api.onchange('route_id')
    def onchange_route_id(self):
        self.route_stop_ids = False
        self.route_passenger_ids = False

    def start_trip(self):
        for record in self:
            record.state = 'start'

    def end_trip(self):
        for record in self:
            record.state = 'end'

    @api.model
    def create(self, vals):
        route = self.env['op.route'].browse([vals['route_id']])
        x = self.env['ir.sequence'].next_by_code('op.route.line') or ''
        seq = ' (%s)' % x
        route_date = datetime.strptime(vals.get('route_date', False),
                                       '%Y-%m-%d').strftime('%d-%m-%Y')
        vals['name'] = route.name + ' ' + route_date + seq
        return super(OpRouteLine, self).create(vals)

    def create_route_stop_line(self):
        for route in self:
            route_stop_ids = [x.stop_id.id for x in route.route_stop_ids]
            psngr_ids = [p.partner_id.id for p in route.route_passenger_ids]
            route_stop_line = self.env['op.route.stop.line']
            route_passenger = self.env['op.route.passenger']
            for stop in route.route_id.stop_ids:
                if stop.id not in route_stop_ids:
                    route_stop_line.create({
                        'route_line_id': route.id, 'stop_id': stop.id})
                for passenger in stop.partner_ids:
                    if passenger.id not in psngr_ids:
                        route_passenger.create({
                            'route_line_id': route.id,
                            'partner_id': passenger.id,
                            'present': True,
                            'stop_id': stop.id
                        })
