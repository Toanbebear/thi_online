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


class SurveySurvey(models.Model):
    _name = "survey.survey"
    _inherit = "survey.survey"

    course_id = fields = fields.Many2one('op.course', 'Course')
