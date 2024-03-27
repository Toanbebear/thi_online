# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, fields


class SuspendedStudent(models.Model):
    _name = "suspended.student"
    _description = "Suspended Student Details"

    student_id = fields.Many2one('op.student', 'Student Name')
    suspend_from_date = fields.Date("Suspend From Date")
    suspend_to_date = fields.Date("Suspend To Date")
    misbehaviour_category_id = fields.Many2one(
        'op.misbehaviour.category', 'Misbehaviour Category')
    discipline_id = fields.Many2one('op.discipline', string='Discipline Id')
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda self: self.env.user.company_id)
