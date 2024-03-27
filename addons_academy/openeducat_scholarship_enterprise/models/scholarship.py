# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, fields, api


class OpScholarship(models.Model):
    _name = "op.scholarship"
    _inherit = "mail.thread"
    _description = "Scholarship"

    name = fields.Char('Name', size=64, required=True)
    student_id = fields.Many2one('op.student', 'Student', required=True)
    type_id = fields.Many2one('op.scholarship.type', 'Type', required=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirm'),
         ('reject', 'Reject')], 'State', default='draft', readonly=True,
        track_visibility='onchange')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)

    def act_confirm(self):
        for record in self:
            record.state = 'confirm'

    def act_reject(self):
        for record in self:
            record.state = 'reject'
