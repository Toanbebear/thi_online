from odoo import api, fields, models


class InheritCrmLine(models.Model):
    _inherit = 'crm.line'

    course_id = fields.Many2one('op.course', string='Course')
    money_receive = fields.Integer('Money receive')
    paid = fields.Integer('Paid')
    full_payment = fields.Boolean('Full payment ?', compute='check_full_payment', store=True)
    note = fields.Char('Notes')

    @api.onchange('course_id')
    def get_product_course(self):
        if self.course_id:
            self.product_id = self.course_id.product_id.id

    @api.depends('paid', 'total', 'type_brand')
    def check_full_payment(self):
        for rec in self:
            rec.full_payment = False
            if rec.type_brand == 'academy':
                rec.full_payment = True if rec.paid and rec.paid == rec.total else False