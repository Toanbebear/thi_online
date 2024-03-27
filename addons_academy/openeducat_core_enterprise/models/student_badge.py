# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, fields


class OpBadgeStudent(models.Model):
    _name = "op.badge.student"
    _description = "Gamification Student badge"
    _order = "create_date desc"
    _rec_name = "badge_name"

    student_id = fields.Many2one(
        'op.student', string="Student", required=True,
        ondelete="cascade", index=True)
    sender_id = fields.Many2one(
        'res.users', string="Sender", help="The user who has send the badge")
    badge_id = fields.Many2one(
        'op.gamification.badge', string='Badge', required=True,
        ondelete="cascade", index=True)
    comment = fields.Text('Comment')
    badge_name = fields.Char(related='badge_id.name', string="Badge Name")
    create_date = fields.Datetime('Created', readonly=True)


class OpGamificationBadge(models.Model):
    _name = "op.gamification.badge"
    _inherit = "gamification.badge"
    _description = "Gamification Badge"

    name = fields.Char('Badge', required=True, translate=True)
    active = fields.Boolean('Active', default=True)
    description = fields.Text('Description', translate=True)
    image = fields.Binary(
        "Image", attachment=True, help="This field holds the image \
        used for the badge, limited to 256x256")
    rule_auth_badge_ids = fields.Many2many('gamification.badge', 'gamification_badge_rule_badge_rel', 'badge3_id', 'badge4_id', string='Required Badges')
