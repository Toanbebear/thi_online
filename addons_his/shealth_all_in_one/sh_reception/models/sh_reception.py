##############################################################################
#    Copyright (C) 2018 shealth (<http://scigroup.com.vn/>). All Rights Reserved
#    shealth, Hospital Management Solutions

# Odoo Proprietary License v1.0
#
# This software and associated files (the "Software") may only be used (executed,
# modified, executed after modifications) if you have purchased a valid license
# from the authors, typically via Odoo Apps, shealth.in, openerpestore.com, or if you have received a written
# agreement from the authors of the Software.
#
# You may develop Odoo modules that use the Software as a library (typically
# by depending on it, importing it and using its resources), but without copying
# any source code or material from the Software. You may distribute those
# modules under the license of your choice, provided that this license is
# compatible with the terms of the Odoo Proprietary License (For example:
# LGPL, MIT, or proprietary licenses similar to this one).
#
# It is forbidden to publish, distribute, sublicense, or sell copies of the Software
# or modified copies of the Software.
#
# The above copyright notice and this permission notice must be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import time
import datetime
from datetime import timedelta


# INHERIT CRM BASE
class SHSelectService(models.TransientModel):
    _inherit = 'crm.select.service'

    def create_quotation(self):
        res = super(SHSelectService, self).create_quotation()

        # partner chưa là có data bệnh nhân => Tạo bệnh nhân
        if not res.partner_id.is_patient:
            # nếu có thông tin người thân
            if res.booking_id.fam_ids:
                family_data = []
                for item in res.booking_id.fam_ids:
                    family_data.append((0, 0, {'type_relation': item.type_relation_id.id,
                                               'name': item.member_name,
                                               'phone': item.phone,
                                               'address': item.member_contact}))
                patient = self.env['sh.medical.patient'].create(
                    {'partner_id': res.partner_id.id, 'family': family_data})
            else:
                patient = self.env['sh.medical.patient'].create({'partner_id': res.partner_id.id})
        else:
            patient = self.env['sh.medical.patient'].search([('partner_id', '=', res.partner_id.id)], limit=1)

        # tạo phiếu đón tiếp
        institution = self.env['sh.medical.health.center'].search([('his_company', '=', self.env.user.company_id.id)],
                                                                  limit=1)
        service_room = self.exam_room_id  # phòng khám
        uom_price = self.uom_price  # số lượn đơn vị giá
        self.env['sh.reception'].create({'patient': patient.id, 'institution': institution.id,
                                         'reason': res.note, 'service_room': service_room.id,
                                         'booking_id': res.booking_id.id, 'sale_order_id': res.id,
                                         'type_crm_id': res.booking_id.type_crm_id.id, 'uom_price': uom_price})


# Đón tiếp Management

class SHReception(models.Model):
    _name = 'sh.reception'
    _description = 'Đón tiếp'

    _rec_name = 'patient'
    _order = "reception_date desc"

    patient = fields.Many2one('sh.medical.patient', 'Bệnh nhân')
    walkin_id = fields.One2many('sh.medical.appointment.register.walkin', 'reception_id', string='Walkin')

    institution = fields.Many2one('sh.medical.health.center', string='Cơ sở y tế', required=True,
                                  domain=lambda self: [('his_company', '=', self.env.companies.ids[0])])

    pass_port = fields.Char('CMND/ Hộ chiếu', related="patient.pass_port", store=True)
    birth_date = fields.Date('Ngày sinh', related="patient.birth_date", store=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Khác')
    ], string='Giới tính', track_visibility='always', related="patient.gender", store=True)
    phone = fields.Char(string='Số điện thoại', related="patient.phone", store=True)
    street = fields.Char('Địa chỉ', related="patient.street", store=True)
    state_id = fields.Many2one('res.country.state', 'Thành phố', related="patient.state_id", store=True)
    country_id = fields.Many2one('res.country', 'Quốc gia', related="patient.country_id", store=True)

    user = fields.Many2one('res.users', string='Người đón tiếp', default=lambda self: self.env.uid,
                           domain=lambda self: [
                               ("groups_id", "=", self.env.ref("shealth_all_in_one.group_sh_medical_receptionist").id)])
    reception_date = fields.Datetime(string='Ngày đón tiếp', default=lambda self: fields.Datetime.now())
    reason = fields.Text(string='Lý do khám')
    advisory = fields.Many2one('sh.medical.health.center.service', string='Tư vấn', domain=lambda self: [
        ("id", "=", self.env.ref("shealth_all_in_one.sh_product_service_kb01").id)],
                               default=lambda self: self.env.ref('shealth_all_in_one.sh_product_service_kb01').id)
    service_room = fields.Many2one('sh.medical.health.center.ot', string='Phòng khám',
                                   domain="[('department.type', '=', 'Examination'),('institution', '=', institution)]")
    close = fields.Boolean(string='Kết thúc đón tiếp')

    booking_id = fields.Many2one('crm.lead')
    sale_order_id = fields.Many2one('sale.order')
    uom_price = fields.Integer(string='Số lượng thực hiện',
                               help="Răng/cm2/...", default=1)

    type_crm_id = fields.Many2one('crm.type', string="Loại booking", readonly=False,
                                  default=lambda self: self.env.ref('crm_base.type_oppor_new').id,
                                  states={'Completed': [('readonly', True)]}, track_visibility='onchange')

    @api.onchange('patient')
    def set_value_patient(self):
        if self.patient:
            self.pass_port = self.patient.pass_port
            self.birth_date = self.patient.birth_date
            self.gender = self.patient.gender
            self.phone = self.patient.phone
            self.street = self.patient.street
            self.state_id = self.patient.state_id.id
            self.country_id = self.patient.country_id.id

    @api.model
    def create(self, vals):
        vals['close'] = True
        res = super(SHReception, self).create(vals)
        if res.patient:
            service = self.env['sh.medical.health.center.service'].search(
                [('product_id', 'in', res.sale_order_id.order_line.mapped('product_id').ids)])
            wk = self.env['sh.medical.appointment.register.walkin'].create({
                'patient': res.patient.id,
                'date': datetime.datetime.strptime(res.reception_date.strftime("%Y-%m-%d %H:%M:%S"),
                                                   "%Y-%m-%d %H:%M:%S") + timedelta(minutes=5) or fields.Datetime.now(),
                'institution': res.institution.id,
                'department': res.service_room.department.id,
                'service_room': res.service_room.id,
                # 'reason_check': res.reason, #đã tự đông related sang nên ko cần ghi nữa, nếu ghi sẽ chạy qua hàm write
                'specialty_exam': res.reason,
                'info_diagnosis': res.reason,
                # 'doctor': self.env.ref('__import__.data_physician_kb').id if self.env.ref('__import__.data_physician_kb',False) else False,
                'pathological_process': "Khách hàng thăm khám về %s có nguyện vọng cải thiện nên vào viện." % str(
                    res.reason),
                'dob': res.birth_date,
                'sex': res.gender,
                'blood_type': res.patient.blood_type,
                'marital_status': res.patient.marital_status,
                'rh': res.patient.rh,
                'reception_id': res.id,
                'booking_id': res.booking_id.id,
                'sale_order_id': res.sale_order_id.id,
                'service': [(6, 0, service.ids)],
                'flag_surgery': service[0].is_surgeries,
                'pathology': service[0].pathology.id,
                'uom_price': res.uom_price,
                'type_crm_id': res.type_crm_id.id
            })
        return res


# Inheriting Patient module to add "Reception" screen reference
class SHealthPatient(models.Model):
    _inherit = 'sh.medical.patient'

    def _reception_count(self):
        sh_reception = self.env['sh.reception'].sudo()
        for pa in self:
            domain = [('patient', '=', pa.id)]
            recept_ids = sh_reception.search(domain)
            recept = sh_reception.browse(recept_ids)
            reception_count = 0
            for rc in recept:
                reception_count += 1
            pa.reception_count = reception_count
        return True

    reception = fields.One2many('sh.reception', 'patient', string='Đón tiếp')
    reception_count = fields.Integer(compute=_reception_count, string="Số lần Đón tiếp")
