from odoo import fields, api, models, _
from dateutil.relativedelta import relativedelta


class Walkin(models.Model):
    _inherit = 'sh.medical.appointment.register.walkin'

    def create_phone_call_re_exam(self):
        for sv in self.service:
            phone_call = self.env['crm.phone.call'].sudo().create({
                'name': 'Xác nhận lịch tái khám',
                'subject': 'Xác nhận lịch tái khám khách hàng %s ' % self.patient.name,
                'user_id': 1,
                'contact_name': self.booking_id.contact_name,
                'partner_id': self.booking_id.partner_id.id,
                'phone': self.booking_id.phone,
                'direction': 'out',
                'company_id': self.booking_id.company_id.id,
                'crm_id': self.booking_id.id,
                'country_id': self.booking_id.country_id.id,
                'state_id': self.booking_id.state_id.id,
                'street': self.booking_id.street,
                'type_crm_id': self.env.ref('crm_base.type_phone_call_exam_schedule').id,
                'stage_id': self.env.ref('crm_base.crm_stage_no_process').id,
                'date_re_exam': self.date_re_exam,
                'call_date': self.date_re_exam - relativedelta(days=+1),
                'create_by': 1,
                'service_id': sv.id,
                'desc_doctor': self.comments,
                'date_out_location': self.date_out,
            })

    def create_phone_call_service(self):
        for sv in self.service:
            pc = self.env['crm.phone.call'].sudo().create({
                'name': 'Chăm sóc sau dịch vụ lần 1 ',
                'subject': 'Chăm sóc sau dịch vụ khách hàng %s' % self.patient.name,
                'user_id': 1,
                'contact_name': self.booking_id.contact_name,
                'partner_id': self.booking_id.partner_id.id,
                'phone': self.booking_id.phone,
                'direction': 'out',
                'company_id': self.booking_id.company_id.id,
                'crm_id': self.booking_id.id,
                'country_id': self.booking_id.country_id.id,
                'state_id': self.booking_id.state_id.id,
                'street': self.booking_id.street,
                'type_crm_id': self.env.ref('crm_base.type_phone_call_after_service_care').id,
                'stage_id': self.env.ref('crm_base.crm_stage_no_process').id,
                'date_out_location': self.date_out,
                'call_date': self.date_out + relativedelta(days=+1),
                'create_by': 1,
                'service_id': sv.id,
                'desc_doctor': self.comments,
                'date_re_exam': self.date_re_exam,
            })

    def write(self, vals):
        res = super(Walkin, self).write(vals)
        for rec in self:
            if vals.get('date_re_exam'):
                self.create_phone_call_re_exam()
            if vals.get('date_out'):
                self.create_phone_call_service()
        return res
