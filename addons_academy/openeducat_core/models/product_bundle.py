from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class ProductBundle(models.Model):
    _name = 'product.bundle'

    name = fields.Char("BOM's name")
    code = fields.Char("BOM's code")
    bom_type = fields.Selection([('course_bom', 'Course BOM'), ('gift_bom', 'Gift BOM')], string='BOM type',
                                default='course_bom')
    duplicate = fields.Many2one('product.bundle', string='Duplicate from')
    total_cost = fields.Float('Total cost', compute='_get_total')
    total_price = fields.Float('Total price', compute='_get_total')
    currency_id = fields.Many2one(
        'res.currency', 'Currency',
        default=lambda self: self.env.user.company_id.currency_id.id,
        required=True)
    products = fields.One2many('products.line', 'bundle', string='Product')
    products_domain = fields.Many2many('product.product', string='Duma', compute='_get_total')

    @api.depends('products')
    def _get_total(self):
        for record in self:
            record.products_domain = [
                (6, 0, [product.product.id for product in record.products if product.product])] if len(
                record.products) > 0 else False
            record.total_cost = sum(
                [product.cost * product.quantity for product in record.products]) if record.products else 0
            record.total_price = sum(
                [product.price * product.quantity for product in record.products]) if record.products else 0

    @api.onchange('duplicate')
    def onchange_duplicate(self):
        if self.duplicate:
            # model = self._context.get('active_model')
            # current_record = self.env['op.admission'].browse(self._context.get('active_id'))
            self.name = self.duplicate.name + ' - '
            vals = []
            for record in self.env['products.line'].search([('bundle', '=', self.duplicate.id)]):
                vals.append((0, 0, {'product': record.product.id,
                                    'quantity': record.quantity,
                                    'currency_id': record.currency_id.id,
                                    'cost': record.cost,
                                    'price': record.price}))
            self.update({'products': vals})
        if not self.duplicate and len(self.products) > 0:
            for record in self.products:
                record.unlink()


class ProductsLine(models.Model):
    _name = 'products.line'

    bundle = fields.Many2one('product.bundle')
    course_id = fields.Many2one('op.course', 'Course')
    batch_id = fields.Many2one('op.batch', 'Batch')
    product = fields.Many2one('product.product', string='Product')
    quantity = fields.Float('Quantity', default=0)
    cost = fields.Float('Cost per unit')
    price = fields.Float('Price per unit')
    total_cost = fields.Float('Total cost', compute='_get_total_cost')
    currency_id = fields.Many2one(
        'res.currency', 'Currency',
        default=lambda self: self.env.user.company_id.currency_id.id,
        required=True)
    uom_id = fields.Many2one('uom.uom', string='Unit', related='product.uom_id')
    uom_category = fields.Many2one('uom.category', related='product.uom_id.category_id')

    exceed_maximum = fields.Boolean('Exceed maximum', compute='_get_exceed')

    @api.depends('batch_id', 'product')
    def _get_exceed(self):
        # Todo: try to reduce search queries
        for record in self:
            if record.batch_id and not record.course_id:
                course_line = self.env['products.line'].search([('product', '=', record.product.id),
                                                                ('course_id', '=', record.batch_id.course_id.id),
                                                                ('batch_id', '=', False)], limit=1)
                if not course_line or record.quantity > course_line.quantity:
                    record.exceed_maximum = True
                else:
                    record.exceed_maximum = False
            else:
                record.exceed_maximum = False

    @api.depends('quantity', 'cost')
    def _get_total_cost(self):
        for record in self:
            if record.quantity and record.cost:
                record.total_cost = record.quantity * record.cost
            else:
                record.total_cost = 0

    @api.onchange('product')
    def _onchange_product(self):
        for record in self:
            if record.product:
                record.cost = record.product.standard_price
                record.price = record.product.lst_price

    @api.constrains('quantity')
    def validate_quantity(self):
        for record in self:
            if record.quantity <= 0:
                raise ValidationError(_("Quantity must be greater than zero!"))

    _sql_constraints = [
        ('product_BOM_uniq', 'unique(product, bundle)', 'Product must be unique per BOM!'),
        ('product_batch_uniq', 'unique(product, batch_id)', 'Product must be unique per batch!'),
        ('product_course_uniq', 'unique(product, course_id)', 'Product must be unique per course!'),
    ]
