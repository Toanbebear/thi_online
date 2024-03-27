from odoo import fields, api, models, _
from odoo.exceptions import ValidationError


class LoyaltyLineReward(models.Model):
    _name = 'crm.loyalty.line.reward'

    name = fields.Char('Name')
    brand_id = fields.Many2one('res.brand', string='Brand')
    rank_id = fields.Many2one('crm.loyalty.rank', string='Rank', domain="[('brand_id','=',brand_id)]")
    loyalty_id = fields.Many2one('crm.loyalty.card', string='Loyalty')
    # reward
    # loai 1 : loại sản phẩm là cho phép khách hàng đc sử dụng miễn phí với số lượng giới hạn
    # loại 2 : loại nhóm sản phẩm cho phép nếu như người dụng chọn sản phẩm trong nhóm này thì sẽ ddc giảm thêm
    # loại 3 : loại ngày đặc biệt cho phép nếu như đến ngày này kh sẽ đc phần quà , và phần quà này có giới hạn time

    type_reward = fields.Selection([('prd', 'Product'), ('ctg', 'Category product')], string='Type reward')
    quantity = fields.Integer('Quantity free', default=1)
    product_id = fields.Many2one('product.product', string='Product', domain="[('type_product_crm','=','service_crm')]")
    number_use = fields.Integer('Number used', compute='set_number_use')
    category_id = fields.Many2many('product.category', string='Category')
    discount_percent = fields.Float('Discount percent')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    stage = fields.Selection([('allow', 'Allow to use'),
                              ('used', 'Used up'),
                              ('not_allow', 'Not allowed to use')],
                             string='Stage', compute='check_stage')
    active = fields.Boolean('Active', default=True)
    reward_parent = fields.Many2one('crm.loyalty.line.reward', string='Reward parent')
    crm_line_ids = fields.One2many('crm.line', 'reward_id', string='Crm line')
    rank = fields.Char('Document rank')

    @api.depends('loyalty_id', 'number_use', 'quantity', 'type_reward')
    def check_stage(self):
        for rec in self:
            rec.stage = 'not_allow'
            if rec.type_reward == 'prd' and rec.loyalty_id:
                if rec.number_use == rec.quantity:
                    rec.stage = 'used'
                elif rec.reward_parent in rec.loyalty_id.rank_id.reward_ids:
                    rec.stage = 'allow'
                else:
                    rec.stage = 'not_allow'
            elif rec.type_reward != 'prd' and rec.loyalty_id:
                if rec.reward_parent in rec.loyalty_id.rank_id.reward_ids:
                    rec.stage = 'allow'
                else:
                    rec.stage = 'not_allow'

    @api.depends('crm_line_ids')
    def set_number_use(self):
        for rec in self:
            rec.number_use = 0
            if rec.crm_line_ids:
                for i in rec.crm_line_ids:
                    rec.number_use += i.number_used

    def use_reward(self):
        return {
            'name': 'Sử dụng quà tặng',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('loyalty.use_reward_form').id,
            'res_model': 'crm.loyalty.use.reward',
            'context': {
                'default_reward_id': self.id,
                'default_loyalty_id': self.loyalty_id.id,
                'default_partner_id': self.loyalty_id.partner_id.id,
            },
            'target': 'new',
        }

    @api.constrains('quantity')
    def check_quantity(self):
        for rec in self:
            if rec.quantity < 1:
                raise ValidationError('Số lượng miễn phí phải lơn hơn hoặc bằng 1')

    @api.constrains('reward')
    def check_reward(self):
        for rec in self:
            if rec.type_reward == 'date_spc' and rec.reward <= 0:
                raise ValidationError('Tiền thưởng không thể nhỏ hơn hoặc bằng 0')

    @api.onchange('type_discount')
    def reset_by_type(self):
        if self.type_reward != 'prd':
            self.quantity = 1
            self.product_id = False
        if self.type_reward != 'ctg':
            self.category_id = False
            self.reward = 0
        if self.type_reward != 'date_spc':
            self.type_date = False
            self.day = 0
            self.reward = 0


class DateSpecial(models.Model):
    _name = 'crm.loyalty.reward.date.special'

    name = fields.Char('Name')
    brand_id = fields.Many2one('res.brand', string='Brand')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    reward_origin = fields.Monetary('Bonus origin')
    reward_used = fields.Monetary('Bonus used')
    reward_remain = fields.Monetary('Bonus remain', compute='set_remain', store=True)
    stage = fields.Selection([('use', 'Allow to use'), ('used_up', 'Used up'), ('expired', 'Expired')], string='Stage')
    loyalty_id = fields.Many2one('crm.loyalty.card', string='Loyalty')
    type = fields.Selection([('reward', 'Reward'), ('use', 'Use')], string='Type')
    active_date = fields.Datetime('Active date')
    end_date = fields.Datetime('End date')
    date_special = fields.Many2one('crm.loyalty.date', string='Date special')
    bonus_date_parent_id = fields.Many2one('crm.loyalty.reward.date.special', string='Bonus date parent')
    bonus_date_child_ids = fields.One2many('crm.loyalty.reward.date.special', 'bonus_date_parent_id',
                                           string='Bonus date child')

    @api.depends('reward_origin', 'reward_used')
    def set_remain(self):
        for rec in self:
            self.reward_remain = self.reward_origin - self.reward_used


class LoyaltyDate(models.Model):
    _name = 'crm.loyalty.date'

    name = fields.Char('Name')
    type = fields.Selection([('b_date', 'Birth date'), ('other', 'Other')], string='Type date')
    brand_id = fields.Many2one('res.brand', string='Brand')
    date = fields.Integer('Date')
    month = fields.Integer('Month')
    reward_ids = fields.Many2many('crm.loyalty.line.reward', 'reward_date_ref', 'reward', 'date', string='Rewards')
    loyalty_ids = fields.Many2many('crm.loyalty.card', 'loyalty_date_ref', 'date_spc', 'loyalty', string='Loyalty')
