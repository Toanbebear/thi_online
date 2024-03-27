from odoo import fields, models, api


class CrmLoyaltyUseReward(models.TransientModel):
    _name = 'crm.loyalty.use.reward'

    loyalty_id = fields.Many2one('crm.loyalty.card', string='Loyalty')
    reward_id = fields.Many2one('crm.loyalty.line.reward', string='Reward')
    booking_id = fields.Many2one('crm.lead', string='Booking',
                                 domain="[('partner_id','=',partner_id),('type','=','opportunity')]")
    partner_id = fields.Many2one('res.partner', string='Customer')

    def confirm(self):
        line = self.env['crm.line'].create({
            'name': self.reward_id.name,
            'quantity': '1',
            'unit_price': 0,
            'type': self.booking_id.type,
            'price_list_id': self.booking_id.price_list_id.id,
            'crm_id': self.booking_id.id,
            'company_id': self.booking_id.company_id.id,
            'product_id': self.reward_id.product_id.id,
            'source_extend_id': self.booking_id.source_id.id,
            'line_special': True,
            'type': 'service',
            'reward_id': self.reward_id.id,
        })
        return {
            'name': 'Booking',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('crm_base.crm_lead_form_booking').id,
            'res_model': 'crm.lead',
            'res_id': self.booking_id.id,
        }
