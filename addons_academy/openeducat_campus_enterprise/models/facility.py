# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, fields, api


class OpCampusFacility(models.Model):
    _name = "op.campus.facility"
    _description = "Campus Facility"

    name = fields.Char('Name', size=64, required=True)
    capacity = fields.Integer('Capacity', default="1")
    facility_type_id = fields.Many2one('op.facility.type', 'Facility Type',
                                       required=True)
    parent_id = fields.Many2one('op.campus.facility', 'Parent Facility',
                                ondelete='cascade')
    child_ids = fields.One2many('op.campus.facility', 'parent_id',
                                string='Child Facility')
    facility_allocation_lines = fields.One2many(
        'op.facility.allocation', 'facility_id', 'Allocations')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)

    def name_get(self):
        def get_names(cat):
            res = []
            while cat:
                res.append(cat.name)
                cat = cat.parent_id
            return res

        return [(cat.id, " / ".join(reversed(get_names(cat)))) for cat in self]
