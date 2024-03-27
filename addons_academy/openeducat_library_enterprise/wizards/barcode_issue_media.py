# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BarcodeIssueMedia(models.TransientModel):
    """ Issue Media """
    _name = "barcode.issue.media"
    _description = "Barcode Issue Media Wizard"

    transaction_type = fields.Selection(
        [('issue', 'Issue'), ('return', 'Return')],
        string='Transaction Type',
        default='issue')
    media_unit_number = fields.Char('Media Unit Number')
    library_card_number = fields.Char('Library Card Number')

    def check_max_issue(self, student_id, library_card_id):
        media_movement_search = self.env["op.media.movement"].search(
            [('library_card_id', '=', library_card_id),
             ('student_id', '=', student_id),
             ('state', '=', 'issue')])
        if len(media_movement_search) < self.env["op.library.card"].browse(
                library_card_id).library_card_type_id.allow_media:
            return True
        else:
            return False

    def barcode_do_issue(self):
        library_card_obj = self.env['op.library.card']
        media_mov_obj = self.env['op.media.movement']
        media_unit = self.env['op.media.unit']
        for media in self:
            unit = media_unit.search(
                [('barcode', '=', media.media_unit_number)])
            if not unit:
                raise UserError(
                    _("Media Unit can not available : %s") %
                    media.media_unit_number)
            elif media.transaction_type == 'return':
                media_move_search = media_mov_obj.search(
                    [('media_unit_id', '=', unit.id), ('state', '=', 'issue')])
                if not media_move_search:
                    raise UserError(_("Can't return media : %s") %
                                    media.media_unit_number)
                media_move_search.return_media(fields.Date.today())
            else:
                card = library_card_obj.search(
                    [('number', '=', media.library_card_number)])
                faculty_id = card.type == 'faculty' and \
                    card.faculty_id.id or False
                student_id = card.type == 'student' \
                    and card.student_id.id or False
                if not card:
                    raise UserError(_("Card not available : %s") %
                                    media.library_card_number)
                elif media.check_max_issue(card.student_id.id, card.id):
                    if unit.state and \
                            unit.state == 'available':
                        media_movement_create = {
                            'media_id': unit.media_id.id,
                            'media_unit_id': unit.id,
                            'type': card.type,
                            'student_id': student_id,
                            'faculty_id': faculty_id,
                            'library_card_id': card.id,
                            'issued_date': fields.Date.today(),
                            'return_date': datetime.today() +
                            relativedelta(
                                days=card.library_card_type_id.duration),
                            'state': 'available',
                        }
                        movement = media_mov_obj.create(
                            media_movement_create)
                        movement.issue_media()
                    else:
                        raise UserError(_("Media Unit can not be issued \
                        because it's state is : %s") % unit.state)
                else:
                    allow_media = card.library_card_type_id.allow_media
                    raise UserError(
                        _('Maximum Number of media allowed for %s is : %s') %
                        (media.student_id.name, allow_media))
