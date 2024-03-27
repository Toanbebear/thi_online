from odoo import fields, models, api


class CancelBooking(models.TransientModel):
    _name = 'cancel.booking'

    name = fields.Text('Reason')
    booking_id = fields.Many2one('crm.lead', string='Booking')

    def set_cancel(self):
        for rec in self:
            if rec.booking_id:
                rec.booking_id.stage_id = self.env.ref('crm_base.crm_stage_cancel').id
                rec.booking_id.reason_cancel = rec.name

    def set_out_sold(self):
        for rec in self:
            if rec.booking_id:
                rec.booking_id.stage_id = self.env.ref('crm_base.crm_stage_out_sold').id
                rec.booking_id.reason_cancel = rec.name
