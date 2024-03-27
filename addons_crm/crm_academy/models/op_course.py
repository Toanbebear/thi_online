from odoo import api, fields, models
from odoo.exceptions import ValidationError

class InheritCourse(models.Model):
    _inherit = 'op.course'

    product_id = fields.Many2one('product.product', string='Product')
    batch_id = fields.One2many('op.batch', 'course_id')

    @api.model
    def create(self, vals):
        res = super(InheritCourse, self).create(vals)
        if res.code and res.name:
            product = self.env['product.product'].sudo().create({
                'name': res.name,
                'sale_ok': True,
                'type': 'service',
                'type_product_crm': 'course',
                'default_code': res.code,
                'currency_id': res.currency_id.id
            })
            res.product_id = product.id
        return res
