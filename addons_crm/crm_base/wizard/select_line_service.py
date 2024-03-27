from odoo import fields, api, models, _
from odoo.exceptions import ValidationError


class SelectService(models.TransientModel):
    _name = 'crm.select.service'

    name = fields.Char('Desc')
    booking_id = fields.Many2one('crm.lead', string='Booking')
    partner_id = fields.Many2one('res.partner', string='Partner')
    crm_line_ids = fields.Many2many('crm.line', 'select_service_ref', 'crm_line_s', 'select_service_s',
                                    string='Services', domain="[('crm_id','=',booking_id), ('stage', '=', 'new')]")
    company_ids = fields.Many2many('res.company', string='Company', compute='set_company_ids', store=True)

    debt_review = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Debt review', default='no')
    debt_review_reason = fields.Text('Reason for debt')
    set_total_order = fields.Float('The amount corresponding to the service performance')
    uom_price = fields.Float('cm2/cc/unit/...', default=1)

    @api.onchange('crm_line_ids')
    def get_uom_price(self):
        self.uom_price = 1
        self.uom_price = sum(self.crm_line_ids.mapped('uom_price'))

    @api.constrains('uom_price')
    def check_limit_uom_price(self):
        for rec in self:
            limit = sum(rec.crm_line_ids.mapped('uom_price'))
            if rec.uom_price > limit:
                raise ValidationError(_("allowed limit on cm2/cc/unit/.. field is %s") % limit)

    @api.depends('booking_id')
    def set_company_ids(self):
        for rec in self:
            if rec.booking_id and rec.booking_id.company_id and rec.booking_id.company2_id:
                list = rec.booking_id.company2_id._origin.ids
                list.append(rec.booking_id.company_id.id)
                rec.company_ids = [(6, 0, list)]
            elif rec.booking_id and rec.booking_id.company_id:
                rec.company_ids = [(4, rec.booking_id.company_id.id)]

    def create_quotation(self):
        order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'pricelist_id': self.booking_id.price_list_id.id,
            'company_id': self.env.company.id,
            'booking_id': self.booking_id.id,
            'campaign_id': self.booking_id.campaign_id.id,
            'source_id': self.booking_id.source_id.id,
            'note': self.name,
            'set_total': self.set_total_order,
        })

        for rec in self.crm_line_ids:
            order_line = self.env['sale.order.line'].create({
                'order_id': order.id,
                'crm_line_id': rec.id,
                'product_id': rec.product_id.id,
                'product_uom': rec.product_id.uom_id.id,
                'company_id': self.env.company.id,
                'price_unit': rec.unit_price,
                'discount': rec.discount_percent,
                'discount_cash': rec.discount_cash / rec.quantity,
                'product_uom_qty': 1,
                'tax_id': False,
            })

        if self.debt_review == 'yes':
            debt = self.env['crm.debt.review'].create({
                'name': self.debt_review_reason,
                'order_id': order.id,
                'booking_id': self.booking_id.id,
                'stage': 'offer',
            })

        return order
