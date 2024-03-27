from odoo import fields, api, models, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from lxml import etree
import json


class PhoneCall(models.Model):
    _inherit = 'crm.phone.call'

    service_id = fields.Many2one('sh.medical.health.center.service', string='Service')
    date_re_exam = fields.Datetime("Date re exam")
    desc_doctor = fields.Char('Desc doctor')
    date_out_location = fields.Datetime('Date out')

    @api.onchange('date_re_exam')
    def set_call_date_2(self):
        if self.date_re_exam:
            self.call_date = self.date_re_exam - relativedelta(days=+1)

    def write(self, vals):
        res = super(PhoneCall, self).write(vals)
        for rec in self:
            if vals.get('date_re_exam'):
                phone_call = self.env['crm.phone.call'].create({
                    'name': 'Xác nhận lịch tái khám',
                    'subject': 'Xác nhận lịch tái khám khách hàng %s ' % self.partner_id.name,
                    'user_id': 1,
                    'contact_name': rec.booking_id.contact_name,
                    'partner_id': rec.booking_id.partner_id.id,
                    'phone': rec.booking_id.phone,
                    'direction': 'out',
                    'company_id': rec.booking_id.company_id.id,
                    'crm_id': rec.booking_id.id,
                    'country_id': rec.booking_id.country_id.id,
                    'state_id': rec.booking_id.state_id.id,
                    'street': rec.booking_id.street,
                    'type_crm_id': self.env.ref('crm_base.type_phone_call_exam_schedule').id,
                    'stage_id': self.env.ref('crm_base.crm_stage_not_confirm').id,
                    'crm_line_id': [(6, 0, rec.booking_id.crm_line_ids.ids)],
                    'date_re_exam': rec.date_re_exam,
                    'call_date': rec.date_re_exam - relativedelta(days=+1),
                    'create_by': 1,
                })
                rec.stage_id = self.env.ref('crm_base.crm_stage_change_schedule').id

        return res
