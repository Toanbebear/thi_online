# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, fields


class OpFaculty(models.Model):
    _inherit = "op.faculty"

    health_faculty_lines = fields.One2many('op.health', 'faculty_id',
                                           string='Health Detail')
