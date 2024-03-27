from odoo import fields, api, models
from odoo.exceptions import ValidationError


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


class RequestDeposit(models.Model):
    _name = 'crm.request.deposit'

    name = fields.Char('Lý do đặt cọc')
    lead_id = fields.Many2one('crm.lead', string='Lead/booking')
    partner_id = fields.Many2one('res.partner', string='Khách hàng')
    amount = fields.Monetary('Số tiền đặt cọc')
    currency_id = fields.Many2one('res.currency', string='Tiền tệ')
    brand_id = fields.Many2one('res.brand', string='Thương hiệu')
    company_id = fields.Many2one('res.company', string='Chi nhánh thụ hưởng')
    payment_id = fields.Many2one('account.payment', string='Payment tương ứng')
    payment_date = fields.Date('Ngày đặt cọc')
    note = fields.Text("Ghi chú")
    program_id = fields.Many2one('crm.discount.program', string='Chương trình giảm giá')

    # đặt cọc giữ khuyến mãi
    # đặt cọc thường

    def convert_payment(self):
        if not self.company_id:
            raise ValidationError('Bạn chưa chọn chi nhánh thụ hưởng!!!')
        else:
            journal_id = self.env['account.journal'].search(
                [('type', '=', 'cash'), ('company_id', '=', self.company_id.id)], limit=1)
            payment = self.env['account.payment'].create({
                'partner_id': self.partner_id.id,
                'company_id': self.company_id.id,
                'currency_id': self.company_id.currency_id.id,
                'amount': self.amount,
                'brand_id': self.brand_id.id,
                'communication': "Đặt cọc giữ chương trình",
                'text_total': num2words_vnm(int(self.amount)) + " đồng",
                'partner_type': 'customer',
                'payment_type': 'inbound',
                'payment_date': self.payment_date,  # ngày thanh toán
                'date_requested': self.payment_date,  # ngày yêu cầu
                'payment_method_id': self.env['account.payment.method'].with_user(1).search(
                    [('payment_type', '=', 'inbound')], limit=1).id,
                'journal_id': journal_id.id,
            })
            return {
                'name': 'Payment đặt cọc',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': payment.id,
                'view_id': self.env.ref('account.view_account_payment_form').id,
                'res_model': 'account.payment',
                'context': {},
            }
