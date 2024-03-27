# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SCIAccountPayment(models.Model):
    _inherit = 'account.payment'

    def post(self):
        res = super(SCIAccountPayment, self).post()
        for rec in self.sudo():
            if rec.partner_type == 'customer' and rec.payment_type == 'outbound':
                partner_company = self.env['res.company'].search([('partner_id', '=', rec.partner_id.id)], limit=1)
                if partner_company:
                    journal = self.env['account.journal'].search([('type', '=', 'general'), ('company_id', '=', partner_company.id)], limit=1)
                    account = rec.company_id.partner_id.with_context(force_company=partner_company.id).property_account_payable_id
                    acc_move_vals = {'date': rec.payment_date,
                                     'ref': rec.name,
                                     'journal_id': journal.id,
                                     'line_ids': [(0, 0, {'account_id': account.id, 'partner_id': rec.company_id.partner_id.id, 'name': rec.communication, 'credit': rec.amount}),
                                                  (0, 0, {'account_id': account.id, 'debit': rec.amount})]}
                    self.env['account.move'].create(acc_move_vals)
        return res

