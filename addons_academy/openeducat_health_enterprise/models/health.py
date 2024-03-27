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


class OpHealth(models.Model):
    _name = "op.health"
    _rec_name = "student_id"
    _description = """Health Detail for Students and Faculties"""

    type = fields.Selection(
        [('student', 'Student'), ('faculty', 'Faculty')],
        'Type', default='student', required=True)
    student_id = fields.Many2one('op.student', 'Student')
    faculty_id = fields.Many2one('op.faculty', 'Faculty')
    height = fields.Float('Height(C.M.)', required=True)
    weight = fields.Float('Weight', required=True)
    physical_challenges = fields.Boolean('Physical Challenge?', default=False)
    physical_challenges_note = fields.Text('Physical Challenge')
    major_diseases = fields.Boolean('Major Diseases?', default=False)
    major_diseases_note = fields.Text('Major Diseases')
    eyeglasses = fields.Boolean('Eye Glasses?')
    eyeglasses_no = fields.Char('Eye Glasses', size=64)
    regular_checkup = fields.Boolean(
        'Any Regular Checkup Required?', default=False)
    health_line = fields.One2many(
        'op.health.line', 'health_id', 'Checkup Lines')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)

    @api.constrains('height', 'weight')
    def check_height_weight(self):
        for record in self:
            if record.height <= 0.0 or record.weight <= 0.0:
                raise ValidationError(_("Enter proper height and weight!"))
