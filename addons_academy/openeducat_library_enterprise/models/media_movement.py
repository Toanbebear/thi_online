# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, exceptions, _


class OpMediaRenew(models.Model):
    _name = "op.media.renew"
    _description = "Library Media Renewal"

    movement_id = fields.Many2one("op.media.movement", 'Media Movement')
    renew_date = fields.Date("Renew Date")
    librarian_id = fields.Many2one("res.users", 'Librarian')


class OpMediaMovement(models.Model):
    _inherit = "op.media.movement"

    @api.depends('media_id', 'media_id.queue_ids')
    def _get_media_count(self):
        for media in self:
            if media.media_id and media.media_id.queue_ids:
                media.queue_count = len(media.media_id.queue_ids)
            else:
                media.queue_count = 0

    media_movement_id = fields.Many2one(
        'op.media.movement', 'Parent Media Movement')
    queue_count = fields.Float("Media Queue Count", compute="_get_media_count")
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
    renew_ids = fields.One2many("op.media.renew", 'movement_id',
                                'Renew Details')
    is_renew = fields.Boolean("Renew")

    def renew_media(self):
        self.ensure_one()
        self.actual_return_date = fields.Date.today()
        self.calculate_penalty()
        if self.penalty:
            raise exceptions.AccessError(
                _("Can't renew media \n you have penalty to pay"))
        date = relativedelta(
            days=self.library_card_id.library_card_type_id.duration)

        self.env['op.media.renew'].create({
            'librarian_id': self.env.uid,
            'movement_id': self.id,
            'renew_date': fields.Date.today(),
        })
        self.return_date = datetime.today() + date
        self.is_renew = True
        return True
