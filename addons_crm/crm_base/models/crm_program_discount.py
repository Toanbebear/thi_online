from odoo import fields, api, models, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError
from datetime import datetime, date
from odoo.tools import pycompat
import random
import json
from lxml import etree
from calendar import monthrange

try:
    import qrcode
except ImportError:
    qrcode = None
try:
    import base64
except ImportError:
    base64 = None
from io import BytesIO
from datetime import datetime


class CRMDiscountProgram(models.Model):
    _name = 'crm.discount.program'

    name = fields.Char('Name')
    code = fields.Char('Code')
    start_date = fields.Datetime('Start date')
    end_date = fields.Datetime('End date')
    stage_prg = fields.Selection([('new', 'New'), ('active', 'Active'), ('expire', 'Expire')], string='Stage',
                                 compute='set_stage_prg', default='new', store=True)
    active = fields.Boolean('Active', default=True)
    type_service = fields.Selection([('product', 'Product'), ('category', 'Category')], string='Type service')
    brand_id = fields.Many2one('res.brand', string='Brand',
                               domain=lambda self: [('id', 'in', self.env.user.company_ids.mapped('brand_id').ids)])
    company_ids = fields.Many2many('res.company', string='Branch', domain="[('brand_id','=',brand_id)]")
    campaign_id = fields.Many2one('utm.campaign', string='Campaign', domain="[('brand_id','=',brand_id)]")
    discount_program_rule = fields.One2many('crm.discount.program.rule', 'discount_program', string='List discount')
    doc_attachment_id = fields.Many2many('ir.attachment', 'discount_program_attach_rel', 'discount_program_id',
                                         'attach_id', string="Tệp đính kèm",
                                         help='You can attach the copy of your document', copy=False)

    # thẻ thành viên đc áp dụng cùng
    loyalty_active = fields.Boolean('Loyalty active')

    #CTKM cộng dồn
    related_discounts_program_ids = fields.Many2many('crm.discount.program', 'crm_discount_program_to_discount_program',
                                                     'discount_program', 'discount_program_related',
                                                     string='Related discount program',
                                                     domain="[('brand_id','=',brand_id)]")

    def write(self, vals):
        res = super(CRMDiscountProgram, self).write(vals)
        for record in self:
            if vals.get('related_discounts_program_ids') and (
                    record.id not in record.related_discounts_program_ids.related_discounts_program_ids.ids):
                record.related_discounts_program_ids.write({'related_discounts_program_ids': [(4, record.id)]})
        return res

    @api.model
    def create(self, vals_list):
        if vals_list.get('related_discounts_program_ids'):
            res = super(CRMDiscountProgram, self).create(vals_list)
            res.related_discounts_program_ids.write({'related_discounts_program_ids': [(4, res.id)]})
        else:
            res = super(CRMDiscountProgram, self).create(vals_list)
        company_code = []
        if res.company_ids:
            for company in res.company_ids:
                company_code.append(company.code)
        else:
            company_code.append('ALL')
        start_date = date(res.start_date.year, res.start_date.month, 1)
        end_date = date(res.start_date.year, res.start_date.month,
                        monthrange(res.start_date.year, res.start_date.month)[1])
        res.code = 'CTKM_' + res.brand_id.code + '_' + '.'.join(company_code) + '_' + str(res.start_date.year) + str(
            res.start_date.month) + '_' + str(self.env['crm.discount.program'].search_count(
            [('brand_id', '=', res.brand_id.id), ('start_date', '>=', start_date), ('start_date', '<=', end_date)]))
        return res

    @api.onchange('type_service')
    def change_by_type_service(self):
        if self.type_service == 'product':
            self.product_ctg_ids = False
        elif self.type_service == 'category':
            self.product_ids = False

    @api.constrains('start_date', 'end_date')
    def error_date(self):
        for rec in self:
            if rec.end_date and rec.start_date and rec.start_date > rec.end_date:
                raise ValidationError(_('Start date cannot be greater than end date'))

    @api.constrains('discount')
    def error_discount_percent(self):
        for rec in self:
            if rec.discount and rec.discount > 100:
                raise ValidationError(_('Can not discount over 100 percent'))
            elif rec.discount and rec.discount < 0:
                raise ValidationError(_('There is no negative discount'))

    @api.depends('start_date', 'end_date')
    def set_stage_prg(self):
        for rec in self:
            rec.stage_prg = 'new'
            if rec.start_date and rec.end_date and rec.id:
                if rec.end_date >= fields.Datetime.now() >= rec.start_date:
                    rec.stage_prg = 'active'
                elif rec.start_date > fields.Datetime.now():
                    rec.stage_prg = 'new'
                elif rec.end_date < fields.Datetime.now():
                    rec.stage_prg = 'expire'

    def unlink(self):
        for rec in self:
            if rec.stage_prg != 'new':
                raise ValidationError('Bạn không thể xóa các chương trình đang không có trạng thái là mới !!!')
            return super(CRMDiscountProgram, self).unlink()

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(CRMDiscountProgram, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                              submenu=submenu)
        doc = etree.XML(res['arch'])
        if view_type == 'form':
            for node in doc.xpath("//field"):
                node.set("attrs",
                         "{'readonly':[('stage_prg','=','active')]}")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = "[('stage_prg','=','active')]"
                node.set('modifiers', json.dumps(modifiers))

        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res


class CRMPromotionProgramRule(models.Model):
    _name = 'crm.discount.program.rule'
    _description = 'CRM Promotion Program Rule'

    type = fields.Selection([('independent_service', 'Independent service'), ('affiliate_service', 'Affiliate service')]
                            , string='Type rule')
    type_discount = fields.Selection([('percent', 'Percent'), ('cash', 'Cash'), ('sale_to', 'Sale to')],
                                     string='Type Discount', default='percent')
    # product_ids = fields.Many2many('product.product', 'product_promotion_program_ref', 'program_id', 'product',
    #                                string='List product',
    #                                domain="[('type_product_crm','in',('service_crm', 'course'))]")
    product_id = fields.Many2one('product.product', string='Product',
                                 domain="[('type_product_crm','in',('service_crm', 'course'))]")
    # product_ctg_ids = fields.Many2many('product.category', 'ctg_promotion_program_ref', 'program_id', 'ctg',
    #                                    string='List category')
    discount = fields.Float('Discount')
    discount_program = fields.Many2one('crm.discount.program', string='Discount Program')


class CRMProgramVoucher(models.Model):
    _name = 'crm.voucher.program'

    _sql_constraints = [
        ('name_prefix', 'unique(prefix)', "Tiền tố này đã tồn tại"),
    ]

    name = fields.Char('Name')
    start_date = fields.Datetime('Start date')
    end_date = fields.Datetime('End date')
    product_id = fields.Many2one('product.product', string='Product',
                                 domain="[('type_product_crm','in',('service_crm', 'course'))]")
    price = fields.Float('Fix price', digits=(3, 0))
    product_ids = fields.Many2many('product.product', 'product_voucher_program_ref', 'program_voucher_id',
                                   'product', string='List product',
                                   domain="[('type_product_crm','in',('service_crm', 'course'))]")
    product_ctg_ids = fields.Many2many('product.category', 'ctg_program_voucher_ref', 'program_voucher_id', 'ctg',
                                       string='List category')
    type_voucher = fields.Selection([('fix', 'Fix price'), ('dis', 'Discount')], string='Type voucher', default=False)
    discount = fields.Float('Discount(%)')
    prefix = fields.Char('Prefix')
    quantity = fields.Integer('Quantity', default=1)
    stage_prg_voucher = fields.Selection([('new', 'New'), ('active', 'Active'), ('expire', 'Expire')], string='Stage',
                                         compute='set_stage', default='new')
    active = fields.Boolean('Active', default=True)
    sequence_id = fields.Many2one('ir.sequence', string='Sequence voucher')
    type_service = fields.Selection([('product', 'Product'), ('category', 'Category')], string='Type service')
    brand_id = fields.Many2one('res.brand', string='Brand', default=lambda self: self.env.company.brand_id)
    company_id = fields.Many2many('res.company', string='Branch',
                                  domain="[('brand_id','=',brand_id)]")
    current_number_voucher = fields.Integer('Current number voucher', compute='get_number_voucher')
    loyalty_active = fields.Boolean('Loyalty active')
    campaign_id = fields.Many2one('utm.campaign', string='Campaign')

    def unlink(self):
        for rec in self:
            if rec.stage_prg_voucher != 'new':
                raise ValidationError('Bạn không thể xóa các chương trình đang không có trạng thái là mới !!!')
            return super(CRMProgramVoucher, self).unlink()

    @api.depends('sequence_id')
    def get_number_voucher(self):
        for rec in self:
            rec.current_number_voucher = 0
            if rec.sequence_id:
                rec.current_number_voucher = rec.sequence_id.number_next_actual - 1

    @api.constrains('quantity')
    def limit_quantity(self):
        for rec in self:
            if rec.quantity > 1000:
                raise ValidationError(_('The maximum amount of creation in 1 time is 1000'))

    @api.constrains('price')
    def validate_fix_price(self):
        for rec in self:
            if rec.price < 0:
                raise ValidationError(_('The Price Correction field must be greater than 0'))

    @api.onchange('type_service')
    def change_by_type_service(self):
        if self.type_service == 'product':
            self.product_ctg_ids = False
        elif self.type_service == 'category':
            self.product_ids = False

    @api.depends('start_date', 'end_date')
    def set_stage(self):
        for rec in self:
            rec.stage_prg_voucher = 'new'
            if rec.start_date and rec.end_date and rec.id:
                if rec.start_date > fields.Datetime.now():
                    rec.stage_prg_voucher = 'new'
                elif rec.end_date >= fields.Datetime.now() >= rec.start_date:
                    rec.stage_prg_voucher = 'active'
                elif rec.end_date < fields.Datetime.now():
                    rec.stage_prg_voucher = 'expire'

    def write(self, vals):
        res = super(CRMProgramVoucher, self).write(vals)
        for rec in self:
            if vals.get('prefix') and rec.sequence_id:
                rec.sequence_id.prefix = vals.get('prefix')
        return res

    def check_sequence(self):
        if not self.sequence_id:
            sequence = self.env['ir.sequence'].create({
                'code': 'crm.voucher',
                'name': 'SEQ code voucher %s' % self.name,
                'prefix': self.prefix,
                'padding': 6,
                'company_id': self.env.user.company_id.id,
            })
            self.sequence_id = sequence.id
            self.create_vouchers(sequence)
        else:
            self.create_vouchers(self.sequence_id)
        view = self.env.ref('sh_message.sh_message_wizard')
        view_id = view and view.id or False
        context = dict(self._context or {})
        context['message'] = 'Voucher đã được tạo thành công!!'
        return {
            'name': 'Success',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sh.message.wizard',
            'views': [(view_id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context,
        }

    def create_vouchers(self, sequence):
        if self.quantity:
            for n in range(0, self.quantity):
                self.env['crm.voucher'].create(
                    {'voucher_program_id': self.id,
                     'name': sequence._next(),
                     'stage_voucher': 'new'
                     }
                )

    @api.constrains('discount')
    def error_discount_percent(self):
        for rec in self:
            if rec.discount and rec.discount > 100:
                raise ValidationError(_('Can not discount over 100 percent'))
            elif rec.discount and rec.discount < 0:
                raise ValidationError(_('There is no negative discount'))

    @api.constrains('start_date', 'end_date')
    def error_date(self):
        for rec in self:
            if rec.end_date and rec.start_date and rec.start_date > rec.end_date:
                raise ValidationError(_('Start date cannot be greater than end date'))


class CRMVoucher(models.Model):
    _name = 'crm.voucher'

    name = fields.Char('Code')
    voucher_program_id = fields.Many2one('crm.voucher.program', string='Voucher program')
    partner_id = fields.Many2one('res.partner', string='Owner')
    partner2_id = fields.Many2one('res.partner', string='Customer used')
    qr_code = fields.Image('QR code', compute='generate_qr', store=True)
    start_date = fields.Datetime('Start date', related='voucher_program_id.start_date')
    end_date = fields.Datetime('End date', related='voucher_program_id.end_date')
    stage_voucher = fields.Selection([('new', 'New'), ('active', 'Active'), ('used', 'Used'), ('expire', 'Expire')],
                                     string='Stage', compute='set_stage', store=True)
    active = fields.Boolean('Active', default=True)
    crm_id = fields.Many2one('crm.lead', string='Lead/booking')
    order_id = fields.Many2one('sale.order', string='Sale order')
    brand_id = fields.Many2one('res.brand', string='Brand', related='voucher_program_id.brand_id')

    @api.model
    def update_stage_voucher(self):
        self.env.cr.execute(""" UPDATE crm_voucher
                                SET stage_voucher = 'expire'
                                FROM crm_voucher_program
                                WHERE crm_voucher_program.id = crm_voucher.voucher_program_id 
                                    and crm_voucher.stage_voucher NOT IN ('used', 'expire') 
                                    and crm_voucher_program.end_date < (now() at time zone 'utc');""")

        # Trong trường hợp voucher ở trạng thái new
        # self.env.cr.execute(""" UPDATE crm_voucher
        #                         SET stage_voucher = 'active'
        #                         FROM crm_voucher_program
        #                         WHERE crm_voucher_program.id = crm_voucher.voucher_program_id
        #                             and crm_voucher.stage_voucher = 'new'
        #                             and ((now() at time zone 'utc')
        #                                 BETWEEN crm_voucher_program.start_date AND crm_voucher_program.end_date) ;""")

    @api.depends('name')
    def generate_qr(self):
        for rec in self:
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
                rec.qr_code = qr_image

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(CRMVoucher, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                      submenu=submenu)
        doc = etree.XML(res['arch'])

        if view_type == 'form':
            for node in doc.xpath("//field"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))

        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
