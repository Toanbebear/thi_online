from odoo import fields, api, models, _


class DebtReview(models.Model):
    _name = 'crm.debt.review'

    name = fields.Text('Reason')
    order_id = fields.Many2one('sale.order', string='Order')
    booking_id = fields.Many2one('crm.lead', string='Booking')
    stage = fields.Selection([('offer', 'Offer'), ('approve', 'Approve'), ('refuse', 'Refuse')], string='Stage',
                             default='offer')
    company_id = fields.Many2one('res.company', string='Company', related='booking_id.company_id',store=True)

    def set_approve(self):
        self.stage = 'approve'
        self.order_id.debt_review = True

    def set_refuse(self):
        self.stage = 'refuse'
        self.order_id.debt_review = False
