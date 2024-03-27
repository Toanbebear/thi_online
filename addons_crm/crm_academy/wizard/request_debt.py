from odoo import api, fields, models


class RequestDebt(models.TransientModel):
    _name = 'request.debt'

    name = fields.Char('Desc')
    booking_id = fields.Many2one('crm.lead', string='Booking')
    partner_id = fields.Many2one('res.partner', string='Partner')
    # company_ids = fields.Many2many('res.company', string='Company', compute='set_company_ids_request_payment',
    #                                store=True)
    company_id = fields.Many2one('res.company', string='Company')
    crm_line_ids = fields.Many2many('crm.line', 'request_debt_ref', 'crm_line_s', 'request_debt_s',
                                    string='Services', domain="[('crm_id','=',booking_id), ('stage', '=', 'new')]")
    amount_total = fields.Float('Amount total', compute='_total_amount', digits=(3, 0))
    payment_amount = fields.Monetary('Payment Amount', digits=(3, 0))
    currency_id = fields.Many2one('res.currency', string='Currency', related='booking_id.price_list_id.currency_id',
                                  store=True)

    # note = fields.Char('Note')

    @api.onchange('crm_line_ids')
    def onchange_name(self):
        if self.crm_line_ids:
            self.note = ''
            for course in self.crm_line_ids:
                self.note += course.course_id.name + ";"

    @api.depends('booking_id')
    def set_company_ids_request_payment(self):
        for rec in self:
            if rec.booking_id and rec.booking_id.company_id and rec.booking_id.company2_id:
                list = rec.booking_id.company2_id._origin.ids
                list.append(rec.booking_id.company_id.id)
                rec.company_ids = [(6, 0, list)]
            elif rec.booking_id and rec.booking_id.company_id:
                rec.company_ids = [(4, rec.booking_id.company_id.id)]

    # @api.depends('booking_id')
    # def get_crm_line_ids(self):
    #     self.crm_line_ids = False
    #     if self.booking_id:
    #         if self.booking_id.crm_line_ids:
    #             for rec in self.booking_id.crm_line_ids:
    #                 if rec.stage == 'new':
    #                     self.crm_line_ids += rec

    @api.depends('crm_line_ids')
    def _total_amount(self):
        self.amount_total = 0
        if self.crm_line_ids:
            for rec in self.crm_line_ids:
                self.amount_total += rec.total

    def request_debt(self):
        self.env['crm.debt.review'].create({
            'name': self.name,
            'booking_id': self.booking_id.id,
            'crm_line_ids': self.crm_line_ids,
            'amount_total': self.amount_total,
            'payment_amount': self.payment_amount,
            'stage': 'offer',
        })