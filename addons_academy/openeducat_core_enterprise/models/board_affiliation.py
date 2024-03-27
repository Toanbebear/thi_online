# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, fields


class OpResCompany(models.Model):
    _inherit = "res.company"

    affiliation_ids = fields.One2many('op.board.affiliation', 'company_id',
                                      'Affiliation Board')


class OpBoardAffiliation(models.Model):
    _name = "op.board.affiliation"
    _description = "Board Affiliation"

    name = fields.Char('Board Name')
    code = fields.Char('Code')
    note = fields.Text('Description')
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.user.company_id)
