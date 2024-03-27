from odoo import fields, api, models, _
from odoo.exceptions import ValidationError
from odoo import modules
from odoo.tools.safe_eval import safe_eval
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

try:
    import qrcode
except ImportError:
    qrcode = None
try:
    import base64
except ImportError:
    base64 = None
from io import BytesIO


class Loyalty(models.Model):
    _name = 'crm.loyalty.card'

    _sql_constraints = [
        ('name_name', 'unique(name)', "Mã thẻ này đã được cấp !!!"),
        ('name_loyalty', 'unique(partner_id,brand_id)', "Khách hàng này đã có thẻ !!!"),
    ]

    # general
    name = fields.Char('Code card')
    rank_id = fields.Many2one('crm.loyalty.rank', string='Rank', tracking=True)
    reward_ids = fields.One2many('crm.loyalty.line.reward', 'loyalty_id', string="Reward", tracking=True)
    brand_id = fields.Many2one('res.brand', string='Brand', tracking=True, related='company_id.brand_id', store=True)
    partner_id = fields.Many2one('res.partner', string='Customer', tracking=True)
    birth_date = fields.Date('Birth date', related='partner_id.birth_date')
    phone = fields.Char('Phone', related='partner_id.phone', tracking=True)
    code_customer = fields.Char('Code customer', related='partner_id.code_customer', tracking=True)
    country_id = fields.Many2one('res.country', string='Country', tracking=True, related='partner_id.country_id')
    state_id = fields.Many2one('res.country.state', string='State', tracking=True, related='partner_id.state_id')
    address_detail = fields.Char('Address detail', related='partner_id.street', tracking=True)
    source_id = fields.Many2one('utm.source', string='Original source', tracking=True)
    create_by = fields.Many2one('res.users', string='Create by', tracking=True, default=lambda self: self.env.user)
    create_on = fields.Datetime('Create on', tracking=True, default=fields.Datetime.now())
    company_id = fields.Many2one('res.company', string='Company', tracking=True, default=lambda self: self.env.company)
    date_interaction = fields.Datetime('Date interaction', tracking=True)
    qr = fields.Binary(string="QR Code", compute='generate_qr')
    url = fields.Char('url')
    loyalty_import = fields.Boolean('Loyalty import')
    validity_card = fields.Integer('Validity card', related='rank_id.validity_card', store=True)
    due_date = fields.Datetime('Due date', compute='set_due_date', store=True)

    # cash
    currency_id = fields.Many2one('res.users', string='User', tracking=True)
    amount = fields.Monetary('Amount', tracking=True, store=True)

    # date special
    bonus = fields.Monetary('Bonus', tracking=True)
    rw_date_spc_ids = fields.One2many('crm.loyalty.reward.date.special', 'loyalty_id', string='Reward date special',
                                      tracking=True)

    image = fields.Binary('Image', default=False)
    date_special = fields.Many2many('crm.loyalty.date', 'loyalty_date_ref', 'loyalty', 'date_spc',
                                    string='Special date')
    time_active = fields.Integer('Time active')
    money_reward = fields.Monetary('Money reward')
    bonus_date_ids = fields.One2many('crm.loyalty.reward.date.special', 'loyalty_id', string='Bonus date')

    @api.depends('date_interaction', 'validity_card')
    def set_due_date(self):
        for rec in self:
            rec.due_date = False
            if rec.date_interaction:
                rec.due_date = rec.date_interaction + relativedelta(days=+ rec.validity_card)

    @api.depends('name')
    def generate_qr(self):
        for rec in self:
            rec.qr = False
            if qrcode and base64 and rec.name:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(rec.name)
                qr.make(fit=True)
                img = qr.make_image()
                temp = BytesIO()
                img.save(temp, format="PNG")
                qr_image = base64.b64encode(temp.getvalue())
                rec.qr = qr_image

    def write(self, vals):
        res = super(Loyalty, self).write(vals)
        for rec in self:
            if vals.get('amount'):
                rec.set_rank(rec.amount, rec.rank_id)
        return res

    def set_rank(self, amount, rank):
        if amount:
            rank_now = self.env['crm.loyalty.rank'].search(
                [('money_fst', '<=', amount),
                 ('money_end', '>=', amount),
                 ('brand_id', '=', self.brand_id.id)], limit=1)
            if rank is False or rank.id != rank_now.id:
                self.rank_id = rank_now
                self.set_reward(self.rank_id)
                self.get_special_date(self.rank_id)

    def set_reward(self, rank):
        if rank:
            rewards = self.env['crm.loyalty.line.reward'].search(
                [('brand_id', '=', self.brand_id.id), ('rank_id', '=', rank.id)])
            rw_general = set(rank.reward_ids) & set(self.reward_ids.mapped('reward_parent'))
            if not rw_general:
                for rw in rewards:
                    reward = self.env['crm.loyalty.line.reward'].create({
                        'name': rw.name,
                        'brand_id': rw.brand_id.id,
                        'loyalty_id': self.id,
                        'type_reward': rw.type_reward,
                        'quantity': rw.quantity,
                        'product_id': rw.product_id.id,
                        'category_id': rw.category_id,
                        'discount_percent': rw.discount_percent,
                        'rank': rw.rank_id.name,
                        'currency_id': rw.currency_id.id,
                        'reward_parent': rw.id,
                    })

    def get_special_date(self, rank):
        if rank.date_special:
            self.time_active = rank.time_active
            self.money_reward = rank.money_reward
            self.date_special = [(6, 0, rank.date_special.ids)]

    def find_loyalty_card_by_ref_using_qr(self, qr):
        if '/' in qr:
            qr = qr.rsplit('/', 1)[1]
            qr = qr.upper()
        loyalty_card = self.search([('name', '=', qr)], limit=1)
        if not loyalty_card:
            action = self.env.ref('loyalty.loyalty_card_find')
            result = action.read()[0]
            context = safe_eval(result['context'])
            context.update({
                'default_state': 'warning',
                'default_status': _('KHÔNG CÓ MÃ QR %s TRÊN HỆ THỐNG') % qr
            })
            result['context'] = context
            return result
        action = self.env.ref('loyalty.action_open_loyalty')
        result = action.read()[0]
        res = self.env.ref('loyalty.loyalty_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['res_id'] = loyalty_card.id
        return result

    def search_loyalty(self, ll):
        loyalty = self.env['crm.loyalty.card'].search([('date_special', '!=', False), ('id', 'not in', ll.ids)],
                                                      limit=100)
        if loyalty:
            self.cron_money_reward_loyalty(loyalty)
        else:
            self.cron_money_reward_loyalty(loyalty)

    # cong tien thuong
    def cron_money_reward_loyalty(self, ll):
        if not ll:
            loyalty = self.env['crm.loyalty.card'].search([('date_special', '!=', False)], limit=100)
        else:
            loyalty = ll
        today = fields.Date.today()
        month = today.month
        day = today.day
        for lt in loyalty:
            for rw in lt.date_special:
                if rw.type == 'b_date' and lt.partner_id.birth_date.month == month \
                        and lt.partner_id.birth_date.day == day:
                    self.set_bonus_date_special(rw, lt)

                elif rw.type == 'other' and rw.month == month and rw.date == date:
                    self.set_bonus_date_special(rw, lt)

    def set_bonus_date_special(self, rw, lt):
        self.env['crm.loyalty.reward.date.special'].create({
            'name': 'Bonus %s' % rw.name,
            'brand_id': lt.brand_id.id,
            'currency_id': self.env.user.company_id.currency_id.id,
            'reward_origin': lt.money_reward,
            'loyalty_id': lt.id,
            'type': 'reward',
            'active_date': fields.Datetime.now(),
            'end_date': fields.Datetime.now() + relativedelta(days=+ lt.time_active),
            'date_special': rw.id,
        })
