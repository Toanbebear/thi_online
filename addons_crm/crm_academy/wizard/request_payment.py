from odoo import api, fields, models
from datetime import date
from odoo.exceptions import UserError, AccessError, ValidationError, Warning


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


class RequestPayment(models.TransientModel):
    _name = 'request.payment'
    _description = 'Request Payment'

    name = fields.Char('Desc')
    booking_id = fields.Many2one('crm.lead', string='Booking')
    partner_id = fields.Many2one('res.partner', string='Partner')
    crm_line_ids = fields.Many2many('crm.line', 'request_payment_ref', 'crm_line_s', 'request_payment_s',
                                    string='Services', domain="[('crm_id','=',booking_id), ('stage', '!=', 'cancel')]")
    # company_ids = fields.Many2many('res.company', string='Company', compute='set_company_ids_request_payment',
    #                                store=True)
    company_id = fields.Many2one('res.company', string='Company')
    currency_id = fields.Many2one('res.currency', string='Currency', related='booking_id.price_list_id.currency_id', store=True)

    amount_total = fields.Monetary('Amount total', digits=(3, 0))
    payment_type = fields.Selection([('in_bound', 'In bound'), ('out_bound', 'Out bound')],
                                    string='Payment method', default='in_bound')
    debt_review_reason = fields.Text('Reason for debt')
    payment_amount = fields.Integer('Payment Amount', compute='compute_payment_amount')
    account_payment = fields.Many2one('account.payment')

    @api.depends('crm_line_ids.money_receive')
    def compute_payment_amount(self):
        self.payment_amount = 0
        for rec in self.crm_line_ids:
            if rec.money_receive:
                self.payment_amount += rec.money_receive

    @api.onchange('crm_line_ids')
    def onchange_name(self):
        if self.crm_line_ids:
            self.name = ''
            for course in self.crm_line_ids:
                self.name += course.course_id.name + ";"

    @api.depends('booking_id')
    def set_company_ids_request_payment(self):
        for rec in self:
            if rec.booking_id and rec.booking_id.company_id and rec.booking_id.company2_id:
                list = rec.booking_id.company2_id._origin.ids
                list.append(rec.booking_id.company_id.id)
                rec.company_ids = [(6, 0, list)]
            elif rec.booking_id and rec.booking_id.company_id:
                rec.company_ids = [(4, rec.booking_id.company_id.id)]

    # @api.depends('crm_line_ids')
    # def _get_total_amount(self):
    #     self.amount_total = 0
    #     if self.crm_line_ids:
    #         for rec in self.crm_line_ids:
    #             self.amount_total += rec.total

    # def create_payment_academy(self):
    #     if self.booking_id.crm_line_ids.course_id:
    #         # Tạo payment
    #         payment = self.env['account.payment'].sudo().create({
    #             'name': False,
    #             'payment_type': 'inbound',
    #             'crm_id': self.booking_id.id,
    #             'partner_id': self.partner_id.id,
    #             'company_id': self.booking_id.company_id.id,
    #             'currency_id': self.booking_id.currency_id.id,
    #             'amount': '0',
    #             'communication': self.name,
    #             'text_total': num2words_vnm(int(self.amount_total)) + " đồng",
    #             'partner_type': 'customer',
    #             'payment_date': date.today(),
    #             'communication': self.name,
    #             'payment_method_id': '1',
    #             'journal_id': self.env['account.journal'].search(
    #                 [('company_id', '=', self.booking_id.company_id.id), ('type', '=', 'cash')], limit=1).id,
    #         })
    #         payment.crm_line_ids = [(6, 0, self.crm_line_ids.ids)]

    def request_draft_payment(self):
        if self.booking_id.crm_line_ids.course_id:
            service_name = ''
            total_price = 0
            vals = []
            for record in self.booking_id.crm_line_ids:
                if record.paid < record.total:
                    service_name += record.course_id.name + ";"
                    # total_price += record.total - record.paid
                    vals.append(record.id)
            payment = self.env['account.payment'].sudo().create({
                'name': False,
                'payment_type': 'inbound',
                'crm_id': self.booking_id.id,
                'partner_id': self.partner_id.id,
                'company_id': self.company_id.id,
                'currency_id': self.booking_id.currency_id.id,
                'amount': self.amount_total,
                'communication': "Thu phí dịch vụ: " + service_name,
                'text_total': num2words_vnm(int(total_price)) + " đồng",
                'partner_type': 'customer',
                'payment_date': date.today(),
                'payment_method_id': '1',
                'journal_id': self.env['account.journal'].search(
                    [('company_id', '=', self.booking_id.company_id.id), ('type', '=', 'cash')], limit=1).id,
                'crm_line_ids': [(6, 0, vals)],
            })
            return payment.write({'state': 'draft'})
        else:
            raise ValidationError('You must select at least one service!')