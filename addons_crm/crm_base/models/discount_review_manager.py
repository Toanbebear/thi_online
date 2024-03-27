from odoo import fields, api, models, _
from lxml import etree
from odoo.exceptions import ValidationError


class DiscountReviewManager(models.Model):
    _name = 'crm.discount.review'

    name = fields.Text('Reason for the discount')
    crm_line_id = fields.Many2one('crm.line', string='Line service')
    booking_id = fields.Many2one('crm.lead', string='Booking')
    partner_id = fields.Many2one('res.partner', string='Customer')
    type = fields.Selection([('discount_pr', 'Discount percent'), ('discount_cash', 'Discount cash')],
                            string='Type discount')
    discount = fields.Float('Discount', digits=(3, 0))
    stage_id = fields.Selection([('offer', 'Offer'), ('approve', 'Approve'), ('refuse', 'Refuse')], string='Stage',
                                default='offer')
    color = fields.Integer('Color Index', default=0)
    company_id = fields.Many2one('res.company', string='Company', related='booking_id.company_id', store=True)
    rule_discount_id = fields.Many2one('crm.rule.discount', string='Discount limit')
    active = fields.Boolean('Active', default=True)
    total_amount_after_discount = fields.Float('Total Amount After Discount',
                                               compute='_compute_total_amount_after_discount', store='True')

    @api.depends('discount', 'booking_id', 'crm_line_id')
    def _compute_total_amount_after_discount(self):
        for record in self:
            record.total_amount_after_discount = 0
            if record.discount and record.booking_id and record.crm_line_id:
                for line in record.booking_id.crm_line_ids:
                    if line.id == record.crm_line_id.id and line.total != 0:
                        record.total_amount_after_discount = line.total - (line.total * (record.discount/100))

    def approve(self):
        user = self.env.user
        if self.rule_discount_id and user not in self.rule_discount_id.user_ids:
            raise ValidationError('Bạn không có trong danh sách được duyệt giảm giá !!!')

        elif self.rule_discount_id and user in self.rule_discount_id.user_ids:
            for rec in self.crm_line_id:
                if self.type == 'discount_pr':
                    rec.discount_percent += self.discount
                elif self.type == 'discount_cash':
                    rec.discount_cash += self.discount
            self.stage_id = 'approve'
            self.color = 4

        else:
            raise ValidationError('Không thể duyệt giảm giá khi không có quy tắc giảm giá !!!')

    def refuse(self):
        for rec in self.crm_line_id:
            if self.type == 'discount_pr' and rec.discount_percent >= self.discount:
                rec.discount_percent -= self.discount
            elif self.type == 'discount_cash' and rec.discount_cash >= self.discount:
                rec.discount_cash -= self.discount
        self.stage_id = 'refuse'
        self.color = 0

    def name_get(self):
        result = []
        for rec in self:
            if rec.type and rec.discount and rec.stage_id:
                if rec.type == 'discount_pr':
                    name = 'Giảm thêm %s ' % rec.discount
                elif rec.type == 'discount_cash':
                    name = 'Giảm thêm %s VND' % rec.discount
            result.append((rec.id, name))
        return result


class RuleDiscount(models.Model):
    _name = 'crm.rule.discount'

    name = fields.Char('Name')
    discount = fields.Float('ceiling level')
    discount2 = fields.Float('Maximum levels')
    user_ids = fields.Many2many('res.users', string='User approve')
    active = fields.Boolean('Active', default=True)
    _sql_constraints = [
        ('name_discount', 'unique(discount,discount2)', "Mức giảm giá này đã tồn tại"),
    ]

    @api.onchange('discount', 'discount2')
    def set_name(self):
        self.name = False
        if self.discount:
            self.name = 'Giảm giá trên %s' % self.discount + '% ,' + 'dưới %s' % self.discount2 + '%'

    @api.constrains('discount')
    def condition_discount(self):
        for rec in self:
            if rec.discount <= 0:
                raise ValidationError('Mức giảm giá tối thiểu phải lớn hơn 0')
            if rec.discount >= rec.discount2:
                raise ValidationError('Mức giảm giá tối đa phải lớn hơn mức giảm giá tối thiểu')

    @api.constrains('discount2')
    def condition_discount2(self):
        for rec in self:
            if rec.discount and rec.discount2 < rec.discount or rec.discount2 > 100:
                raise ValidationError(
                    ('Mức giảm giá tối đa chỉ nhận giá trị lớn hơn %s và nhỏ hơn hoặc bằng 100') % rec.discount)
