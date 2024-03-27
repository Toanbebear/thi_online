# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, fields


class OpStudent(models.Model):
    _inherit = "op.student"

    health_lines = fields.One2many('op.health', 'student_id',
                                   string='Health Detail')
