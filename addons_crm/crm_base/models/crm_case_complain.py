from odoo import fields, api, models, _
from odoo.exceptions import ValidationError
from datetime import datetime
from lxml import etree
import json


class CaseCrm(models.Model):
    _name = 'crm.case'
    _inherit = "mail.thread"

    name = fields.Char('Name')
    subject_case = fields.Char('Subject')
    code = fields.Char('ID case')
    product_ids = fields.Many2many('product.product', string='Product')
    type_case = fields.Selection(
        [('complain', 'Complain'), ('warning', 'Warning')],
        string='Type case')
    priority = fields.Selection([('0', 'Low'), ('1', 'Normal'), ('2', 'high'), ('3', 'Urgency')], string='Priority')
    create_by = fields.Many2one('res.users', string='Owner', default=lambda self: self.env.user)
    create_on = fields.Datetime('Create on', default=fields.Datetime.now())
    stage_id = fields.Selection(
        [('new', 'New'), ('processing', 'Processing'), ('waiting', 'Waiting'), ('track', 'Need to track'),
         ('waiting_detail', 'Waiting for detail'), ('finding', 'Finding'), ('research', 'Researching'),
         ('duplicate', 'Duplicate client'), ('hold', 'On hold'), ('resolve', 'Resolve'), ('done', 'Done')],
        String='stage', default='new')
    brand_id = fields.Many2one('res.brand', string='Brand')
    company_id = fields.Many2one('res.company', string='Company')
    user_id = fields.Many2one('res.users', string='Handler')
    start_date = fields.Datetime('Start date', default=fields.Datetime.now())
    end_date = fields.Datetime('End date')
    duration = fields.Char('Duration', compute='set_duration')
    partner_id = fields.Many2one('res.partner', string='Customer')
    phone = fields.Char('Phone')
    country_id = fields.Many2one('res.country', string='Country', related='partner_id.country_id')
    state_id = fields.Many2one('res.country.state', string='State', related='partner_id.state_id')
    street = fields.Char('Street', related='partner_id.street')
    account_facebook = fields.Char('Account facebook')
    booking_id = fields.Many2one('crm.lead', string='Booking')
    phone_call_id = fields.Many2one('crm.phone.call', string='Phone call')
    content_complain_ids = fields.Many2many('crm.content.complain', string='Content complain')
    content_solution_ids = fields.Many2many('crm.case.solution', string='Content Solution')
    note = fields.Text('Note')

    @api.constrains('start_date', 'start_date')
    def check_date(self):
        """ Check that the total percent is not bigger than 100.0 """
        for rec in self:
            if rec.end_date and rec.start_date >= rec.end_date:
                raise ValidationError(
                    _('The start date must not be greater than or coincide with the end date !'))

    @api.depends('start_date', 'end_date')
    def set_duration(self):
        for rec in self:
            rec.duration = 'Received'
            if rec.start_date and rec.end_date:
                rec.duration = (rec.end_date - rec.start_date)
            else:
                rec.duration = '00:00:00'

    @api.onchange('end_date')
    def set_stage_done(self):
        for rec in self:
            if rec.end_date:
                rec.stage_id = 'done'
            else:
                rec.stage_id = 'processing'

    @api.onchange('stage_id')
    def onchange_end_date(self):
        for rec in self:
            if rec.stage_id == 'done':
                rec.end_date = datetime.now()

    @api.model
    def create(self, vals):
        res = super(CaseCrm, self).create(vals)
        res.code = self.env['ir.sequence'].next_by_code('crm.case')
        return res

    @api.onchange('phone')
    def check_partner(self):
        if self.phone:
            partner = self.env['res.partner'].search([('phone', '=', self.phone)])
            if partner:
                self.partner_id = partner.id
                self.country_id = partner.country_id.id
                self.state_id = partner.state_id.id
                self.street = partner.street

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(CaseCrm, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                   submenu=submenu)
        doc = etree.XML(res['arch'])
        if view_type == 'form':
            for node in doc.xpath("//field[@name='brand_id']"):
                node_domain = "[('id', 'in', %s)]" % self.env.user.company_ids.mapped('brand_id').ids
                node.set("domain", node_domain)
                modifiers = json.loads(node.get("modifiers"))
                modifiers['domain'] = node_domain
                node.set("modifiers", json.dumps(modifiers))

        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res


class CrmComplainCode(models.Model):
    _name = 'crm.complain.code'

    name = fields.Char('Name')
    code = fields.Char('Code')
    # brand_ids = fields.Many2many('res.brand', string='Brand')
    # company_ids = fields.Many2many('res.company', domain="[('brand_id','in',brand_ids)]")
    department_ids = fields.Many2many('hr.department', string='Department')

    _sql_constraints = [
        ('code_complain_uniq', 'unique(code)', 'This code already exists!')
    ]

class CrmContentComplain(models.Model):
    _name = 'crm.content.complain'
    _rec_name = 'department_id'

    name = fields.Char('Note')
    department_id = fields.Many2one('hr.department', string='Department')
    code_detail = fields.Many2many('crm.complain.code', string='Code detail',
                                   domain="[('department_ids','in',department_id)]")

class CrmCaseSolution(models.Model):
    _name = 'crm.case.solution'

    desc = fields.Text('Phản ánh khách hàng')
    solution = fields.Text('Giải pháp')