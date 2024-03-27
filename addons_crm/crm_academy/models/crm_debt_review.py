from odoo import api, fields, models
from datetime import date


def num2words_vnm(num):
    under_20 = ['không', 'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín', 'mười', 'mười một',
                'mười hai', 'mười ba', 'mười bốn', 'mười lăm', 'mười sáu', 'mười bảy', 'mười tám', 'mười chín']
    tens = ['hai mươi', 'ba mươi', 'bốn mươi', 'năm mươi', 'sáu mươi', 'bảy mươi', 'tám mươi', 'chín mươi']
    above_100 = {100: 'trăm', 1000: 'nghìn', 1000000: 'triệu', 1000000000: 'tỉ'}

    if num < 20:
        return under_20[num]

    elif num < 100:
        under_20[1], under_20[5] = 'mốt', 'lăm'  # thay cho một, năm
        result = tens[num // 10 - 2]
        if num % 10 > 0:  # nếu num chia 10 có số dư > 0 mới thêm ' ' và số đơn vị
            result += ' ' + under_20[num % 10]
        return result

    else:
        unit = max([key for key in above_100.keys() if key <= num])
        result = num2words_vnm(num // unit) + ' ' + above_100[unit]
        if num % unit != 0:
            if num > 1000 and num % unit < unit / 10:
                result += ' không trăm'
            if 1 < num % unit < 10:
                result += ' linh'
            result += ' ' + num2words_vnm(num % unit)
    return result.capitalize()


class CrmDebtReviewInherit(models.Model):
    _inherit = 'crm.debt.review'

    amount_total = fields.Float('Amount total')
    payment_amount = fields.Float('Payment Amount')
    note = fields.Char('Note')
    type_brand = fields.Selection(related='booking_id.type_brand')
    crm_line_ids = fields.Many2many('crm.line', 'debt_to_crm_line', 'crm_line_to_debt', string='List product')

    def set_approve(self):
        res = super(CrmDebtReviewInherit, self).set_approve()
        if self.type_brand == 'academy' and self.crm_line_ids.course_id:
            service_name = []
            total_price = 0
            vals = []
            for record in self.crm_line_ids:
                service_name.append(record.course_id.name)
                vals.append(record.id)
            payment = self.env['account.payment'].sudo().create({
                'name': False,
                'payment_type': 'inbound',
                'crm_id': self.booking_id.id,
                'partner_id': self.booking_id.partner_id.id,
                'company_id': self.company_id.id,
                'currency_id': self.booking_id.currency_id.id,
                'amount': self.payment_amount,
                'communication': "Thu phí dịch vụ: " + '.'.join(service_name),
                'text_total': num2words_vnm(int(total_price)) + " đồng",
                'partner_type': 'customer',
                'payment_date': date.today(),
                'payment_method_id': '1',
                'journal_id': self.env['account.journal'].search(
                    [('company_id', '=', self.booking_id.company_id.id), ('type', '=', 'cash')], limit=1).id,
                'crm_line_ids': [(6, 0, vals)],
            })
            return payment.write({'state': 'draft'})
        return res