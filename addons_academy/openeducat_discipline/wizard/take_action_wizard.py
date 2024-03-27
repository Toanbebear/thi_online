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


class TakeAction(models.TransientModel):
    _name = "take.action"
    _description = "Take Action Based on Misbehaviour"

    fine = fields.Boolean('Fine')
    fine_amount = fields.Integer(' Fine Amount')
    suspend = fields.Boolean('Suspend')
    suspend_from_date = fields.Date("Suspend From Date")
    suspend_to_date = fields.Date("Suspend To Date")
    discipline_id = fields.Many2one('op.discipline',
                                    string='Discipline Record')
    action_remark = fields.Text("Remark")

    @api.constrains('suspend_from_date', 'suspend_to_date')
    def check_dates(self):
        for record in self:
            if record.suspend:
                suspend_from_date = \
                    fields.Date.from_string(record.suspend_from_date)
                suspend_to_date = \
                    fields.Date.from_string(record.suspend_to_date)
                if suspend_to_date < suspend_from_date:
                    raise ValidationError(
                        _("To Date cannot be set before From Date."))

    def take_action(self):
        for record in self:
            discipline = self.env['op.discipline']. \
                browse([self.env.context.get('active_id', False)])
            if record.fine and not record.suspend:
                record.get_fine_data(discipline)
            elif record.suspend and not record.fine:
                record.get_suspend_data(discipline)
            elif record.suspend and record.fine:
                record.get_fine_data(discipline)
                record.get_suspend_data(discipline)
            else:
                discipline.state = 'done'

    def get_suspend_data(self, discipline):
        suspend = self.env["suspended.student"].create({
            'student_id': discipline.student_id.id,
            'suspend_from_date': self.suspend_from_date,
            'suspend_to_date': self.suspend_to_date,
            'misbehaviour_category_id': discipline.misbehaviour_category_id.id,
            'discipline_id': discipline.id})
        self.ensure_one()
        template = \
            self.env.ref('openeducat_discipline.'
                         'email_suspension_from_school_template',
                         False)
        template.send_mail(suspend.id, force_send=True)
        discipline.state = 'suspended'

    def get_fine_data(self, discipline):
        accounts = self.env['account.account']
        invoice_account = accounts.search(
            [('user_type_id', '=',
              self.env.ref('account.data_account_type_receivable').id)],
            limit=1).id
        invoice_line_account = accounts.search(
            [('user_type_id', '=',
              self.env.ref('account.data_account_type_expenses').id)],
            limit=1).id

        invoice = self.env['account.invoice'].create({
            'partner_id': discipline.student_id.partner_id.id,
            'account_id': invoice_account,
            'type': 'out_invoice',
            'date_invoice': fields.date.today(),
        })
        df_product_1 = self.env.ref('openeducat_discipline.df_product_1')
        self.env['account.move.line'].create({
            'product_id': df_product_1.id,
            'name': df_product_1.name,
            # 'origin': discipline.student_id.application_number,
            'quantity': 1.0,
            'price_unit': self.fine_amount,
            'discount': 0.0,
            'uom_id': df_product_1.uom_id.id,
            'invoice_id': invoice.id,
            'account_id': invoice_line_account,
        })
        discipline.state = 'done'
