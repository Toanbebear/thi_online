from odoo import fields, api, models


class CRM(models.Model):
    _inherit = 'crm.lead'

    def select_service(self):
        company = self.env.user.company_id.id
        return {
            'name': 'Lựa chọn dịch vụ',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('crm_base.view_form_crm_select_service').id,
            'res_model': 'crm.select.service',
            'context': {
                'default_partner_id': self.partner_id.id,
                'default_booking_id': self.id,
                'default_institution': self.env['sh.medical.health.center'].sudo().
                    search([('his_company', '=', self.env.company.id)], limit=1).id,
            },
            'target': 'new',
        }

    walkin_ids = fields.One2many('sh.medical.appointment.register.walkin', 'booking_id', string='Walkin')
