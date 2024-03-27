from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class InheritAccountPayment(models.Model):
    _inherit = 'account.payment'

    crm_line_ids = fields.Many2many('crm.line', string='List product')
    source = fields.Many2one('utm.source')

    @api.onchange('journal_id', 'crm_id', 'walkin', 'payment_method')
    def _get_lines_domain(self):
        if self.type_brand == 'academy':
            self.crm_line_ids = [(6, 0, self.env['crm.line'].search(
                [('crm_id', '=', self.crm_id.id), ('full_payment', '=', False)]).ids)]
        elif self.type_brand == 'hospital':
            self.crm_line_ids = [(6, 0, self.env['crm.line'].search(
                [('service_id', 'in', self.walkin.service.ids), ('crm_id', '=', self.walkin.booking_id.id)]).ids)]

    def post(self):
        res = super(InheritAccountPayment, self).post()
        if self.crm_id and self.crm_id.type_brand == 'academy':
            total = 0
            for rec in self.crm_line_ids:
                total += int(rec.money_receive)
            if int(self.amount) != total:
                raise ValidationError('Tiền nhận được cần được chia đủ vào các khóa học')
            else:
                for rec in self.crm_line_ids:
                    rec.paid += rec.money_receive
                    rec.money_receive = 0
                    rec.note = ' '
        return res

    # def create(self, vals_list):
    #     rec = super(InheritAccountPayment, self).create(vals_list)
    #     if self.crm_id and self.crm_id.type_brand == 'academy':
    #         for record in self.crm_line_ids:
    #             record.paid += record.money_receive
    #             # self.amount += rec.money_receive
    #             # rec.money_receive = 0
    #             record.note = ' '
    #     return rec

    # @api.constrains('crm_line_ids')
    # def check_amount(self):
    #     if self.type_brand == 'academy' and self.crm_line_ids:
    #         total = 0
    #         for rec in self.crm_line_ids:
    #             total += int(rec.money_receive)
    #         if int(self.amount) != total:
    #             raise ValidationError('Tiền nhận được cần được chia đủ vào các khóa học')