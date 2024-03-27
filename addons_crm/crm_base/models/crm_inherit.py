from odoo import fields, api, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import logging
import json
from lxml import etree
import odoorpc
from odoo.http import request

_logger = logging.getLogger(__name__)


def num2words_vnm(num):
    under_20 = ['không', 'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín', 'mười', 'mười một',
                'mười hai', 'mười ba', 'mười bốn', 'mười lăm', 'mười sáu', 'mười bảy', 'mười tám', 'mười chín']
    tens = ['hai mươi', 'ba mươi', 'bốn mươi', 'năm mươi', 'sáu mươi', 'bảy mươi', 'tám mươi', 'chín mươi']
    above_100 = {100: 'trăm', 1000: 'nghìn', 1000000: 'triệu', 1000000000: 'tỉ'}

    if num < 20:
        return under_20[num]

    elif num < 100:
        under_20[1], under_20[5] = 'mốt', 'lăm'  # thay cho một, năm
        result = tens[num // 10 - 2]
        if num % 10 > 0:  # nếu num chia 10 có số dư > 0 mới thêm ' ' và số đơn vị
            result += ' ' + under_20[num % 10]
        return result

    else:
        unit = max([key for key in above_100.keys() if key <= num])
        result = num2words_vnm(num // unit) + ' ' + above_100[unit]
        if num % unit != 0:
            if num > 1000 and num % unit < unit / 10:
                result += ' không trăm'
            if 1 < num % unit < 10:
                result += ' linh'
            result += ' ' + num2words_vnm(num % unit)
    return result.capitalize()


class CrmStage(models.Model):
    _inherit = 'crm.stage'

    crm_type_id = fields.Many2many('crm.type', 'stage_type_crm_ref', 'stage', 'type_crm', string='Type crm')
    crm_stage_insight_id = fields.Integer('Insight stage id')


class UtmCampaign(models.Model):
    _inherit = 'utm.campaign'

    brand_id = fields.Many2one('res.brand', string='Brand')


class ResCompany(models.Model):
    _inherit = 'res.company'

    brand_id = fields.Many2one('res.brand', string='Brand')
    brand_ids = fields.Many2many('res.brand', string='Brands')

    @api.onchange('brand_id')
    def set_brand_ids(self):
        if self.brand_id:
            self.brand_ids = [(4, self.brand_id.id)]


class PriceList(models.Model):
    _inherit = 'product.pricelist'

    brand_id = fields.Many2one('res.brand', string='Brand')
    start_date = fields.Date('Start date')
    end_date = fields.Date('End date')
    type = fields.Selection([('service', 'Service'), ('guarantee', 'Guarantee'), ('product', 'Product')],
                            string='Type price list',
                            default='service')


class CrmPayment(models.Model):
    _inherit = 'account.payment'

    crm_id = fields.Many2one('crm.lead', string='Booking/lead',
                             domain="[('partner_id','=',partner_id), ('type', '=', 'opportunity')]")
    brand_id = fields.Many2one('res.brand', string='Brand', related='company_id.brand_id', store=True)
    # company2_id = fields.Many2one('res.company', string='Company shared')
    currency_rate_id = fields.Many2one('res.currency.rate', string='Currency rate',
                                       domain="[('currency_id','=',currency_id)]")
    amount_vnd = fields.Float('Amount vnd', compute='set_amount_vnd', store=True, digits=(3, 0))
    payment_method = fields.Selection(
        [('tm', 'Tiền mặt'), ('ck', 'Chuyển khoản'), ('nb', 'Thanh toán nội bộ'), ('pos', 'Quẹt thẻ qua POS'),
         ('vdt', 'Thanh toán qua ví điện tử')], string='Payment method')

    @api.constrains('amount_vnd')
    def check_refund(self):
        for rec in self:
            if rec.payment_type == 'outbound' and rec.amount_vnd and rec.crm_id and \
                    rec.amount_vnd > rec.crm_id.amount_remain:
                raise ValidationError(_('The refund amount larger than the existing customer amount'))

    @api.onchange('currency_id')
    def back_value(self):
        self.currency_rate_id = False
        # quy đổi tiền về tiền việt
        self.text_total = num2words_vnm(round(self.amount_vnd)) + " đồng"

    @api.depends('currency_rate_id', 'amount', 'currency_id')
    def set_amount_vnd(self):
        for rec in self:
            rec.amount_vnd = 0
            if rec.amount:
                if rec.currency_id and rec.currency_id == self.env.ref('base.VND'):
                    rec.amount_vnd = rec.amount * 1
                elif rec.currency_rate_id and rec.currency_id != self.env.ref('base.VND'):
                    rec.amount_vnd = rec.amount / rec.currency_rate_id.rate

                # quy đổi tiền về tiền việt
                rec.text_total = num2words_vnm(round(rec.amount_vnd)) + " đồng"

    # overwrite lại hàm thay đổi tiền
    @api.onchange('amount')
    def onchange_amount(self):
        if self.amount and self.amount > 0:
            # neu currency là VND
            if self.currency_id == self.env.ref('base.VND'):
                self.text_total = num2words_vnm(round(self.amount)) + " đồng"
            # neu currency khác
            else:
                self.text_total = num2words_vnm(round(self.amount_vnd)) + " đồng"
        elif self.amount and self.amount < 0:
            raise ValidationError(
                _('Số tiền thanh toán không hợp lệ!'))
        else:
            self.text_total = "Không đồng"

    @api.onchange('crm_id')
    def set_partner(self):
        for rec in self:
            if rec.crm_id and rec.state == 'draft':
                rec.partner_id = rec.crm_id.partner_id.id

    def post(self):
        res = super(CrmPayment, self).post()
        if self.crm_id and self.crm_id.stage_id != self.env.ref('crm.stage_lead4'):
            self.crm_id.stage_id = self.env.ref('crm_base.crm_stage_paid').id
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(CrmPayment, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                      submenu=submenu)
        doc = etree.XML(res['arch'])

        VND = self.env.ref('base.VND').id

        if view_type == 'form':
            for node in doc.xpath("//field[@name='currency_rate_id']"):
                node.set("attrs", "{'required':[('currency_id','!=',%s)]}" % VND)
                modifiers = json.loads(node.get("modifiers"))
                modifiers['required'] = "[('currency_id','!=',%s)]" % VND
                node.set('modifiers', json.dumps(modifiers))

        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    crm_line_id = fields.Many2one('crm.line', string='Crm line')
    brand_id = fields.Many2one('res.brand', string='Brand', related='company_id.brand_id', store=True)
    amount_remain = fields.Monetary('Amount remain', related='booking_id.amount_remain')
    document_related = fields.Char('Document related')
    booking_id = fields.Many2one('crm.lead', string='Booking', domain="[('type','=','opportunity')]")
    set_total = fields.Monetary('Set amount used')
    debt_review = fields.Boolean('Debt review')

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if self.booking_id:
            self.booking_id.stage_id = self.env.ref('crm.stage_lead4').id
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    crm_line_id = fields.Many2one('crm.line', string='Crm line')
    discount_cash = fields.Monetary('Discount cash')
    uom_price = fields.Float('cm2/cc/unit/...', default=1)

    @api.constrains('price_unit')
    def error_discount_cash(self):
        for rec in self:
            if rec.discount_cash > rec.price_unit * (1 - (rec.discount or 0.0) / 100.0) or rec.discount_cash < 0:
                raise ValidationError(_('Invalid discount'))

    @api.depends('product_uom_qty', 'discount', 'discount_cash', 'price_unit', 'tax_id', 'uom_price')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0) - line.discount_cash
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id)
            total = line.price_unit * line.product_uom_qty * line.uom_price * (
                    1 - (line.discount or 0.0) / 100.0) - line.discount_cash
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': total,
                'price_subtotal': total,
            })

    def _prepare_invoice_line(self):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        """
        self.ensure_one()

        # check giá phải > 0 thì mới tính discount
        if self.price_unit > 0:
            discount = 100 - self.price_subtotal / self.price_unit * 100
        else:
            discount = 0

        return {
            'display_type': self.display_type,
            'sequence': self.sequence,
            'name': self.name,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'discount': discount,
            'price_unit': self.price_unit,
            'tax_ids': [(6, 0, self.tax_id.ids)],
            'analytic_account_id': self.order_id.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'sale_line_ids': [(4, self.id)],
        }


class Product(models.Model):
    _inherit = 'product.product'

    type_product_crm = fields.Selection([('course', 'Course'), ('service_crm', 'Service'), ('product', 'Product')],
                                        string='Type Product crm')


class TypeSource(models.Model):
    _name = 'type.source'

    name = fields.Char('Name')
    code = fields.Char('Code')
    active = fields.Boolean('Active', default=True)


class CategorySource(models.Model):
    _name = 'crm.category.source'

    name = fields.Char('Name')
    code = fields.Char('Code')

    _sql_constraints = [
        ('code_category_source_uniq', 'unique(code)', 'This code already exists!')
    ]


class TagSource(models.Model):
    _name = 'crm.tag.source'
    name = fields.Char('Name')
    code = fields.Integer('Code tag source')

    # đồng bộ source mkt
    @api.model
    def sync_source_mkt(self):
        tags = self.env['crm.tag.source'].search([]).mapped('code')

        sync = self.env.ref('crm_base.sync_insight')
        odoo = odoorpc.ODOO(host=sync.ip, port=sync.port)
        odoo.login(sync.database, sync.user, sync.password)
        source_mkt = odoo.env['source.mkt'].search_read(domain=[('id', 'not in', tags)], fields=['name'])
        for sr in source_mkt:
            self.env['crm.tag.source'].create({
                'name': sr['name'],
                'code': sr['id'],
            })


class UtmSource(models.Model):
    _inherit = 'utm.source'

    type_source_id = fields.Many2one('type.source', string='Type source')
    active = fields.Boolean('Active', default=True)
    code = fields.Char('Code')
    category_id = fields.Many2one('crm.category.source', string='Category source')
    utm_source_ins_id = fields.Integer('Insight source')
    tag_ids = fields.Many2many('crm.tag.source', string='Tags source')
    # gắn source mkt vs nguồn trên crm

    _sql_constraints = [
        ('code_source_uniq', 'unique(code)', 'This code already exists!')
    ]


class PriceUnitItem(models.Model):
    _inherit = 'product.pricelist.item'

    price_currency_usd = fields.Float('Unit price usd')
    rate_currency_id = fields.Many2one('res.currency.rate', string='Rate currency')

    @api.onchange('rate_currency_id', 'price_currency_usd')
    def set_fix_price(self):
        self.fixed_price = 0
        if self.rate_currency_id:
            self.fixed_price = self.price_currency_usd / self.rate_currency_id.rate

    @api.model
    def cron_set_rate(self, list_item=[]):
        if list_item:
            items = self.env['product.pricelist.item'].search(
                [('price_currency_usd', '>', 0), ('id', 'not in', list_item)], limit=200).ids
            if items:
                list_item += items
            else:
                list_item = []
                self.env.ref('crm_base.set_rate').nextcall = (fields.Datetime.now() + timedelta(days=1)).replace(
                    hour=9,
                    minute=0,
                    second=0)

        else:
            items = self.env['product.pricelist.item'].search([('price_currency_usd', '>', 0)], limit=200).ids
            if items:
                list_item += items
                self.env.ref('crm_base.set_rate').nextcall = fields.Datetime.now() + timedelta(minutes=10)
            else:
                self.env.ref('crm_base.set_rate').nextcall = (fields.Datetime.now() + timedelta(days=1)).replace(
                    hour=9,
                    minute=0,
                    second=0)

        self.env.ref('crm_base.set_rate').code = 'model.cron_set_rate(%s)' % (list_item)
        rate = self.env['res.currency.rate'].search([('currency_id', '=', self.env.ref("base.USD").id)])[0]

        if items:
            for item in items:
                self.env['product.pricelist.item'].browse(item).rate_currency_id = rate.id
                self.env['product.pricelist.item'].browse(item).set_fix_price()


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    discount_cash = fields.Monetary('Discount cash')


class GuaranteeCustomer(models.Model):
    _inherit = 'res.partner'

    def booking_guarantee(self):
        return {
            'name': 'Booking bảo hành',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('crm_base.view_form_create_booking_guarantee').id,
            'res_model': 'crm.create.guarantee',
            'context': {
                'default_partner_id': self.id,
                'default_brand_id': self.env.company.brand_id.id,
            },
            'target': 'new',
        }
