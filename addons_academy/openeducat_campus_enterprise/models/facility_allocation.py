# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OpFacilityAllocation(models.Model):
    _name = 'op.facility.allocation'
    _inherit = ['mail.thread']
    _rec_name = 'partner_id'
    _description = "Facility Allocation"

    partner_id = fields.Many2one(
        'res.partner', 'Person', required=True, track_visibility='onchange')
    facility_id = fields.Many2one('op.campus.facility', 'Facility',
                                  required=True, track_visibility='onchange')
    from_date = fields.Datetime('From Date', default=fields.Datetime.now(),
                                track_visibility='onchange')
    to_date = fields.Datetime('To Date', track_visibility='onchange')
    product_id = fields.Many2one(
        'product.product', 'Product', track_visibility='onchange')
    invoice_id = fields.Many2one(
        'account.move', 'Invoice', track_visibility='onchange')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)

    @api.model
    def create(self, vals):
        facility = self.env['op.campus.facility'].browse(
            [vals.get('facility_id', False)])
        from_date = str(vals.get('from_date', False))
        to_date = str(vals.get('to_date', False))
        if facility:
            count = self.env['op.facility.allocation'].search_count(
                ['&', ('facility_id', '=', facility.id), '|', '&',
                 ('from_date', '<=', from_date), ('to_date', '>=', from_date),
                 '&', ('from_date', '<=', to_date),
                 ('to_date', '>=', to_date)])
            if count >= facility.capacity:
                raise ValidationError(
                    _('Facility is not available in that Dates.'))
        return super(OpFacilityAllocation, self).create(vals)
