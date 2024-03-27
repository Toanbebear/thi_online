from odoo import fields, api, models, _


class BookingGuarantee(models.TransientModel):
    _name = 'crm.create.guarantee'

    crm_id = fields.Many2one('crm.lead', string='Related booking')
    partner_id = fields.Many2one('res.partner', string='Customer')
    brand_id = fields.Many2one('res.brand', string='Brand')
    price_list_id = fields.Many2one('product.pricelist', string='price list',
                                    domain="[('brand_id','=',brand_id),('type','=','guarantee')]")
    date_guarantee = fields.Datetime('Date guarantee')
    code_booking = fields.Char('Mã booking tương ứng')
    source_id = fields.Many2one('utm.source', string='Nguồn')

    def confirm(self):
        bk = self.env['crm.lead'].create({
            'name': '/',
            'code_booking': self.code_booking,
            'type_crm_id': self.env.ref('crm_base.type_oppor_guarantee').id,
            'type': 'opportunity',
            'contact_name': self.partner_id.name,
            'partner_id': self.partner_id.id,
            'stage_id': self.env.ref('crm_base.crm_stage_not_confirm').id,
            'phone': self.partner_id.phone,
            'mobile': self.partner_id.mobile,
            'street': self.partner_id.street,
            'email_from': self.partner_id.email,
            'lead_id': self.crm_id.id if self.crm_id else False,
            'gender': self.partner_id.gender,
            'company_id': self.env.company.id,
            'state_id': self.partner_id.state_id.id,
            'source_id': self.crm_id.source_id.id if self.crm_id else self.source_id.id,
            'campaign_id': self.crm_id.campaign_id.id if self.crm_id else False,
            'medium_id': self.crm_id.medium_id.id if self.crm_id else False,
            'customer_come': 'no',
            'user_id': self.env.user.id,
            'birth_date': self.partner_id.birth_date,
            'year_of_birth': self.partner_id.year_of_birth,
            'country_id': self.partner_id.country_id.id,
            'facebook_acc': self.crm_id.facebook_acc if self.crm_id else False,
            'price_list_id': self.price_list_id.id,
            'pass_port': self.partner_id.pass_port,
            'booking_date': self.date_guarantee,
            'user_id': self.env.user.id,
            'type_data': 'old',
            'category_source_id': self.crm_id.category_source_id.id if self.crm_id
            else self.source_id.category_id.id,
        })

        return {
            'name': 'Booking guarantee',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('crm_base.crm_lead_form_booking').id,
            'res_model': 'crm.lead',
            'res_id': bk.id,
        }
