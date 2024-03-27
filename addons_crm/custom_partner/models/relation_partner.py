from odoo import fields, api, models, _


class TypeRelative(models.Model):
    _name = 'type.relative'

    name = fields.Char('Name', translate=True)
    symmetry_relative = fields.Many2one('type.relative', string='Symmetry relative')


class RelationPartner(models.Model):
    _name = 'relation.partner'

    name = fields.Char('Name', compute='relatives_get_name', store=True)
    partner_id = fields.Many2one('res.partner', string='Customer')
    relative_name = fields.Char('Relatives name')
    relative_id = fields.Many2one('res.partner', string='Account Relatives')
    country_id = fields.Many2one('res.country', string='Country', default=241)
    state_id = fields.Many2one('res.country.state', string='State', domain="[('country_id', '=', country_id)]")
    street = fields.Char('Street')
    type_relative_id = fields.Many2one('type.relative', string='Relative')
    birth_date = fields.Date('Birth date')
    pass_port = fields.Char('Pass port')
    phone = fields.Char('Phone')
    company_id = fields.Many2one('res.company', string='Company')

    @api.depends('partner_id', 'relative_id', 'type_relative_id')
    def relatives_get_name(self):
        for rec in self:
            if rec.type_relative_id and rec.partner_id and rec.relative_id:
                rec.name = (_('%s là %s của %s ')) % (
                    rec.relative_name, rec.type_relative_id.name, rec.partner_id.name)

    @api.model
    def create(self, vals):
        relation = super(RelationPartner, self).create(vals)
        domain = []
        if relation.phone:
            domain += [('phone', '=', relation.phone)]
            partner = self.env['res.partner'].search(domain)
            relation.relative_id = partner.id

        return relation

    # @api.model
    # def write(self, vals):
    #     res = super(RelationPartner, self).write(vals)
    #     for rec in self:
    #         if vals.get('relative_name'):
    #             rec.relative_id.name = rec.relative_name
    #         if vals.get('street'):
    #             rec.relative_id.street = rec.street
    #         if vals.get('state_id'):
    #             rec.relative_id.state_id = rec.state_id.id
    #         if vals.get('phone'):
    #             rec.relative_id.phone = rec.phone
    #         if vals.get('pass_port'):
    #             rec.relative_id.pass_port = rec.pass_port
    #     return res
