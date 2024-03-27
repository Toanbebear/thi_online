from odoo import fields, api, models, _
from odoo.exceptions import ValidationError


class CrmLine(models.Model):
    _name = 'crm.line'
    _rec_name = 'product_id'

    # them truong company shared va chuyen exam room thanh many2many

    name = fields.Char('Name')
    quantity = fields.Integer('Quantity', default=1)
    number_used = fields.Integer('Number used', compute='set_number_used', store=True)
    unit_price = fields.Monetary('Unit price')
    discount_percent = fields.Float('Discount(%)', store=True)
    type = fields.Selection([('consu', 'Consumable'), ('service', 'Service'), ('product', 'Storable Product')],
                            string='type')
    discount_cash = fields.Monetary('Discount cash')
    price_list_id = fields.Many2one('product.pricelist', string='Price list')
    currency_id = fields.Many2one('res.currency', string='Currency', related='price_list_id.currency_id', store=True)
    total_before_discount = fields.Monetary('Total before discount', compute='get_total_line', store=True)
    total_discount = fields.Monetary('Tổng tiền đã giảm', compute='get_total_line', store=True)
    total = fields.Monetary('Total', compute='get_total_line', store=True)
    crm_id = fields.Many2one('crm.lead', string='CRM')
    company_id = fields.Many2one('res.company', string='Company')
    company_shared = fields.Many2many('res.company', 'line_company_shared2_ref', 'company2s', 'line2s',
                                      string='Company shared', related='crm_id.company2_id')
    product_id = fields.Many2one('product.product', string='Product')
    product_ctg_id = fields.Many2one('product.category', string='Category product', related='product_id.categ_id',
                                     store=True)
    order_id = fields.One2many('sale.order', 'crm_line_id', string='Order')
    sale_order_line_id = fields.One2many('sale.order.line', 'crm_line_id', 'sale order line')
    stage = fields.Selection(
        [('new', 'Allow to use'), ('processing', 'Processing'), ('done', 'Done'), ('waiting', 'Awaiting approval'),
         ('cancel', 'Cancel')],
        string='Stage',
        compute='set_stage', store=True)
    cancel = fields.Boolean('Cancel')
    type_brand = fields.Selection([('hospital', 'Hospital'), ('academy', 'Academy')], string='Type',
                                  related='crm_id.type_brand', store=True)
    history_discount_ids = fields.One2many('history.discount', 'crm_line_id', string='History discount')
    source_extend_id = fields.Many2one('utm.source', string='Extended source')
    uom_price = fields.Float('Đơn vị xử lý', default=1)
    discount_review_id = fields.Many2one('crm.discount.review', string='Discount review')
    voucher_id = fields.Many2one('crm.voucher', string='Voucher')
    prg_ids = fields.Many2many('crm.discount.program', 'line_prg_ref', 'prg', 'line', string='Discount program')
    prg_voucher_ids = fields.Many2many('crm.voucher.program', 'line_voucher_ref', 'voucher', 'line',
                                       string='Voucher program')
    color = fields.Integer('Color')
    line_special = fields.Boolean('Line special')


    def name_get(self):
        res = []
        for crm_line in self:
            if crm_line.voucher_id.voucher_program_id.type_voucher == 'fix':
                res.append((crm_line.id, _('[%s] %s - %s ') % (
                crm_line.product_id.default_code, crm_line.product_id.name, crm_line.voucher_id.voucher_program_id.price)))
            else:
                res.append((crm_line.id, _('[%s] %s') % (
                crm_line.product_id.default_code, crm_line.product_id.name)))
        return res

    @api.depends('sale_order_line_id.state', 'number_used', 'quantity', 'cancel', 'discount_review_id.stage_id')
    def set_stage(self):
        for rec in self:
            rec.stage = 'new'
            sol_stage = rec.sale_order_line_id.mapped('state')
            if rec.cancel is True:
                rec.stage = 'cancel'
            elif rec.discount_review_id and rec.discount_review_id.stage_id == 'offer':
                rec.stage = 'waiting'
            elif rec.number_used == rec.quantity:
                rec.stage = 'done'
            elif 'draft' in sol_stage:
                rec.stage = 'processing'

    def unlink(self):
        for rec in self:
            if rec.create_uid != self.env.user:
                raise ValidationError('Bạn không thể xóa dịch vụ của nhân viên khác tạo !!!')
            elif rec.stage == 'new' and rec.number_used > 0:
                raise ValidationError('Bạn chỉ có thể xóa dịch vụ khi khách hàng chưa sử dụng !!!')
            elif rec.stage != 'new':
                raise ValidationError(
                    'Bạn chỉ có thế xóa dịch vụ khi dịch vụ đó đang ở trạng thái được phép sử dụng !!!')
            return super(CrmLine, self).unlink()

    @api.depends('sale_order_line_id.state')
    def set_number_used(self):
        for rec in self:
            rec.number_used = 0
            if rec.sale_order_line_id:
                list_sol = rec.sale_order_line_id.filtered(lambda l: l.state in ['sale', 'done'])
                rec.number_used = len(list_sol)

    @api.model
    def default_get(self, fields):
        """ Hack :  when going from the pipeline, creating a stage with a sales team in
            context should not create a stage for the current Sales Team only
        """
        ctx = dict(self.env.context)
        if ctx.get('default_type') == 'lead' or ctx.get('default_type') == 'opportunity':
            ctx.pop('default_type')
        return super(CrmLine, self.with_context(ctx)).default_get(fields)

    @api.onchange('product_id')
    def set_unit_price(self):
        if self.product_id:
            item_price = self.env['product.pricelist.item'].search(
                [('pricelist_id', '=', self.price_list_id.id), ('product_id', '=', self.product_id.id)])
            if item_price:
                self.unit_price = item_price.fixed_price
            else:
                raise ValidationError(_('This service is not included in the price list'))
        else:
            self.unit_price = 0
            self.quantity = 1
            self.discount_cash = 0
            self.discount_percent = 0

    @api.depends('quantity', 'unit_price', 'discount_percent', 'discount_cash', 'uom_price')
    def get_total_line(self):
        for rec in self:
            rec.total_before_discount = rec.unit_price * rec.quantity * rec.uom_price
            rec.total = rec.total_before_discount - rec.total_before_discount * \
                        rec.discount_percent / 100 - rec.discount_cash
            rec.total_discount = rec.total_before_discount - rec.total

    @api.constrains('discount_percent', 'discount_cash', 'total', 'total_before_discount')
    def error_discount(self):
        for rec in self:
            if rec.discount_percent > 100 or rec.discount_percent < 0:
                raise ValidationError('Giảm giá phần trăm chỉ chấp nhận giá trị trong khoảng 0 đến 100')
            if rec.discount_cash > rec.total_before_discount:
                raise ValidationError('Giảm giá tiền mặt không thể lớn hơn tổng tiền dịch vụ')

    @api.constrains('quantity')
    def validate_quantity(self):
        for rec in self:
            if rec.quantity <= 0:
                raise ValidationError(_('Quantity must be greater than 0'))
            elif rec.quantity >= 100:
                raise ValidationError(_('The amount cannot be more than 100'))

    @api.onchange('quantity')
    def validate_quantity_crm_line(self):
        for rec in self:
            if rec.quantity <= 0:
                raise ValidationError(_('Quantity must be greater than 0'))
            elif rec.quantity >= 100:
                raise ValidationError(_('The amount cannot be more than 100'))

    def create_quotation(self):
        order = self.env['sale.order'].create({
            'partner_id': self.crm_id.partner_id.id,
            'pricelist_id': self.crm_id.price_list_id.id,
            'company_id': self.crm_id.company_id.id,
            'user_id': self.crm_id.user_id.id,
            'opportunity_id': self.crm_id.id,
            # 'date_order': fields.Datetime.now,
            'crm_line_id': self.id,
        })

        order_line = self.env['sale.order.line'].create({
            'product_id': self.product_id.id,
            'name': self.product_id.name,
            'product_uom_qty': self.quantity,
            'product_uom': self.product_id.uom_id.id,
            'price_unit': self.unit_price,
            'discount': self.discount_percent,
            'order_id': order.id,
        })

        return {
            'name': 'Quotations',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('sale.view_order_form').id,
            'res_model': 'sale.order',
            'res_id': order.id,
        }

    def write(self, vals):
        res = super(CrmLine, self).write(vals)
        for rec in self:
            if rec.sale_order_line_id:
                for sol in rec.sale_order_line_id:
                    if vals.get('discount_percent'):
                        sol.discount = rec.discount_percent
                    if vals.get('discount_cash'):
                        sol.discount_cash = rec.discount_cash
                    if vals.get('uom_price'):
                        sol.uom_price = rec.uom_price
        return res
