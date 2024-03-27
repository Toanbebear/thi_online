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
import datetime
from odoo import tools
from datetime import date
from odoo.exceptions import UserError
from odoo.tools import pycompat
from odoo.exceptions import UserError, AccessError, ValidationError, Warning
import logging

_logger = logging.getLogger(__name__)

# Inpatient Hospitalization Management


class SHealthInpatient(models.Model):
    _name = 'sh.medical.inpatient'
    _description = "Information about the Patient administration"

    ADMISSION_TYPE = [
            ('Routine', 'Routine'),
            # ('Maternity', 'Maternity'),
            ('Elective', 'Elective'),
            # ('Urgent', 'Urgent'),
            ('Emergency', 'Emergency'),
            ('Other', 'Other'),
        ]

    INPATIENT_STATES = [
            ('Draft', 'Nháp'),
            ('Hospitalized', 'Đã nhập viện'),
            ('Invoiced', 'Invoiced'),
            ('Discharged', 'Đã xuất viện'),
            ('Cancelled', 'Đã hủy'),
        ]

    # Automatically detect logged in physician

    def _get_physician(self):
        """Return default physician value"""
        therapist_obj = self.env['sh.medical.physician']
        domain = [('sh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain, limit=1)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    def _get_default_institution(self):
        inpatient_institution = self.env['sh.medical.health.center'].search([('his_company', '=', self.env.companies.ids[0])], limit=1)
        if inpatient_institution:
            return inpatient_institution.id or False
        else:
            return False

    def _get_default_ward(self):
        inpatient_department = self.env['sh.medical.health.center.ward'].search([('type', '=', 'Inpatient'),('institution.his_company', '=', self.env.companies.ids[0])], limit=1)
        if inpatient_department:
            return inpatient_department.id or False
        else:
            return False

    name = fields.Char(string='Inpatient #', size=128, readonly=True, required=True, default=lambda *a: '/')
    patient = fields.Many2one('sh.medical.patient', string='Patient', help="Patient Name", required=True, readonly=True, states={'Draft': [('readonly', False)]})
    admission_type = fields.Selection(ADMISSION_TYPE, string='Admission Type', required=True, readonly=True, states={'Draft': [('readonly', False)]}, default=lambda *a: 'Elective')
    admission_reason = fields.Many2one('sh.medical.pathology', string='Reason for Admission', help="Reason for Admission", readonly=True, states={'Draft': [('readonly', False)]})
    admission_reason_walkin = fields.Text(related='walkin.reason_check', readonly=True,store=True)
    admission_date = fields.Datetime(string='Hospitalization Date', readonly=True, states={'Draft': [('readonly', False)]})
    discharge_date = fields.Datetime(string='Discharge Date', readonly=False, states={'Discharged': [('readonly', True)]})
    attending_physician = fields.Many2one('sh.medical.physician', string='Attending Physician', readonly=False, states={'Discharged': [('readonly', True)]}, default=_get_physician)
    operating_physician = fields.Many2one('sh.medical.physician', string='Operating Physician', readonly=False, states={'Discharged': [('readonly', True)]})
    institution = fields.Many2one('sh.medical.health.center', string='Cơ sở y tế', readonly=True, states={'Draft': [('readonly', False)]},default=_get_default_institution)
    ward = fields.Many2one('sh.medical.health.center.ward', string='Ward', readonly=True, states={'Draft': [('readonly', False)]},default=_get_default_ward)
    # ward_surgery = fields.Text(default=lambda self: self.env.ref('shealth_all_in_one.sh_surgeries_dep_knhn').name, readonly=True,store=True)
    bed = fields.Many2one('sh.medical.health.center.beds', string='Bed', readonly=True, states={'Draft': [('readonly', False)]})
    nursing_plan = fields.Text(string='Nursing Plan', readonly=False,states={'Discharged': [('readonly', True)]})
    discharge_plan = fields.Text(string='Discharge Plan', readonly=False,states={'Discharged': [('readonly', True)]})
    admission_condition = fields.Text(string='Condition before Admission', readonly=True,states={'Draft': [('readonly', False)]})
    info = fields.Text(string='Extra Info', readonly=False,states={'Discharged': [('readonly', True)]})
    state = fields.Selection(INPATIENT_STATES, string='State', default=lambda *a: 'Draft')

    services = fields.Many2many('sh.medical.health.center.service', 'sh_inpatient_service_rel', 'inpatient_id', 'service_id',
                               readonly=True, store=True, track_visibility='onchange',
                               string='Dịch vụ')

    @api.onchange('discharge_date', 'admission_date')
    def _onchange_date(self):
        if self.admission_date and self.discharge_date:
            if self.admission_date > self.discharge_date:
                raise UserError(
                    _('Thông tin không hợp lệ! Ngày vào khoa phải trước ngày kết thúc chăm sóc!'))


    def write(self, vals):
        if vals.get('admission_date') or vals.get('discharge_date'):
            for record in self:
                # date_requested = vals.get('date_requested') or record.date_requested
                admission_date = vals.get('admission_date') or record.admission_date
                discharge_date = vals.get('discharge_date') or record.discharge_date

                # format to date
                if isinstance(admission_date, str):
                    admission_date = datetime.datetime.strptime(admission_date, '%Y-%m-%d %H:%M:%S')
                if isinstance(discharge_date, str):
                    discharge_date = datetime.datetime.strptime(discharge_date, '%Y-%m-%d %H:%M:%S')
                if admission_date and discharge_date and admission_date > discharge_date:
                    raise UserError(
                        _(
                            'Thông tin không hợp lệ! Ngày vào khoa phải trước ngày kết thúc chăm sóc!'))

        return super(SHealthInpatient, self).write(vals)


    def view_detail_inpatient(self):
        return {
            'name': _('Chi tiết bệnh nhân lưu'),  # label
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': self.env.ref('shealth_all_in_one.sh_medical_inpatient_view').id,
            'res_model': 'sh.medical.inpatient',  # model want to display
            'target': 'current',  # if you want popup,
            'context': {'form_view_initial_mode': 'edit'},
            'res_id': self.id
        }

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('sh.medical.inpatient.%s'%vals['institution'])
        if not sequence:
            raise ValidationError(_('Định danh phiếu lưu bệnh nhân của Cơ sở y tế này đang không tồn tại!'))
        vals['name'] = sequence or '/'
        health_inpatient = super(SHealthInpatient, self).create(vals)
        return health_inpatient


    def _default_account(self):
        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        return journal.default_credit_account_id.id


    def set_to_hospitalized(self):
        hospitalized_date = False
        bed_obj = self.env["sh.medical.health.center.beds"]
        for ina in self:
            if ina.admission_date:
                hospitalized_date = ina.admission_date
            else:
                hospitalized_date = datetime.datetime.now()
            # if ina.bed:
            #     query = _("update sh_medical_health_center_beds set state='Occupied' where id=%s") % (str(ina.bed.id))
            #     self.env.cr.execute(query)
        return self.write({'state': 'Hospitalized', 'admission_date': hospitalized_date})


    def set_to_discharged(self):
        discharged_date = False
        bed_obj = self.env["sh.medical.health.center.beds"]
        for ina in self:
            if ina.discharge_date:
                discharged_date = ina.discharge_date
            else:
                discharged_date = datetime.datetime.now()

            # if ina.bed:
            #     query = _("update sh_medical_health_center_beds set state='Free' where id=%s") % (str(ina.bed.id))
            #     self.env.cr.execute(query)
        return self.write({'state': 'Discharged', 'discharge_date': discharged_date})


    def set_to_invoiced(self):
        invoice_obj = self.env["account.move"]
        invoice_line_obj = self.env["account.move.line"]
        inv_ids = []
        res = {}

        for inpatient in self:

            # Calculate Hospitalized duration
            duration = 1

            if inpatient.admission_date and inpatient.discharge_date:
                admission_date = datetime.datetime.strptime(inpatient.admission_date.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
                discharge_date = datetime.datetime.strptime(inpatient.discharge_date.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
                delta = date(discharge_date.year, discharge_date.month, discharge_date.day) - date(admission_date.year, admission_date.month, admission_date.day)
                if delta.days == 0:
                    duration = 1
                else:
                    duration = delta.days

            # Create Invoice
            if inpatient.bed:
                curr_invoice = {
                    'partner_id': inpatient.patient.partner_id.id,
                    'account_id': inpatient.patient.partner_id.property_account_receivable_id.id,
                    'patient': inpatient.patient.id,
                    'state': 'draft',
                    'type':'out_invoice',
                    'date_invoice': datetime.date.today(),
                    'origin': "Inpatient# : " + inpatient.name,
                    'target': 'new',
                }

                inv_ids = invoice_obj.create(curr_invoice)

                prd_account_id = self._default_account()

                # Create Invoice line
                curr_invoice_line = {
                    'name': "Inpatient Admission charge for " + str(duration) + " day(s) of " + inpatient.bed.product_id.name,
                    'product_id': inpatient.bed.product_id.id,
                    'price_unit': duration * inpatient.bed.list_price,
                    'quantity': 1.0,
                    'account_id': prd_account_id,
                    'invoice_id': inv_ids.id,
                }
                inv_line_ids = invoice_line_obj.create(curr_invoice_line)
                res = self.write({'state': 'Invoiced'})

            else:
                raise UserError(_('Please first select bed to raise an invoice !'))
        return res


    def set_to_cancelled(self):
        bed_obj = self.env["sh.medical.health.center.beds"]
        # for ina in self:
        #     if ina.bed:
        #         query = _("update sh_medical_health_center_beds set state='Free' where id=%s") % (str(ina.bed.id))
        #         self.env.cr.execute(query)
        return self.write({'state': 'Cancelled'})


    def set_to_draft(self):
        return self.write({'state': 'Draft'})
    

    def unlink(self):
        for inpatient in self.filtered(lambda inpatient: inpatient.state not in ['Draft']):
            raise UserError(_('You can not delete an admission record which is not in "Draft" state !!'))
        return super(SHealthInpatient, self).unlink()


class SHealthInpatientProfile(models.Model):
    _name = "sh.medical.inpatient.mydetails"
    _description = "Patient view only own admissions"
    _auto = False

    INPATIENT_STATES = [
        ('Draft', 'Draft'),
        ('Hospitalized', 'Hospitalized'),
        ('Invoiced', 'Invoiced'),
        ('Discharged', 'Discharged'),
        ('Cancelled', 'Cancelled'),
    ]

    name = fields.Char(string='Inpatient #', size=128, readonly=True)
    patient = fields.Many2one('sh.medical.patient', string='Patient', help="Patient Name", readonly=True)
    admission_type = fields.Char(string='Admission Type', size=128, readonly=True)
    admission_reason = fields.Many2one('sh.medical.pathology', string='Reason for Admission', help="Reason for Admission", readonly=True)
    admission_date = fields.Datetime(string='Hospitalization Date', readonly=True)
    discharge_date = fields.Datetime(string='Discharge Date', readonly=True)
    attending_physician = fields.Many2one('sh.medical.physician', string='Attending Physician', readonly=True)
    operating_physician = fields.Many2one('sh.medical.physician', string='Operating Physician', readonly=True)
    ward = fields.Many2one('sh.medical.health.center.ward', string='Ward', required=True, readonly=True)
    bed = fields.Many2one('sh.medical.health.center.beds', string='Bed', required=True, readonly=True)
    nursing_plan = fields.Text(string='Nursing Plan', readonly=True)
    discharge_plan = fields.Text(string='Discharge Plan', readonly=True)
    admission_condition = fields.Text(string='Condition before Admission', readonly=True)
    info = fields.Text(string='Extra Info', readonly=True)
    state = fields.Selection(INPATIENT_STATES, string='State', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'sh_medical_inpatient_mydetails')
        self.env.cr.execute("""
            create or replace view sh_medical_inpatient_mydetails as (
                 select
                     o.id as id,
                     o.name as name,
                     o.patient as patient,
                     o.admission_type as admission_type,
                     o.admission_date as admission_date,
                     o.admission_reason as admission_reason,
                     o.discharge_date as discharge_date,
                     o.attending_physician as attending_physician,
                     o.operating_physician as operating_physician,
                     o.ward as ward,
                     o.bed as bed,
                     o.nursing_plan as nursing_plan,
                     o.discharge_plan as discharge_plan,
                     o.admission_condition as admission_condition,
                     o.info as info,
                     o.state as state
                 from
                     sh_medical_inpatient o
            )
        """)