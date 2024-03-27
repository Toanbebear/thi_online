from odoo import fields, api, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    stage_sol = fields.Selection([('new', 'New'), ('processing', 'Processing'), ('done', 'Done'), ('cancel', 'Cancel')],
                                 string='Stage')
    odontology = fields.Boolean('Odontology', related='crm_line_id.odontology')

    @api.model
    def create(self, vals):
        res = super(SaleOrderLine, self).create(vals)
        if res.order_id.document_related and res.product_id.type == 'service' and res.order_id and res.order_id.booking_id:
            crm_line = self.env['crm.line'].create({
                'product_id': res.product_id.id,
                'quantity': res.product_uom_qty,
                'unit_price': res.price_unit,
                'crm_id': res.order_id.booking_id.id,
                'company_id': res.order_id.company_id.id,
                'price_list_id': res.order_id.pricelist_id.id,
                'sale_order_line_id': [(4, res.id)],
                'stage': 'new',
            })
        return res


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    odontology = fields.Boolean('Odontology', compute='set_odontology')

    @api.depends('order_line')
    def set_odontology(self):
        for rec in self:
            rec.odontology = False
            if rec.order_line and rec.order_line[0].odontology is True:
                rec.odontology = True
