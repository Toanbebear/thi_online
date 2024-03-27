from odoo import fields, models, api


class ShareBooking(models.TransientModel):
    _name = 'share.booking'

    company_shared_id = fields.Many2one('res.company', string='Select company share')
    booking_id = fields.Many2one('crm.lead', string='Booking')

    def get_company(self):
        if self.booking_id:
            self.booking_id.company2_id = [(4, self.company_shared_id.id)]
