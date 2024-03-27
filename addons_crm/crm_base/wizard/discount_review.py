from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class DiscountReview(models.TransientModel):
    _name = 'discount.review'

    name = fields.Text('Reason for the discount')
    crm_line_id = fields.Many2one('crm.line', string='Service',
                                  domain="[('crm_id','=',booking_id),('stage','=','new'),('number_used','=',0)]")
    booking_id = fields.Many2one('crm.lead', string='Booking')
    partner_id = fields.Many2one('res.partner', string='Customer')
    type = fields.Selection([('discount_pr', 'Discount percent'), ('discount_cash', 'Discount cash')],
                            string='Type discount')
    rule_discount_id = fields.Many2one('crm.rule.discount', string='Discount limit')
    discount = fields.Float('Discount')

    @api.constrains('discount', 'type')
    def error_discount(self):
        for rec in self:
            if rec.type == 'discount_pr':
                if rec.discount <= 0 or rec.discount > 100:
                    raise ValidationError('Chỉ nhận giảm giá trong khoảng từ 0 đến 100 !!!')
                elif rec.discount + 100 - \
                        (rec.crm_line_id.total / rec.crm_line_id.total_before_discount) * \
                        100 > rec.rule_discount_id.discount2:
                    raise ValidationError('Tổng giảm giá xin duyệt của line dịch vụ này '
                                          'đang vượt quá mức cao nhất của quy tắc giảm giá bạn chọn !!!')
            if rec.type == 'discount_cash':
                if rec.discount > rec.crm_line_id.total:
                    raise ValidationError('Số tiền xin giảm giá đang lớn hơn tổng tiền của line dịch vụ !!!')
                elif 100 - (rec.crm_line_id.total - rec.discount) / rec.crm_line_id.total_before_discount * 100 \
                        > rec.rule_discount_id.discount2:
                    raise ValidationError('Tổng giảm giá xin duyệt của line dịch vụ này '
                                          'đang vượt quá mức cao nhất của quy tắc giảm giá bạn chọn !!!')

    def offer(self):
        rv = self.env['crm.discount.review'].create({
            'name': self.name,
            'crm_line_id': self.crm_line_id.id,
            'booking_id': self.booking_id.id,
            'partner_id': self.partner_id.id,
            'type': self.type,
            'discount': self.discount,
            'rule_discount_id': self.rule_discount_id.id,
        })
        self.crm_line_id.discount_review_id = rv.id

        view_rec = self.env.ref('crm_base.view_discount_review_finish',
                                raise_if_not_found=False)
        action = self.env.ref(
            'crm_base.action_view_discount_review_wizard', raise_if_not_found=False
        ).read([])[0]
        action['views'] = [(view_rec and view_rec.id or False, 'form')]
        return action
