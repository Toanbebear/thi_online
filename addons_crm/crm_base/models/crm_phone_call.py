from odoo.osv import expression
from dateutil.relativedelta import relativedelta
from odoo import fields, api, models, _
from lxml import etree
import json


class PhoneCall(models.Model):
    _name = "crm.phone.call"
    _inherit = "mail.thread"

    name = fields.Char(string="Name", tracking=True)
    subject = fields.Char(string='Subject', tracking=True)
    user_id = fields.Many2one('res.users', string='Sale person', tracking=True, default=lambda self: self.env.user)
    contact_name = fields.Char('Contact name', tracking=True)
    partner_id = fields.Many2one('res.partner', string='Account customer', tracking=True)
    phone = fields.Char('Phone', tracking=True)
    direction = fields.Selection([('in', 'Ingoing'), ('out', 'Outgoing')], string='direction', tracking=True)
    desc = fields.Text('Description', tracking=True)
    brand_id = fields.Many2one('res.brand', string='Brand', tracking=True, related='company_id.brand_id', store=True)
    company_id = fields.Many2one('res.company', string='Company', tracking=True,
                                 default=lambda self: self.env.company)
    crm_id = fields.Many2one('crm.lead', string='Regarding booking', tracking=True, domain='[("type","!=","lead")]')
    order_id = fields.Many2one('sale.order', string='Regarding order', tracking=True)
    country_id = fields.Many2one('res.country', string='Country', default=241, tracking=True)
    state_id = fields.Many2one('res.country.state', string='City', tracking=True)
    street = fields.Char('Street', tracking=True)
    type_crm_id = fields.Many2one('crm.type', string='Type phone call', domain="[('phone_call','=',True)]",
                                  tracking=True)
    stage_id = fields.Many2one('crm.stage', string='Stage', tracking=True, domain="[('crm_type_id','in',type_crm_id)]")
    note = fields.Text('Note', tracking=True)
    crm_line_id = fields.Many2many('crm.line', 'line_phone_call_ref', 'phone_call', 'line', string='Service')
    booking_date = fields.Datetime('Booking date', tracking=True)
    call_date = fields.Datetime('Call date', default=fields.Datetime.now, tracking=True)
    create_on = fields.Datetime('Create on', default=fields.Datetime.now, tracking=True)
    create_by = fields.Many2one('res.users', string='Create by', default=lambda self: self.env.user, tracking=True)
    active = fields.Boolean('Active', default=True)
    assign_time = fields.Datetime('Assign time', tracking=True, default=fields.Datetime.now)
    type_brand = fields.Selection([('hospital', 'Hospital'), ('academy', 'Academy')], string='Type brand',
                                  related='brand_id.type')
    active = fields.Boolean('Active', default=True)
    code_customer = fields.Char('Code customer', related='partner_id.code_customer', store=True)

    def create_case(self):
        return {
            'name': 'Case',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('crm_base.crm_case_view_form').id,
            'res_model': 'crm.case',
            'context': {
                'default_booking_id': self.crm_id.id,
                'default_company_id': self.company_id.id,
                'default_partner_id': self.partner_id.id,
                'default_phone_call_id': self.id,
                'default_phone': self.phone,
                'default_country_id': self.country_id.id,
                'default_state_id': self.state_id.id,
                'default_street': self.street,
                'default_brand_id': self.brand_id.id,
                'default_account_facebook': self.crm_id.facebook_acc,
            },
            'target': 'new',
        }

    @api.onchange('booking_date')
    def set_call_date_1(self):
        if self.booking_date:
            self.call_date = self.booking_date - relativedelta(days=+1)

    @api.onchange('phone')
    def set_partner(self):
        if self.phone:
            partner = self.env['res.partner'].search([('phone', '=', self.phone)])
            if partner:
                self.partner_id = partner.id
                self.contact_name = partner.name
                self.country_id = partner.country_id.id
                self.state_id = partner.state_id.id
                self.street = partner.street

    def write(self, vals):
        res = super(PhoneCall, self).write(vals)
        for rec in self:
            if rec.type_crm_id == self.env.ref('crm_base.type_phone_call_confirm_appointment') and rec.crm_id and \
                    rec.crm_id.stage_id == self.env.ref('crm_base.crm_stage_not_confirm'):
                if vals.get('stage_id') == self.env.ref('crm_base.crm_stage_confirm').id:
                    rec.crm_id.stage_id = self.env.ref('crm_base.crm_stage_confirm').id

            if vals.get('booking_date'):
                phone_call = self.env['crm.phone.call'].create({
                    'name': _('Confirm appointment'),
                    'subject': _('Confirm appointment'),
                    'user_id': 1,
                    'contact_name': rec.contact_name,
                    'partner_id': rec.partner_id.id,
                    'phone': rec.phone,
                    'direction': 'out',
                    'company_id': rec.company_id.id,
                    'crm_id': rec.crm_id.id,
                    'country_id': rec.country_id.id,
                    'state_id': rec.state_id.id,
                    'street': rec.street,
                    'type_crm_id': self.env.ref('crm_base.type_phone_call_confirm_appointment').id,
                    'stage_id': self.env.ref('crm_base.crm_stage_no_process').id,
                    'crm_line_id': [(6, 0, rec.crm_line_id.ids)],
                    'booking_date': rec.booking_date,
                    'call_date': rec.booking_date - relativedelta(days=+1),
                    'create_by': 1,
                })
                rec.crm_id.booking_date = rec.booking_date
                rec.stage_id = self.env.ref('crm_base.crm_stage_change_schedule').id

        return res

