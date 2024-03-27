from odoo import fields, api, models, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class CheckPartnerAndQualify(models.TransientModel):
    _name = 'check.partner.qualify'

    name = fields.Char('Contact name')
    phone = fields.Char('Phone')
    booking_date = fields.Datetime('Booking date')
    lead_id = fields.Many2one('crm.lead', string='Lead')
    company_id = fields.Many2one('res.company', string='Company')
    type = fields.Selection([('lead', 'Lead'), ('opportunity', 'Opportunity')], string='Type record crm')
    partner_id = fields.Many2one('res.partner', string='Partner')
    code_booking = fields.Char('Mã booking tương ứng')

    def qualify(self):
        self.lead_id.stage_id = self.env.ref('crm_base.crm_stage_booking').id
        self.lead_id.check_booking = True
        if self.partner_id:
            customer = self.partner_id.id
        else:
            partner = self.env['res.partner'].search([('phone', '=', self.phone)])
            if partner:
                self.lead_id.partner_id = partner.id
                customer = partner.id
            else:
                prt = self.env['res.partner'].create({
                    'name': self.name,
                    'phone': self.phone,
                    'country_id': self.lead_id.country_id.id,
                    'state_id': self.lead_id.state_id.id,
                    'street': self.lead_id.street,
                    'birth_date': self.lead_id.birth_date,
                    'pass_port': self.lead_id.pass_port,
                    'gender': self.lead_id.gender,
                    'year_of_birth': self.lead_id.year_of_birth,
                    'company_id': False,
                    'source_id': self.lead_id.source_id.id,
                    'email': self.lead_id.email_from,
                })
                customer = prt.id
                self.lead_id.partner_id = customer

        booking = self.env['crm.lead'].create({
            'type_crm_id': self.env.ref('crm_base.type_oppor_new').id,
            'type': 'opportunity',
            'contact_name': self.lead_id.contact_name,
            'partner_id': customer,
            'stage_id': self.env.ref('crm_base.crm_stage_not_confirm').id,
            'phone': self.lead_id.phone,
            'mobile': self.lead_id.mobile,
            'street': self.lead_id.street,
            'email_from': self.lead_id.email_from,
            'lead_id': self.lead_id.id,
            'gender': self.lead_id.gender,
            'company_id': self.lead_id.company_id.id,
            'state_id': self.lead_id.state_id.id,
            'source_id': self.lead_id.source_id.id,
            'campaign_id': self.lead_id.campaign_id.id,
            'medium_id': self.lead_id.medium_id.id,
            'customer_come': 'no',
            'category_source_id': self.lead_id.category_source_id.id,
            'user_id': self.env.user.id,
            'birth_date': self.lead_id.birth_date,
            'year_of_birth': self.lead_id.year_of_birth,
            'country_id': self.lead_id.country_id.id,
            'facebook_acc': self.lead_id.facebook_acc,
            'price_list_id': self.lead_id.price_list_id.id,
            'product_ctg_ids': [(6, 0, self.lead_id.product_ctg_ids.ids)],
            'description': self.lead_id.description,
            'special_note': self.lead_id.special_note,
            'pass_port': self.lead_id.pass_port,
            'booking_date': self.booking_date,
            'user_id': self.lead_id.user_id.id,
            'type_data': self.lead_id.type_data,
            'code_booking': self.code_booking,
            'brand_id': self.lead_id.brand_id.id,
            'fam_ids': [(6, 0, self.lead_id.fam_ids.ids)],
        })

        if self.lead_id.crm_line_ids:
            for rec in self.lead_id.crm_line_ids:
                line = self.env['crm.line'].create({
                    'name': rec.name,
                    'quantity': rec.quantity,
                    'number_used': rec.number_used,
                    'unit_price': rec.unit_price,
                    'discount_percent': rec.discount_percent,
                    'type': rec.type,
                    'discount_cash': rec.discount_cash,
                    'price_list_id': rec.price_list_id.id,
                    'total_before_discount': rec.total_before_discount,
                    'crm_id': booking.id,
                    'company_id': rec.company_id.id,
                    'product_id': rec.product_id.id,
                    'source_extend_id': rec.source_extend_id.id,
                    'uom_price': rec.uom_price,
                    'prg_ids': [(6, 0, rec.prg_ids.ids)],
                })

        self.create_phone_call(booking)

        return {
            'name': 'Booking',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('crm_base.crm_lead_form_booking').id,
            'res_model': 'crm.lead',
            'res_id': booking.id,
        }

    def create_phone_call(self, booking):
        phone_call = self.env['crm.phone.call'].create({
            'name': ('Xác nhận lịch hẹn khách hàng %s' % booking.contact_name),
            'subject': ('Xác nhận lịch hẹn'),
            'user_id': 1,
            'contact_name': booking.contact_name,
            'partner_id': booking.partner_id.id,
            'phone': booking.phone,
            'direction': 'out',
            'company_id': booking.company_id.id,
            'crm_id': booking.id,
            'country_id': booking.country_id.id,
            'state_id': booking.state_id.id,
            'street': booking.street,
            'type_crm_id': self.env.ref('crm_base.type_phone_call_confirm_appointment').id,
            'stage_id': self.env.ref('crm_base.crm_stage_no_process').id,
            'crm_line_id': [(6, 0, booking.crm_line_ids._origin.ids)],
            'booking_date': booking.booking_date,
            'call_date': booking.booking_date - relativedelta(days=+1),
            'create_by': 1,
        })
