from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    _sql_constraints = [
        ('name_phone', 'unique(phone)', "Số điện thoại này đã tồn tại"),
    ]

    birth_date = fields.Date('Birth date')
    year_of_birth = fields.Char('Year of birth')
    age = fields.Integer('Age', compute='set_age')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')], string='Gender')
    pass_port = fields.Char('Pass port')
    relation_ids = fields.One2many('relation.partner', 'partner_id', string='Relation partner')
    code_customer = fields.Char('Code customer')
    crm_ids = fields.One2many('crm.lead', 'partner_id', string='CRM')
    payment_ids = fields.One2many('account.payment', 'partner_id', string='Payments')
    source_id = fields.Many2one('utm.source', string='Source')

    @api.model
    def default_get(self, fields):
        """ Hack :  when going from the pipeline, creating a stage with a sales team in
            context should not create a stage for the current Sales Team only
        """
        ctx = dict(self.env.context)
        if ctx.get('default_type') == 'lead' or ctx.get('default_type') == 'opportunity':
            ctx.pop('default_type')
        return super(ResPartner, self.with_context(ctx)).default_get(fields)

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        if res.company_type == 'person':
            res.code_customer = self.env['ir.sequence'].next_by_code('res.partner')
        return res

    def set_age(self):
        for rec in self:
            rec.age = 0
            if rec.year_of_birth and rec.year_of_birth.isdigit() is True:
                rec.age = fields.Datetime.now().year - int(rec.year_of_birth)

    @api.constrains('phone')
    def constrain_phone_number(self):
        for rec in self:
            if rec.phone and rec.phone.isdigit() is False:
                raise ValidationError('Điện thoại không được phép chứa ký tự chữ !!!')
