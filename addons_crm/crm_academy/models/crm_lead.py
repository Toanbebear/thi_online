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


class InheritCRM(models.Model):
    _inherit = 'crm.lead'

    check_payment = fields.Boolean(compute='check_payment_course', default=False, store=True)
    academy_institute = fields.Many2one('op.institute', string='Cơ sở')

    @api.depends('amount_total', 'amount_paid')
    def check_payment_course(self):
        for rec in self:
            rec.check_payment = False
            if rec.type_brand == 'academy':
                rec.check_payment = True if rec.amount_total <= rec.amount_paid else False

    def request_payment(self):
        vals = []
        if self.crm_line_ids:
            for rec in self.crm_line_ids:
                if rec.total > rec.paid:
                    vals.append(rec.id)
        return {
            'name': 'Yêu cầu thu phí',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('crm_academy.request_payment_form_view').id,
            'res_model': 'request.payment',
            'context': {
                'default_company_id': self.company_id.id,
                'default_partner_id': self.partner_id.id,
                'default_booking_id': self.id,
            },
            'target': 'new',
        }

    def request_debt(self):
        return {
            'name': 'Yêu cầu duyệt nợ',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('crm_academy.request_debt_form').id,
            'res_model': 'request.debt',
            'context': {
                'default_company_id': self.company_id.id,
                'default_partner_id': self.partner_id.id,
                'default_booking_id': self.id,
            },
            'target': 'new',
        }

    def create_students(self):
        return {
            'name': 'GHI DANH HỌC VIÊN',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('crm_academy.student_from_booking_form').id,
            'res_model': 'student.from.booking',
            'context': {
                'default_name': self.contact_name,
                'default_phone': self.phone,
                'default_lead_id': self.id,
                'default_institute_id': self.academy_institute.id,
            },
            'target': 'new',
        }

    def qualify_partner_academy(self):
        return {
            'name': 'THÔNG TIN LỊCH HẸN',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('crm_academy.check_partner_academy_view_form').id,
            'res_model': 'check.partner.qualify',
            'context': {
                'default_name': self.contact_name,
                'default_phone': self.phone,
                'default_lead_id': self.id,
                'default_company_id': self.company_id.id,
                'default_type': self.type,
                'default_partner_id': self.partner_id.id,
            },
            'target': 'new',
        }
