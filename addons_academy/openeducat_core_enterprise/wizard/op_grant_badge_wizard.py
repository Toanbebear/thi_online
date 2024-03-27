# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import fields, models, api


class op_grant_badge_wizard(models.TransientModel):
    _name = "op.badge.student.wizard"
    _description = "Badge Student Wizard"

    student_id = fields.Many2one("op.student", string='Student',
                                 required=True)
    badge_id = fields.Many2one(
        "op.gamification.badge", string='Badge', required=True)
    comment = fields.Text('Comment')

    def action_grant_badge(self):
        for wiz in self:
            self.env['op.badge.student'].create({
                'student_id': wiz.student_id.id,
                'sender_id': self.env.uid,
                'badge_id': wiz.badge_id.id,
                'comment': wiz.comment,
            })
        return True
