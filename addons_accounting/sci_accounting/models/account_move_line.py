# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    balance = fields.Monetary('Số dư', compute="get_balance_line")

    @api.depends('debit','credit')
    def get_balance_line(self):
        for record in self:
            record.balance = record.debit - record.credit
