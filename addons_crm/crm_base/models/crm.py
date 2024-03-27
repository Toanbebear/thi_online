from odoo import fields, api, models
from lxml import etree
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
from datetime import datetime, date, timedelta
import json
from dateutil.relativedelta import relativedelta

class CRMFamilyInfo(models.Model):
    _name = 'crm.family.info'

    crm_id = fields.Many2one('crm.lead', string="CRM",invisible=1)
    member_name = fields.Char(string='Name')
    type_relation_id = fields.Many2one('type.relative', string='Type relation')
    phone = fields.Char(string='Phone')
    member_contact = fields.Char(string='Contact No')

class CRM(models.Model):
    _inherit = 'crm.lead'

    # infomation customer

    birth_date = fields.Date('Birth date', tracking=True)
    year_of_birth = fields.Char('Year of birth', tracking=True)
    age = fields.Integer('Age', tracking=True)
    gender = fields.Selection([('male', 'Male'),
                               ('female', 'Female'),
                               ('other', 'Other')], string='Gender',
                              tracking=True)
    pass_port = fields.Char('Pass port', tracking=True)
    # general

    create_on = fields.Datetime('Create on', default=fields.Datetime.now)
    create_by = fields.Many2one('res.users', string='Create by', default=lambda self: self.env.user)
    assign_time = fields.Datetime('Assign time', tracking=True, default=fields.Datetime.now)

    assign_person = fields.Many2one('res.users', string='Assigned person', tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', tracking=True, related='price_list_id.currency_id')
    special_note = fields.Text('Special note', tracking=True)
    product_ctg_ids = fields.Many2many('product.category', 'product_ctg_crm_ref', 'crm_ids', 'product_ctg_ids',
                                       string='Product category', tracking=True)
    crm_line_ids = fields.One2many('crm.line', 'crm_id', string='Line service', tracking=True)
    department_id = fields.Many2one('hr.department', string='Business unit', tracking=True, compute='set_department',
                                    store=True)
    facebook_acc = fields.Char('Facebook account', tracking=True)
    fam_ids = fields.One2many('crm.family.info', 'crm_id', string='Family', help='Family Information')
    type_crm_id = fields.Many2one('crm.type', string='Type record',
                                  domain='[("phone_call","=",False),("type_crm","=",type)]')
    brand_id = fields.Many2one('res.brand', string='Brand', store=True)
    price_list_id = fields.Many2one('product.pricelist', string='Price list', tracking=True,
                                    domain="[('type','=','service'),('brand_id','=',brand_id)]")
    category_source_id = fields.Many2one('crm.category.source', string='Category source')
    source_id = fields.Many2one(domain="[('category_id','=',category_source_id)]")

    # booking
    customer_come = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Customer come', tracking=True)
    lead_id = fields.Many2one('crm.lead', string='Lead/Booking', tracking=True)
    booking_date = fields.Datetime('Booking date', default=fields.Datetime.now)
    payment_ids = fields.One2many('account.payment', 'crm_id', string='Payment')
    check_paid = fields.Boolean('Check paid')
    amount_total = fields.Monetary('Total', compute='set_total', group_operator="sum", store=True)
    amount_paid = fields.Monetary('Paid', compute='set_paid_booking', group_operator="sum", store=True)
    amount_used = fields.Monetary('Used', compute='set_used_booking', group_operator="sum", store=True)
    amount_remain = fields.Monetary('Remain', compute='set_amount_remain', group_operator="sum", store=True)
    reason_cancel = fields.Text('Reason')
    discount_review_ids = fields.One2many('crm.discount.review', 'booking_id', string='Deep discounts')
    code_customer = fields.Char('Code customer', related='partner_id.code_customer', store=True)
    wallet_id = fields.Many2one('partner.wallet', string='Wallet')
    type_brand = fields.Selection([('hospital', 'Hospital'), ('academy', 'Academy')], string='Type brand',
                                  related='brand_id.type', store=True)
    order_ids = fields.One2many('sale.order', 'booking_id', string='Orders')
    history_discount_ids = fields.One2many('history.discount', 'crm_id', string='History discount')
    check_won = fields.Boolean('Check won', compute='set_check_won')
    code_booking = fields.Char('Mã booking tương ứng')

    # lead
    booking_ids = fields.One2many('crm.lead', 'lead_id', string='Booking', tracking=True)
    re_open = fields.Boolean('Re-open', default=False)
    check_booking = fields.Boolean('Check booking', compute='set_check_booking', store=True)
    lead_insight = fields.Boolean('Lead insight ?')
    # inherit field
    team_id = fields.Many2one(default=False, domain="[('company_id', '=', company_id)]")
    stage_id = fields.Many2one(domain="[('crm_type_id', 'in',type_crm_id)]", default=False)
    country_id = fields.Many2one(default=241)
    company2_id = fields.Many2many('res.company', 'company_crm_share_ref', 'crm', 'company', string='Company shared',
                                   tracking=True)
    type_data = fields.Selection([('old', 'Old'), ('new', 'New')], string='Type data')
    arrival_date = fields.Datetime('Arrival date')
    type_price_list = fields.Selection('Type', related='price_list_id.type')

    # @api.depends('price_list_id')
    # def _get_type_booking(self):
    #     for record in self:
    #         if record.price_list_id:
    #             record.is_guarantee = True if record.price_list_id.type == 'guarantee' else False
    #         print(record.is_guarantee)

    @api.constrains('birth_date', 'year_of_birth')
    def constrains_year_date(self):
        for record in self:
            if record.birth_date and record.year_of_birth and record.birth_date.year != int(record.year_of_birth):
                raise ValidationError("Giá trị NĂM của trường năm sinh và trường ngày sinh không trùng khớp")

    @api.onchange('company_id')
    def _onchange_action(self):
        domain = {'brand_id': [('id', 'in', self.company_id.brand_ids.ids)]}
        self.brand_id = self.company_id.brand_id.id
        return {'domain': domain}

    @api.onchange('category_source_id')
    def onchange_by_category(self):
        if self.category_source_id and self.source_id.category_id != self.category_source_id:
            self.source_id = False

    @api.onchange('country_id')
    def onchange_by_country(self):
        if self.state_id and self.state_id.country_id != self.country_id:
            self.state_id = False
            self.street = False

    @api.depends('user_id')
    def set_department(self):
        for rec in self:
            rec.department_id = False
            if rec.user_id:
                rec.department_id = self.env['hr.employee'].sudo().search(
                    [('user_id', '=', rec.user_id.id)]).department_id.id

    # @api.constrains('phone_relatives')
    # def check_phone_relatives(self):
    #     for rec in self:
    #         if rec.phone_relatives:
    #             if rec.phone_relatives.isdigit() is False:
    #                 raise ValidationError('Điện thoại người thân 1 chỉ nhận giá trị số')
    #             elif len(rec.phone_relatives) > 10:
    #                 raise ValidationError('Điện thoại người thân 1 không được vượt quá 10 kí tự')

    @api.constrains('year_of_birth')
    def validate_year(self):
        for rec in self:
            if rec.year_of_birth:
                if int(rec.year_of_birth) >= date.today().year:
                    raise ValidationError('Năm sinh phải nhỏ hơn năm hiện tại')

    # @api.constrains('mobile_relatives')
    # def check_mobile_relatives(self):
    #     for rec in self:
    #         if rec.mobile_relatives:
    #             if rec.mobile_relatives.isdigit() is False:
    #                 raise ValidationError('Điện thoại người thân 2 chỉ nhận giá trị số')
    #             elif len(rec.mobile_relatives) > 10:
    #                 raise ValidationError('Điện thoại người thân 2 không được vượt quá 10 kí tự')
    #             elif rec.phone_relatives and rec.mobile_relatives == rec.phone_relatives:
    #                 raise ValidationError('Điện thoại người thân 2 không được trùng với Điện thoại người thân 1')

    @api.constrains('phone')
    def check_phone(self):
        for rec in self:
            if rec.phone:
                if rec.phone.isdigit() is False:
                    raise ValidationError('Điện thoại khách hàng chỉ nhận giá trị số')

    # @api.constrains('mobile')
    # def check_mobile(self):
    #     for rec in self:
    #         if rec.mobile:
    #             if rec.mobile.isdigit() is False:
    #                 raise ValidationError('Điện thoại khách hàng 2 chỉ nhận giá trị số')
    #             elif len(rec.mobile) > 10:
    #                 raise ValidationError('Điện thoại khách hàng 2 không được vượt quá 10 kí tự')
    #             elif rec.phone and rec.mobile == rec.phone:
    #                 raise ValidationError('Điện thoại khách hàng 2 không được trùng với điện thoại khách hàng 1')

    def create_phone_call_info(self):
        if self.company_id not in self.env.user.company_ids:
            raise ValidationError('Bạn không có quyền tạo phone call của %s' % self.company2_id.name)
        else:
            pc = self.env['crm.phone.call'].create({
                'name': 'Khách hàng %s hỏi thêm thông tin' % self.contact_name,
                'subject': 'Khách hàng hỏi thêm thông tin',
                'user_id': self.env.user.id,
                'contact_name': self.partner_id.name,
                'partner_id': self.partner_id.id,
                'phone': self.partner_id.phone,
                'direction': 'in',
                'company_id': self.company_id.id,
                'crm_id': self.id,
                'country_id': self.country_id.id,
                'state_id': self.state_id.id,
                'street': self.street,
                'type_crm_id': self.env.ref('crm_base.type_phone_call_customer_ask_info').id,
                'stage_id': self.env.ref('crm_base.crm_stage_no_process').id,
                'booking_date': self.booking_date,
                'crm_line_id': [(6, 0, self.crm_line_ids._origin.ids)],
            })

            return {
                'name': 'Phone call',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': pc.id,
                'view_id': self.env.ref('crm_base.view_form_phone_call').id,
                'res_model': 'crm.phone.call',
                'context': {},
            }

    @api.depends('booking_ids')
    def set_check_booking(self):
        for rec in self:
            rec.check_booking = False
            if rec.booking_ids:
                rec.check_booking = True
            else:
                rec.check_booking = False

    @api.depends('stage_id')
    def set_check_won(self):
        for rec in self:
            rec.check_won = False
            if rec.stage_id == self.env.ref('crm.stage_lead4'):
                rec.check_won = True

    def reopen_lead(self):
        self.stage_id = self.env.ref('crm_base.crm_stage_re_open').id
        self.re_open = True

    @api.onchange('customer_come')
    def set_stage_customer_come(self):
        if self.customer_come == 'yes':
            self.stage_id = self.env.ref('crm_base.crm_stage_confirm').id
            self.arrival_date = fields.Datetime.now()
        else:
            self.arrival_date = False

    def update_info(self):
        self.stage_id = self.env.ref('crm_base.crm_stage_booking').id
        self.re_open = False
        if self.booking_ids:
            for rec in self.booking_ids:
                rec.write({
                    'contact_name': self.contact_name,
                    'phone': self.phone,
                    'mobile': self.mobile,
                    'gender': self.gender,
                    'country_id': self.country_id.id,
                    'state_id': self.state_id.id,
                    'academy_institute': self.academy_institute or False,
                    'street': self.street,
                    'birth_date': self.birth_date,
                    'year_of_birth': self.year_of_birth,
                    'pass_port': self.pass_port,
                    'facebook_acc': self.facebook_acc,
                    'email_from': self.email_from,
                    'fam_ids': [(6, 0, self.fam_ids.ids)],
                })

        if self.partner_id:
            self.partner_id.write({
                'name': self.contact_name,
                'phone': self.phone,
                'mobile': self.mobile,
                'gender': self.gender,
                'year_of_birth': self.year_of_birth,
                'pass_port': self.pass_port,
                'country_id': self.country_id.id,
                'state_id': self.state_id.id,
                'street': self.street,
            })

    @api.onchange('phone')
    def check_partner_lead(self):
        if self.phone and self.type == 'lead' and self.stage_id != self.env.ref('crm_base.crm_stage_re_open'):

            partner = self.env['res.partner'].search([('phone', '=', self.phone)])

            lead_ids = self.env['crm.lead'].search(
                [('phone', '=', self.phone), ('brand_id', '=', self.brand_id.id)], order="id asc", limit=1)
            if partner:
                self.partner_id = partner.id
                self.gender = partner.gender
                self.birth_date = partner.birth_date
                self.country_id = partner.country_id.id
                self.state_id = partner.state_id.id
                self.street = partner.street
                self.mobile = partner.mobile
                self.year_of_birth = partner.year_of_birth
                self.pass_port = partner.pass_port
                self.contact_name = partner.name
                self.type_data = 'old' if lead_ids else 'new'
                self.source_id = partner.source_id.id
                self.category_source_id = partner.source_id.category_id.id
            else:
                self.partner_id = False
                self.gender = lead_ids.gender
                self.birth_date = lead_ids.birth_date
                self.country_id = lead_ids.country_id.id if lead_ids else self.env.ref('base.vn').id
                self.state_id = lead_ids.state_id.id
                self.street = lead_ids.street
                self.mobile = lead_ids.mobile
                self.year_of_birth = lead_ids.year_of_birth
                self.pass_port = lead_ids.pass_port
                self.contact_name = lead_ids.contact_name
                self.source_id = lead_ids.source_id.id
                self.type_data = 'old' if lead_ids else 'new'
                self.category_source_id = lead_ids.source_id.category_id.id
                self.email_from = lead_ids.email_from
                self.facebook_acc = lead_ids.facebook_acc

    def open_discount_review(self):
        if not self.crm_line_ids:
            raise ValidationError(_('Booking does not contain services'))
        elif self.stage_id not in [self.env.ref('crm_base.crm_stage_not_confirm'),
                                   self.env.ref('crm_base.crm_stage_confirm')]:
            raise ValidationError(_('Booking has begun to process cannot apply any discounts'))
        else:
            return {
                'name': 'GIẢM GIÁ SÂU',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': self.env.ref('crm_base.view_discount_review').id,
                'res_model': 'discount.review',
                'context': {
                    'default_booking_id': self.id,
                    'default_partner_id': self.partner_id.id,
                    'default_crm_line_ids': self.crm_line_ids.ids,
                },
                'target': 'new',
            }

    @api.onchange('contact_name')
    def set_upper_name(self):
        if self.contact_name:
            contact = self.contact_name
            self.contact_name = contact.upper()

    @api.onchange('contact_name')
    def set_name_lead(self):
        if self.type == 'lead':
            self.name = self.contact_name
            if self.contact_name:
                self.name = self.contact_name.upper()

    def clone_lead(self):
        return {
            'name': 'LEAD',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('crm_base.form_crm_lead').id,
            'res_model': 'crm.lead',
            'context': {
                'default_name': self.name,
                'default_contact_name': self.contact_name,
                'default_partner_id': self.partner_id.id,
                'default_type_crm_id': self.type_crm_id.id,
                'default_type': self.type,
                'default_gender': self.gender,
                'default_birth_date': self.birth_date,
                'default_year_of_birth': self.year_of_birth,
                'default_phone': self.phone,
                'default_mobile': self.mobile,
                'default_pass_port': self.pass_port,
                'default_country_id': self.country_id.id,
                'default_state_id': self.state_id.id,
                'default_street': self.street,
                'default_email_from': self.email_from,
                'default_facebook_acc': self.facebook_acc,
                'default_stage_id': self.env.ref('crm_base.crm_stage_no_process').id,
                'default_company_id': self.company_id.id,
                'default_description': 'COPY',
                'default_special_note': self.special_note,
                'default_price_list_id': self.price_list_id.id,
                'default_currency_id': self.currency_id.id,
                'default_source_id': self.source_id.id,
                'default_campaign_id': self.campaign_id.id,
                'default_medium_id': self.medium_id.id,
                'default_category_source_id': self.category_source_id.id,
            },
        }

    def share_booking(self):
        return {
            'name': 'Share booking',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('crm_base.view_share_booking').id,
            'res_model': 'share.booking',
            'context': {
                'default_booking_id': self.id,
            },
            'target': 'new',
        }

    def cancel_booking(self):
        return {
            'name': 'Close booking',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('crm_base.view_form_cancel_booking').id,
            'res_model': 'cancel.booking',
            'context': {
                'default_booking_id': self.id,
            },
            'target': 'new',
        }

    def create_booking_guarantee(self):
        return {
            'name': 'Create booking guarantee',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('crm_base.view_form_create_booking_guarantee').id,
            'res_model': 'crm.create.guarantee',
            'context': {
                'default_crm_id': self.id,
                'default_brand_id': self.brand_id.id,
                'default_partner_id': self.partner_id.id,
            },
            'target': 'new',
        }

    def qualify_partner(self):
        return {
            'name': 'THÔNG TIN LỊCH HẸN',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('crm_base.check_partner_view_form').id,
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

    def apply_discount(self):
        return {
            'name': 'Áp dụng voucher',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('crm_base.view_apply_discount').id,
            'res_model': 'crm.apply.voucher',
            'context': {
                'default_partner_id': self.partner_id.id,
                'default_crm_id': self.id,
            },
            'target': 'new',
        }

    def apply_prg(self):
        return {
            'name': 'Áp dụng chương trình giảm giá',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('crm_base.view_apply_discount_prg').id,
            'res_model': 'crm.apply.discount.program',
            'context': {
                'default_partner_id': self.partner_id.id,
                'default_crm_id': self.id,
                'default_campaign_id': self.campaign_id.id,
            },
            'target': 'new',
        }

    @api.onchange('company_id')
    def reset_sale_team(self):
        self.team_id = False
        self.price_list_id = False

    @api.onchange('birth_date')
    def set_year_of_birth(self):
        if self.birth_date:
            self.year_of_birth = self.birth_date.year

    @api.onchange('company_id')
    def set_price_list(self):
        if self.company_id:
            self.price_list_id = False

    def write(self, vals):
        res = super(CRM, self).write(vals)
        for rec in self:
            if rec.partner_id:
                if vals.get('contact_name'):
                    rec.partner_id.name = rec.contact_name
                if vals.get('phone'):
                    rec.partner_id.phone = rec.phone
                if vals.get('gender'):
                    rec.partner_id.gender = rec.gender
                if vals.get('birth_date'):
                    rec.partner_id.birth_date = rec.birth_date
                if vals.get('pass_port'):
                    rec.partner_id.pass_port = rec.pass_port
                if vals.get('country_id'):
                    rec.partner_id.country_id = rec.country_id.id
                if vals.get('state_id'):
                    rec.partner_id.state_id = rec.state_id.id
                if vals.get('street'):
                    rec.partner_id.street = rec.street
        return res

    @api.model
    def create(self, vals):
        res = super(CRM, self).create(vals)
        if res.type == 'opportunity':
            res.stage_id = self.env.ref('crm_base.crm_stage_not_confirm').id
            res.name = self.env['ir.sequence'].next_by_code('crm.lead')

            if res.partner_id:
                res.partner_id.name = res.contact_name
                res.partner_id.gender = res.gender
                res.partner_id.birth_date = res.birth_date
                res.partner_id.year_of_birth = res.year_of_birth
                res.partner_id.country_id = res.country_id.id
                res.partner_id.state_id = res.state_id.id
                res.partner_id.street = res.street
        return res

    def select_service(self):
        return {
            'name': 'Lựa chọn dịch vụ',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('crm_base.view_form_crm_select_service').id,
            'res_model': 'crm.select.service',
            'context': {
                'default_partner_id': self.partner_id.id,
                'default_booking_id': self.id,
            },
            'target': 'new',
        }

    # @api.constrains('phone')
    # def constraint_phone(self):
    #     for rec in self:
    #         if rec.phone and rec.phone.isdigit() is False:
    #             raise ValidationError(_('Wrong phone number format'))

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(CRM, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        stage_lead_bk = self.env.ref('crm_base.crm_stage_booking').id
        stage_lead_re_open = self.env.ref('crm_base.crm_stage_re_open').id
        stage_bk_paid = self.env.ref('crm_base.crm_stage_paid').id
        stage_bk_won = self.env.ref('crm.stage_lead4').id
        stage_bk_confirm = self.env.ref('crm_base.crm_stage_confirm').id
        stage_bk_not_confirm = self.env.ref('crm_base.crm_stage_not_confirm').id
        view_lead = self.env.ref('crm_base.form_crm_lead')
        view_booking = self.env.ref('crm_base.crm_lead_form_booking')

        if view_type == 'form' and view_id == view_lead.id:
            for node in doc.xpath("//field"):
                node.set("attrs",
                         "{'readonly':[('stage_id','=',%s)]}" % stage_lead_bk)
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = "[('stage_id','=',%s)]" % stage_lead_bk
                node.set('modifiers', json.dumps(modifiers))

            for node in doc.xpath("//field[@name='user_id']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='lead_insight']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='assign_time']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='crm_line_ids']"):
                node.set("attrs", "{'readonly':[('check_booking','=',True)]}")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = "[('check_booking','=',True)]"
                node.set('modifiers', json.dumps(modifiers))

            for node in doc.xpath("//field[@name='stage_id']"):
                node.set("attrs", "{'readonly':[('check_booking','=',True)]}")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = "[('check_booking','=',True)]"
                node.set('modifiers', json.dumps(modifiers))

            for node in doc.xpath("//field[@name='brand_id']"):
                node.set("attrs", "{'readonly':[('check_booking','=',True)]}")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = "[('check_booking','=',True)]"
                node.set('modifiers', json.dumps(modifiers))

            for node in doc.xpath("//field[@name='company_id']"):
                node.set("attrs", "{'readonly':[('check_booking','=',True)]}")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = "[('check_booking','=',True)]"
                node.set('modifiers', json.dumps(modifiers))

            for node in doc.xpath("//field[@name='department_id']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='price_list_id']"):
                node.set("attrs", "{'readonly':[('check_booking','=',True)]}")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = "[('check_booking','=',True)]"
                node.set('modifiers', json.dumps(modifiers))

            for node in doc.xpath("//field[@name='currency_id']"):
                node.set("attrs", "{'readonly':[('check_booking','=',True)]}")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = "[('check_booking','=',True)]"
                node.set('modifiers', json.dumps(modifiers))

            for node in doc.xpath("//field[@name='source_id']"):
                node.set("attrs", "{'readonly':[('check_booking','=',True)]}")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = "[('check_booking','=',True)]"
                node.set('modifiers', json.dumps(modifiers))

            for node in doc.xpath("//field[@name='category_source_id']"):
                node.set("attrs",
                         "{'readonly':['|',('check_booking','=',True),('type_data','=','old'),"
                         "('phone','!=',False),('category_source_id','!=',False)]}")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = "['|',('check_booking','=',True),('type_data','=','old')," \
                                        "('phone','!=',False),('category_source_id','!=',False)]"
                node.set('modifiers', json.dumps(modifiers))

            for node in doc.xpath("//field[@name='category_source_id']"):
                node.set("force_save", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['force_save'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='campaign_id']"):
                node.set("attrs", "{'readonly':[('check_booking','=',True)]}")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = "[('check_booking','=',True)]"
                node.set('modifiers', json.dumps(modifiers))

            for node in doc.xpath("//field[@name='medium_id']"):
                node.set("attrs", "{'readonly':[('check_booking','=',True)]}")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = "[('check_booking','=',True)]"
                node.set('modifiers', json.dumps(modifiers))

            for node in doc.xpath("//field[@name='currency_id']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='create_by']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='create_on']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='write_date']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='write_uid']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='name']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='type_data']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='type_data']"):
                node.set("force_save", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['force_save'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='partner_id']"):
                node.set("force_save", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['force_save'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='code_customer']"):
                node.set("force_save", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['force_save'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='source_id']"):
                node.set("force_save", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['force_save'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='partner_id']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='code_customer']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='type_brand']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

        if view_type == 'form' and view_id == view_booking.id:
            for node in doc.xpath("//field"):
                node.set("attrs",
                         "{'readonly':[('stage_id','not in',[%s,%s])]}" % (stage_bk_confirm, stage_bk_not_confirm))
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = "[('stage_id','not in',[%s,%s])]" % (stage_bk_confirm, stage_bk_not_confirm)
                node.set('modifiers', json.dumps(modifiers))

            for node in doc.xpath("//field[@name='price_list_id']"):
                node.set("attrs",
                         "{'readonly':[('stage_id','not in',[%s,%s]),'|',('type_crm_id','=',%s)]}" %
                         (stage_bk_not_confirm, stage_bk_confirm, self.env.ref('crm_base.type_oppor_guarantee').id))
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = "[('stage_id','not in',[%s,%s]),'|',('type_crm_id','=',%s)]" % (
                    stage_bk_not_confirm, stage_bk_confirm, self.env.ref('crm_base.type_oppor_guarantee').id)
                node.set('modifiers', json.dumps(modifiers))

            for node in doc.xpath("//field[@name='type_crm_id']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            if self.env.ref('crm_base.receptionist_crm') not in self.env.user.groups_id:
                for node in doc.xpath("//field[@name='customer_come']"):
                    node.set("readonly", "True")
                    modifiers = json.loads(node.get("modifiers"))
                    modifiers['readonly'] = True
                    node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='type_data']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='type_data']"):
                node.set("force_save", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['force_save'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='type_brand']"):
                node.set("force_save", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['force_save'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='brand_id']"):
                node.set("force_save", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['force_save'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='arrival_date']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='arrival_date']"):
                node.set("force_save", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['force_save'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='type_crm_id']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='name']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='code_customer']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='crm_line_ids']"):
                node.set("readonly", "False")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = False
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='department_id']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='discount_review_ids']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='brand_id']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='partner_id']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='write_uid']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='write_date']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='create_on']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='create_by']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='amount_total']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='amount_paid']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='amount_used']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='amount_remain']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='currency_id']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='reason_cancel']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='lead_id']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='type_brand']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='contact_name']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='phone']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='gender']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='country_id']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='state_id']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='street']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='birth_date']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='year_of_birth']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='mobile']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='pass_port']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='email_from']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='facebook_acc']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='category_source_id']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='category_source_id']"):
                node.set("force_save", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['force_save'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='source_id']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//field[@name='company_id']"):
                node.set("attrs",
                         "{'readonly':[('company_id','not in',%s),'|',"
                         "('stage_id','not in',[%s,%s])]}" % (self.env.user.company_ids.ids, stage_bk_confirm,
                                                              stage_bk_not_confirm))
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = "[('stage_id','not in',[%s,%s]),'|',('company_id','not in',%s)]" % (
                    stage_bk_confirm, stage_bk_not_confirm, self.env.user.company_ids.ids)
                node.set('modifiers', json.dumps(modifiers))

            for node in doc.xpath("//field[@name='company2_id']"):
                node.set("attrs",
                         "{'readonly':[('stage_id','not in',[%s,%s]),'|',('company_id','not in',%s)]}" %
                         (self.env.user.company_ids.ids, stage_bk_confirm, stage_bk_not_confirm))
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = "[('stage_id','not in',[%s,%s]),'|',('company_id','not in',%s)]" % \
                                        (stage_bk_confirm, stage_bk_not_confirm, self.env.user.company_ids.ids)
                node.set('modifiers', json.dumps(modifiers))

        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res

    @api.depends('payment_ids.state', 'payment_ids.payment_type', 'payment_ids.amount')
    def set_paid_booking(self):
        for rec in self:
            paid = 0
            if rec.payment_ids:
                for pm in rec.payment_ids:
                    if pm.state in ['posted', 'reconciled']:
                        if pm.payment_type == 'inbound':
                            paid += pm.amount_vnd
                        elif pm.payment_type == 'outbound':
                            paid -= pm.amount_vnd
            rec.amount_paid = paid

    @api.depends('order_ids.amount_total', 'order_ids.set_total', 'order_ids.state')
    def set_used_booking(self):
        for rec in self:
            used = 0
            if rec.order_ids:
                for record in rec.order_ids:
                    if record.state in ['sale', 'done']:
                        if record.set_total > 0:
                            used += record.set_total
                        else:
                            used += record.amount_total
            rec.amount_used = used

    @api.depends('crm_line_ids.total', 'crm_line_ids.stage')
    def set_total(self):
        for rec in self:
            rec.amount_total = 0
            if rec.crm_line_ids:
                for i in rec.crm_line_ids:
                    if i.stage != 'cancel':
                        rec.amount_total += i.total
                    elif i.stage == 'cancel':
                        rec.amount_total += i.unit_price * i.uom_price * i.number_used

    @api.depends('amount_paid', 'amount_used')
    def set_amount_remain(self):
        for rec in self:
            rec.amount_remain = rec.amount_paid - rec.amount_used

    def action_view_payment_booking(self):
        action = self.env.ref('account.action_account_payments').read()[0]
        action['context'] = {
            'default_partner_id': self.partner_id.id,
            'default_crm_id': self.id,
        }
        action['domain'] = [('crm_id', '=', self.id), ('state', 'in', ('posted', 'reconciled'))]
        return action

    def action_view_sale_order(self):
        action = self.env.ref('sale.action_orders').read()[0]
        action['context'] = {
            'default_partner_id': self.partner_id.id,
            'default_booking_id': self.id,
        }
        action['domain'] = [('booking_id', '=', self.id), ('state', 'not in', ('draft', 'sent', 'cancel'))]
        return action
