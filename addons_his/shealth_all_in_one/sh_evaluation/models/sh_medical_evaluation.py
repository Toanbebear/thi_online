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
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, AccessError, ValidationError, Warning
from odoo import api, fields, models, _
import datetime
import logging

_logger = logging.getLogger(__name__)

class SHealthEvaluationServices(models.Model):
    _name = 'sh.medical.evaluation.services'
    _description = "Loại tái khám bệnh nhân"

    name = fields.Char(string='Tên', required=True)
    has_supply = fields.Boolean(string='Có VTTH?')

class SHealthEvaluationTeam(models.Model):
    _name = "sh.medical.evaluation.team"
    _description = "Evaluation Team"

    _sql_constraints = [('name_unique', 'unique(name,team_member,role)',
                         "Vai trò của thành viên phải là duy nhất!")]

    name = fields.Many2one('sh.medical.evaluation', string='Thăm khám')
    team_member = fields.Many2one('sh.medical.physician', string='Thành viên',
                                  help="Health professional that participated on this surgery",
                                  domain=[('is_pharmacist', '=', False)], required=True)

    service_performances = fields.Many2many('sh.medical.health.center.service', 'sh_evaluation_team_services_rel',
                                            'evaluation_team_id', 'service_id', string='Dịch vụ thực hiện',
                                            help="Các dịch vụ của thành viên với vai trog này thực hiện")

    role = fields.Many2one('sh.medical.team.role', string='Vai trò')
    notes = fields.Char(string='Note')

class SHealthPatientEvaluation(models.Model):
    _name = 'sh.medical.evaluation'
    _description = "Phiếu tái khám bệnh nhân"

    _order = 'evaluation_start_date desc'

    EVALUATION_TYPE = [
            # ('Ambulatory', 'Ambulatory'),
            # ('Emergency', 'Emergency'),
            # ('Inpatient Admission', 'Inpatient Admission'),
            ('Pre-arraganged Appointment', 'Pre-arraganged Appointment'),
            # ('Periodic Control', 'Periodic Control'),
            # ('Phone Call', 'Phone Call'),
            # ('Telemedicine', 'Telemedicine'),
    ]

    MOOD = [
            ('Normal', 'Normal'),
            ('Sad', 'Sad'),
            ('Fear', 'Fear'),
            ('Rage', 'Rage'),
            ('Happy', 'Happy'),
            ('Disgust', 'Disgust'),
            ('Euphoria', 'Euphoria'),
            ('Flat', 'Flat'),
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
        inpatient_department = self.env['sh.medical.health.center.ward'].search([('type', '=', ['Surgery','Inpatient']),('institution.his_company', '=', self.env.companies.ids[0])], limit=1)
        if inpatient_department:
            return inpatient_department.id or False
        else:
            return False

    name = fields.Char(string='Evaluation #', size=64, readonly=True, required=True, default=lambda *a: '/')
    patient = fields.Many2one('sh.medical.patient', string='Patient', help="Patient Name", required=True)
    doctor = fields.Many2one('sh.medical.physician', string='Physician', help="Current primary care / family doctor", domain=[('is_pharmacist','=',False)], required=True, default=_get_physician)
    appointment = fields.Many2one('sh.medical.appointment', string='Appointment #')

    institution = fields.Many2one('sh.medical.health.center', string='Cơ sở y tế', readonly=True,
                                  states={'InProgress': [('readonly', False)]}, default=_get_default_institution)
    ward = fields.Many2one('sh.medical.health.center.ward', string='Khoa', readonly=True,
                           states={'InProgress': [('readonly', False)]}, default=_get_default_ward)
    room = fields.Many2one('sh.medical.health.center.ot', string='Phòng', readonly=True,
                           states={'InProgress': [('readonly', False)]})

    evaluation_start_date = fields.Datetime(string='Evalution Date', required=True)
    evaluation_end_date = fields.Datetime(string='Evalution End Date')
    evaluation_type = fields.Selection(EVALUATION_TYPE, string='Evaluation Type', required=True, index=True, default=lambda *a: 'Pre-arraganged Appointment')
    chief_complaint = fields.Char(string='Chief Complaint', size=128, help='Triệu chứng chính')
    notes_complaint = fields.Text(string='Triệu chứng chi tiết')
    services = fields.Many2many('sh.medical.health.center.service', 'sh_evaluation_service_rel', 'evaluation_id',
                                'service_id', store=True, track_visibility='onchange',
                                string='Dịch vụ')
    derived_from = fields.Many2one('sh.medical.physician', string='Physician who escalated the case')
    derived_to = fields.Many2one('sh.medical.physician', string='Physician to whom escalated')
    glycemia = fields.Float(string='Glycemia', help="Last blood glucose level. It can be approximative.")
    hba1c = fields.Float(string='Glycated Hemoglobin', help="Last Glycated Hb level. It can be approximative.")
    cholesterol_total = fields.Integer(string='Last Cholesterol',help="Last cholesterol reading. It can be approximative")
    hdl = fields.Integer(string='Last HDL', help="Last HDL Cholesterol reading. It can be approximative")
    ldl = fields.Integer(string='Last LDL', help="Last LDL Cholesterol reading. It can be approximative")
    tag = fields.Integer(string='Last TAGs', help="Triacylglycerols (triglicerides) level. It can be approximative")

    systolic = fields.Integer(string='Systolic Pressure')
    diastolic = fields.Integer(string='Diastolic Pressure')
    bpm = fields.Integer(string='Heart Rate', help="Heart rate expressed in beats per minute")
    respiratory_rate = fields.Integer(string='Respiratory Rate', help="Respiratory rate expressed in breaths per minute")
    osat = fields.Integer(string='Oxygen Saturation', help="Oxygen Saturation (arterial).")
    malnutrition = fields.Boolean(string='Malnutrition', help="Check this box if the patient show signs of malnutrition. If not associated to a disease, please encode the correspondent disease on the patient disease history. For example, Moderate protein-energy malnutrition, E44.0 in ICD-10 encoding")
    dehydration = fields.Boolean(string='Dehydration', help="Check this box if the patient show signs of dehydration. If not associated to a disease, please encode the correspondent disease on the patient disease history. For example, Volume Depletion, E86 in ICD-10 encoding")
    temperature = fields.Float(string='Temperature (celsius)')
    weight = fields.Float(string='Weight (kg)')
    height = fields.Float(string='Height (cm)')
    bmi = fields.Float(string='Body Mass Index (BMI)')
    head_circumference = fields.Float(string='Head Circumference', help="Head circumference")
    abdominal_circ = fields.Float(string='Abdominal Circumference')
    edema = fields.Boolean(string='Edema', help="Please also encode the correspondent disease on the patient disease history. For example,  R60.1 in ICD-10 encoding")
    petechiae = fields.Boolean(string='Petechiae')
    hematoma = fields.Boolean(string='Hematomas')
    cyanosis = fields.Boolean(string='Cyanosis', help="If not associated to a disease, please encode it on the patient disease history. For example,  R23.0 in ICD-10 encoding")
    acropachy = fields.Boolean(string='Acropachy', help="Check if the patient shows acropachy / clubbing")
    nystagmus = fields.Boolean(string='Nystagmus', help="If not associated to a disease, please encode it on the patient disease history. For example,  H55 in ICD-10 encoding")
    miosis = fields.Boolean(string='Miosis', help="If not associated to a disease, please encode it on the patient disease history. For example,  H57.0 in ICD-10 encoding" )
    mydriasis = fields.Boolean(string='Mydriasis', help="If not associated to a disease, please encode it on the patient disease history. For example,  H57.0 in ICD-10 encoding")
    cough = fields.Boolean(string='Cough', help="If not associated to a disease, please encode it on the patient disease history.")
    palpebral_ptosis = fields.Boolean(string='Palpebral Ptosis', help="If not associated to a disease, please encode it on the patient disease history")
    arritmia = fields.Boolean(string='Arritmias', help="If not associated to a disease, please encode it on the patient disease history")
    heart_murmurs = fields.Boolean(string='Heart Murmurs')
    heart_extra_sounds = fields.Boolean(string='Heart Extra Sounds', help="If not associated to a disease, please encode it on the patient disease history")
    jugular_engorgement = fields.Boolean(string='Tremor', help="If not associated to a disease, please encode it on the patient disease history")
    ascites = fields.Boolean(string='Ascites', help="If not associated to a disease, please encode it on the patient disease history")
    lung_adventitious_sounds = fields.Boolean(string='Lung Adventitious sounds', help="Crackles, wheezes, ronchus..")
    bronchophony = fields.Boolean(string='Bronchophony')
    increased_fremitus = fields.Boolean(string='Increased Fremitus')
    decreased_fremitus = fields.Boolean(string='Decreased Fremitus')
    jaundice = fields.Boolean(string='Jaundice', help="If not associated to a disease, please encode it on the patient disease history")
    lynphadenitis = fields.Boolean(string='Linphadenitis', help="If not associated to a disease, please encode it on the patient disease history")
    breast_lump = fields.Boolean(string='Breast Lumps')
    breast_asymmetry = fields.Boolean(string='Breast Asymmetry')
    nipple_inversion = fields.Boolean(string='Nipple Inversion')
    nipple_discharge = fields.Boolean(string='Nipple Discharge')
    peau_dorange = fields.Boolean(string='Peau d orange',help="Check if the patient has prominent pores in the skin of the breast" )
    gynecomastia = fields.Boolean(string='Gynecomastia')
    masses = fields.Boolean(string='Masses', help="Check when there are findings of masses / tumors / lumps")
    hypotonia = fields.Boolean(string='Hypotonia', help="Please also encode the correspondent disease on the patient disease history.")
    hypertonia = fields.Boolean(string='Hypertonia', help="Please also encode the correspondent disease on the patient disease history.")
    pressure_ulcers = fields.Boolean(string='Pressure Ulcers', help="Check when Decubitus / Pressure ulcers are present")
    goiter = fields.Boolean(string='Goiter')
    alopecia = fields.Boolean(string='Alopecia', help="Check when alopecia - including androgenic - is present")
    xerosis = fields.Boolean(string='Xerosis')
    erithema = fields.Boolean(string='Erithema', help="Please also encode the correspondent disease on the patient disease history.")
    loc = fields.Integer(string='Level of Consciousness', help="Level of Consciousness - on Glasgow Coma Scale :  1=coma - 15=normal")
    loc_eyes = fields.Integer(string='Level of Consciousness - Eyes', help="Eyes Response - Glasgow Coma Scale - 1 to 4", default=lambda *a: 4)
    loc_verbal = fields.Integer(string='Level of Consciousness - Verbal', help="Verbal Response - Glasgow Coma Scale - 1 to 5", default=lambda *a: 5)
    loc_motor = fields.Integer(string='Level of Consciousness - Motor', help="Motor Response - Glasgow Coma Scale - 1 to 6", default=lambda *a: 6)
    violent = fields.Boolean(string='Violent Behaviour', help="Check this box if the patient is agressive or violent at the moment")
    mood = fields.Selection(MOOD, string='Mood', index=True)
    indication = fields.Many2one('sh.medical.pathology', string='Indication', help="Choose a disease for this medicament from the disease list. It can be an existing disease of the patient or a prophylactic.")
    orientation = fields.Boolean(string='Orientation', help="Check this box if the patient is disoriented in time and/or space")
    memory = fields.Boolean(string='Memory', help="Check this box if the patient has problems in short or long term memory")
    knowledge_current_events = fields.Boolean(string='Knowledge of Current Events', help="Check this box if the patient can not respond to public notorious events")
    judgment = fields.Boolean(string='Jugdment', help="Check this box if the patient can not interpret basic scenario solutions")
    abstraction = fields.Boolean(string='Abstraction', help="Check this box if the patient presents abnormalities in abstract reasoning")
    vocabulary = fields.Boolean(string='Vocabulary', help="Check this box if the patient lacks basic intelectual capacity, when she/he can not describe elementary objects")
    calculation_ability = fields.Boolean(string='Calculation Ability',help="Check this box if the patient can not do simple arithmetic problems")
    object_recognition = fields.Boolean(string='Object Recognition', help="Check this box if the patient suffers from any sort of gnosia disorders, such as agnosia, prosopagnosia ...")
    praxis = fields.Boolean(string='Praxis', help="Check this box if the patient is unable to make voluntary movements")
    info_diagnosis = fields.Text(string='Presumptive Diagnosis')
    directions = fields.Text(string='Plan')
    symptom_pain = fields.Boolean(string='Pain')
    symptom_pain_intensity = fields.Integer(string='Pain intensity', help="Pain intensity from 0 (no pain) to 10 (worst possible pain)")
    symptom_arthralgia = fields.Boolean(string='Arthralgia')
    symptom_myalgia = fields.Boolean(string='Myalgia')
    symptom_abdominal_pain = fields.Boolean(string='Abdominal Pain')
    symptom_cervical_pain = fields.Boolean(string='Cervical Pain')
    symptom_thoracic_pain = fields.Boolean(string='Thoracic Pain')
    symptom_lumbar_pain = fields.Boolean(string='Lumbar Pain')
    symptom_pelvic_pain = fields.Boolean(string='Pelvic Pain')
    symptom_headache = fields.Boolean(string='Headache')
    symptom_odynophagia = fields.Boolean(string='Odynophagia')
    symptom_sore_throat = fields.Boolean(string='Sore throat')
    symptom_otalgia = fields.Boolean(string='Otalgia')
    symptom_tinnitus = fields.Boolean(string='Tinnitus')
    symptom_ear_discharge = fields.Boolean(string='Ear Discharge')
    symptom_hoarseness = fields.Boolean(string='Hoarseness')
    symptom_chest_pain = fields.Boolean(string='Chest Pain')
    symptom_chest_pain_excercise = fields.Boolean(string='Chest Pain on excercise only')
    symptom_orthostatic_hypotension = fields.Boolean(string='Orthostatic hypotension', help="If not associated to a disease,please encode it on the patient disease history. For example,  I95.1 in ICD-10 encoding")
    symptom_astenia = fields.Boolean(string='Astenia')
    symptom_anorexia = fields.Boolean(string='Anorexia')
    symptom_weight_change = fields.Boolean(string='Sudden weight change')
    symptom_abdominal_distension = fields.Boolean(string='Abdominal Distension')
    symptom_hemoptysis = fields.Boolean(string='Hemoptysis')
    symptom_hematemesis = fields.Boolean(string='Hematemesis')
    symptom_epistaxis = fields.Boolean(string='Epistaxis')
    symptom_gingival_bleeding = fields.Boolean(string='Gingival Bleeding')
    symptom_rinorrhea = fields.Boolean(string='Rinorrhea')
    symptom_nausea = fields.Boolean(string='Nausea')
    symptom_vomiting = fields.Boolean(string='Vomiting')
    symptom_dysphagia = fields.Boolean(string='Dysphagia')
    symptom_polydipsia = fields.Boolean(string='Polydipsia')
    symptom_polyphagia = fields.Boolean(string='Polyphagia')
    symptom_polyuria = fields.Boolean(string='Polyuria')
    symptom_nocturia = fields.Boolean(string='Nocturia')
    symptom_vesical_tenesmus = fields.Boolean(string='Vesical Tenesmus')
    symptom_pollakiuria = fields.Boolean(string='Pollakiuiria')
    symptom_dysuria = fields.Boolean(string='Dysuria')
    symptom_stress = fields.Boolean(string='Stressed-out')
    symptom_mood_swings = fields.Boolean(string='Mood Swings')
    symptom_pruritus = fields.Boolean(string='Pruritus')
    symptom_insomnia = fields.Boolean(string='Insomnia')
    symptom_disturb_sleep = fields.Boolean(string='Disturbed Sleep')
    symptom_dyspnea = fields.Boolean(string='Dyspnea')
    symptom_orthopnea = fields.Boolean(string='Orthopnea')
    symptom_amnesia = fields.Boolean(string='Amnesia')
    symptom_paresthesia = fields.Boolean(string='Paresthesia')
    symptom_paralysis = fields.Boolean(string='Paralysis')
    symptom_syncope = fields.Boolean(string='Syncope')
    symptom_dizziness = fields.Boolean(string='Dizziness')
    symptom_vertigo = fields.Boolean(string='Vertigo')
    symptom_eye_glasses = fields.Boolean(string='Eye glasses', help="Eye glasses or contact lenses")
    symptom_blurry_vision = fields.Boolean(string='Blurry vision')
    symptom_diplopia = fields.Boolean(string='Diplopia')
    symptom_photophobia = fields.Boolean(string='Photophobia')
    symptom_dysmenorrhea = fields.Boolean(string='Dysmenorrhea')
    symptom_amenorrhea = fields.Boolean(string='Amenorrhea')
    symptom_metrorrhagia = fields.Boolean(string='Metrorrhagia')
    symptom_menorrhagia = fields.Boolean(string='Menorrhagia')
    symptom_vaginal_discharge = fields.Boolean(string='Vaginal Discharge')
    symptom_urethral_discharge = fields.Boolean(string='Urethral Discharge')
    symptom_diarrhea = fields.Boolean(string='Diarrhea')
    symptom_constipation = fields.Boolean(string='Constipation')
    symptom_rectal_tenesmus = fields.Boolean(string='Rectal Tenesmus')
    symptom_melena = fields.Boolean(string='Melena')
    symptom_proctorrhagia = fields.Boolean(string='Proctorrhagia')
    symptom_xerostomia = fields.Boolean(string='Xerostomia')
    symptom_sexual_dysfunction = fields.Boolean(string='Sexual Dysfunction')
    notes = fields.Text(string='Notes')
    # thong tin vat tu
    supplies = fields.One2many('sh.medical.evaluation.supply', 'name', string="Material Information")
    # trang thai
    state = fields.Selection([
        ('InProgress', 'In progress'),
        ('Completed', 'Completed'),
    ], string='Trạng thái',default='InProgress')

    other_bom = fields.Many2many('sh.medical.product.bundle', 'sh_evaluation_bom_rel', 'evaluation_id', 'bom_id',
                                 string='Chọn Bom khác',
                                 domain="[('service_id', 'in', 'services.ids')]")

    #  check công ty hiện tại của người dùng với công ty của phiếu
    check_current_company = fields.Boolean(string='Cty hiện tại', compute='_check_current_company')

    #  domain vật tư và thuốc theo kho của phòng
    supply_domain = fields.Many2many('sh.medical.medicines', string='Supply domain', compute='_get_supply_domain')

    evaluation_services = fields.Many2many('sh.medical.evaluation.services', 'sh_evaluation_services_type_rel', 'evaluation_id', 'evaluation_services_id',
                                 string='Loại tái khám')

    evaluation_team = fields.One2many('sh.medical.evaluation.team', 'name', string='Thành viên tham gia',
                                     help="Thành viên tham gia thăm khám", readonly=False,
                                     states={'Completed': [('readonly', True)]})

    prescription_ids = fields.One2many('sh.medical.prescription', 'evaluation', string='Đơn thuốc', readonly=False,
                                       states={'Completed': [('readonly', True)]})

    @api.depends('institution.his_company')
    def _check_current_company(self):
        for record in self:
            record.check_current_company = True if record.institution.his_company == self.env.company else False

    @api.onchange('room', 'other_bom')
    def _onchange_other_bom(self):
        self.supplies = False
        if self.other_bom:
            vals = []
            check_duplicate = []
            for record in self.other_bom:
                for record_line in record.products.filtered(lambda p: p.note == 'Evaluation'):
                    location = self.room.location_supply_stock
                    if record_line.product_id.medicament_type == 'Medicine':
                        location = self.room.location_medicine_stock
                    # product = record_line.product_id.product_id
                    if location:
                        # available_qty = self.env['stock.quant']._get_available_quantity(product_id=product, location_id=location)
                        # if record_line.uom_id != product.uom_id:
                        #     available_qty = product.uom_id._compute_quantity(available_qty, record_line.uom_id)
                        # qty = min(record_line.quantity, available_qty)
                        qty = record_line.quantity
                        # if qty > 0:
                        mats_id = record_line.product_id.id
                        if mats_id not in check_duplicate:
                            check_duplicate.append(mats_id)
                            vals.append((0, 0, {'supply': mats_id,
                                                'qty': qty,
                                                'uom_id': record_line.uom_id,
                                                'location_id': location.id,
                                                'services': [(4,record.service_id.id)],
                                                'notes': record_line.note}))
                        else:
                            old_supply_index = check_duplicate.index(mats_id)
                            vals[old_supply_index][2]['services'] += [(4,record.service_id.id)]
                            vals[old_supply_index][2]['qty'] += qty
                            # vals[old_supply_index][2]['qty'] = min(qty + vals[old_supply_index][2]['qty'], available_qty)
            self.supplies = vals

    @api.depends('room')
    def _get_supply_domain(self):
        for record in self:
            record.supply_domain = False
            room = record.room
            if room:
                locations = room.location_medicine_stock + room.location_supply_stock
                if locations:
                    products = self.env['stock.quant'].search(
                        [('quantity', '>', 0), ('location_id', 'in', locations.ids)]).filtered(lambda q: q.reserved_quantity < q.quantity).mapped('product_id')
                    if products:
                        medicines = self.env['sh.medical.medicines'].search([('product_id', 'in', products.ids)])
                        record.supply_domain = [(6, 0, medicines.ids)]

    @api.onchange('evaluation_start_date', 'evaluation_end_date')
    def _onchange_date_evaluation(self):
        if self.evaluation_start_date and self.evaluation_end_date:
            if self.evaluation_start_date > self.evaluation_end_date:
                raise UserError(
                    _(
                        'Thông tin không hợp lệ! Thời gian bắt đầu trước thời gian kết thúc thăm khám!'))

    # cộng dồn số lượng vật tư nếu đã nhập rồi
    @api.onchange('supplies')
    def _onchange_supplies(self):
        if self.supplies:
            id_supplies = {}
            inx = 0
            for supply in self.supplies:
                if str(supply.supply.id) in id_supplies:
                    # cộng dồn số lượng
                    qty_sup = self.supplies[id_supplies[str(supply.supply.id)]].qty_used + supply.qty_used
                    self.supplies[id_supplies[str(supply.supply.id)]].qty_used = qty_sup
                    self.supplies = [(2, supply.id, False)]
                else:
                    # chưa có
                    id_supplies[str(supply.supply.id)] = inx
                inx += 1

    @api.onchange('institution')
    def _onchange_institution(self):
        # set khoa mac dinh la khoa phau thuat cua co so y te
        if self.institution:
            sur_dep = self.env['sh.medical.health.center.ward'].search(
                [('institution', '=', self.institution.id), ('type', '=', 'Surgery')], limit=1)
            self.ward = sur_dep
            self.room = False

    @api.onchange('ward')
    def _onchange_ward(self):
        if self.ward:
            self.room = False

    def reset_all_supply(self):
        for evaluation in self.filtered(lambda sp: sp.state not in ['Completed']):
            evaluation.supplies = False

    def reverse_materials(self):
        num_of_location = len(self.supplies.mapped('location_id'))
        pick_need_reverses = self.env['stock.picking'].search(
            [('origin', 'ilike', 'THBN - %s - %s' % (self.name, self.walkin.name)),
             ('company_id', '=', self.env.company.id)], order='create_date DESC', limit=num_of_location)
        if pick_need_reverses:
            for pick_need_reverse in pick_need_reverses:
                date_done = pick_need_reverse.date_done
                fail_pick_count = self.env['stock.picking'].search_count([('name', 'ilike', pick_need_reverse.name), ('company_id', '=', self.env.company.id)])
                pick_need_reverse.name += '-FP%s' % fail_pick_count
                pick_need_reverse.move_ids_without_package.write(
                    {'reference': pick_need_reverse.name})  # sửa cả trường tham chiếu của move.line (Dịch chuyển kho)

                new_wizard = self.env['stock.return.picking'].new(
                    {'picking_id': pick_need_reverse.id})  # tạo new wizard chưa lưu vào db
                new_wizard._onchange_picking_id()  # chạy hàm onchange với tham số ở trên
                wizard_vals = new_wizard._convert_to_write(
                    new_wizard._cache)  # lấy dữ liệu sau khi đã chạy qua onchange
                wizard = self.env['stock.return.picking'].with_context(reopen_flag=True, no_check_quant=True).create(
                    wizard_vals)
                new_picking_id, pick_type_id = wizard._create_returns()
                new_picking = self.env['stock.picking'].browse(new_picking_id)
                # check chính xác tại tủ xuất
                new_picking.with_context(exact_location=True).action_assign()
                for move_line in new_picking.move_ids_without_package:
                    for move_live_detail in move_line.move_line_ids:
                        move_live_detail.qty_done = move_live_detail.product_uom_qty
                    # move_line.quantity_done = move_line.product_uom_qty
                new_picking.with_context(force_period_date=date_done).button_validate()

                # sua ngay hoan thanh
                for move_line in new_picking.move_ids_without_package:
                    move_line.move_line_ids.write(
                        {'date': date_done})  # sửa ngày hoàn thành ở stock move line
                new_picking.move_ids_without_package.write(
                    {'date': date_done})  # sửa ngày hoàn thành ở stock move

                new_picking.date_done = date_done
                new_picking.sci_date_done = date_done

    def set_to_completed(self):
        flag_check = False
        if self.evaluation_services:
            for eval_ser in self.evaluation_services:
                if eval_ser.has_supply:
                    flag_check = True
                    break
        if flag_check:
            if not self.supplies:
                raise ValidationError('Bạn phải nhập VTTH cho phiếu trước khi xác nhận hoàn thành!')

        #trừ vtth tái khám theo tủ
        if self.evaluation_end_date:
            evaluation_end_date = self.evaluation_end_date
        else:
            evaluation_end_date = fields.Datetime.now()

        vals = {}
        validate_str = ''
        for mat in self.supplies:
            if mat.qty_used > 0:  # CHECK SO LUONG SU DUNG > 0
                quantity_on_hand = self.env['stock.quant']._get_available_quantity(mat.supply.product_id,
                                                                                   mat.location_id)  # check quantity trong location
                if mat.uom_id != mat.supply.uom_id:
                    mat.write({'qty_used': mat.uom_id._compute_quantity(mat.qty_used, mat.supply.uom_id),
                               'uom_id': mat.supply.uom_id.id})  # quy so suong su dung ve don vi chinh cua san pham

                if quantity_on_hand < mat.qty_used:
                    validate_str += "+ ""[%s]%s"": Còn %s %s tại ""%s"" \n" % (
                        mat.supply.default_code, mat.supply.name, str(quantity_on_hand), str(mat.uom_id.name),
                        mat.location_id.name)
                else:  # truong one2many trong stock picking de tru cac product trong inventory
                    sub_vals = {
                        'name': 'THBN: ' + mat.supply.product_id.name,
                        'origin': str(self.walkin.id) + "-" + str(self.services.ids),  # mã pk-mã dịch vụ
                        'date': evaluation_end_date,
                        'company_id': self.env.company.id,
                        'date_expected': evaluation_end_date,
                        'product_id': mat.supply.product_id.id,
                        'product_uom_qty': mat.qty_used,
                        'product_uom': mat.uom_id.id,
                        'location_id': mat.location_id.id,
                        'location_dest_id': self.patient.partner_id.property_stock_customer.id,
                        'partner_id': self.patient.partner_id.id,
                        # xuat cho khach hang/benh nhan nao
                    }

                    if not vals.get(str(mat.location_id.id)):
                        vals[str(mat.location_id.id)] = [sub_vals]
                    else:
                        vals[str(mat.location_id.id)].append(sub_vals)

        # neu co vat tu tieu hao
        if vals and validate_str == '':
            # tao phieu xuat kho
            picking_type = self.env['stock.picking.type'].search([('code', '=', 'outgoing'),
                                                                  ('warehouse_id', '=',
                                                                   self.institution.warehouse_ids[0].id)],
                                                                 limit=1).id
            for location_key in vals:
                pick_note = 'THBN - %s - %s - %s' % (self.name, self.walkin.name, location_key)
                pick_vals = {'note': pick_note,
                             'origin': pick_note,
                             'partner_id': self.patient.partner_id.id,
                             'patient_id': self.patient.id,
                             'picking_type_id': picking_type,
                             'location_id': int(location_key),
                             'location_dest_id': self.patient.partner_id.property_stock_customer.id,
                             'date_done': evaluation_end_date,
                             # xuat cho khach hang/benh nhan nao
                             'immediate_transfer': True,
                             # 'move_ids_without_package': vals[location_key]
                             }
                fail_pick_name = self.env['stock.picking'].search(
                    [('origin', 'ilike', 'THBN - %s - %s - %s' % (self.name, self.walkin.name, location_key))],
                    limit=1).name
                if fail_pick_name:
                    pick_vals['name'] = fail_pick_name.split('-', 1)[0]
                stock_picking = self.env['stock.picking'].create(pick_vals)
                for move_val in vals[location_key]:
                    move_val['name'] = stock_picking.name + " - " + move_val['name']
                    move_val['picking_id'] = stock_picking.id
                    self.env['stock.move'].create(move_val)

                # KO TU DONG XUAT KHO NUA MA CHI TAO PHIEU XUAT THOI
                stock_picking.with_context(exact_location=True).action_assign()  # ham check available trong inventory
                for move_line in stock_picking.move_ids_without_package:
                    for move_live_detail in move_line.move_line_ids:
                        move_live_detail.qty_done = move_live_detail.product_uom_qty
                stock_picking.with_context(force_period_date=evaluation_end_date).sudo().button_validate()  # ham tru product trong inventory, sudo để đọc stock.valuation.layer

                # sua ngay hoan thanh
                for move_line in stock_picking.move_ids_without_package:
                    move_line.move_line_ids.write({'date': evaluation_end_date})  # sửa ngày hoàn thành ở stock move line
                stock_picking.move_ids_without_package.write(
                    {'date': evaluation_end_date})  # sửa ngày hoàn thành ở stock move
                stock_picking.date_done = evaluation_end_date

                stock_picking.create_date = self.evaluation_start_date
        elif validate_str != '':
            raise ValidationError(_(
                "Các loại Thuốc và Vật tư sau đang không đủ số lượng tại tủ xuất:\n" + validate_str + "Hãy liên hệ với quản lý kho!"))

        self.write({'state': 'Completed', 'evaluation_end_date': evaluation_end_date})

        # cap nhat vat tu cho phieu kham
        self.walkin.update_walkin_material()

    def set_to_inprogress(self):
        #mở lại phiếu
        if self.state == 'Completed':
            self.reverse_materials()
            res = self.write({'state': 'InProgress'})
        else:
            if self.evaluation_start_date:
                evaluation_start_date = self.evaluation_start_date
            else:
                evaluation_start_date = datetime.datetime.now()

            res = self.write({'state': 'InProgress', 'evaluation_start_date': evaluation_start_date})

    @api.model
    def create(self,vals):
        sequence = self.env['ir.sequence'].next_by_code('sh.medical.evaluation.%s'% vals['institution'])
        if not sequence:
            raise ValidationError(_('Định danh phiếu Thăm khám của Cơ sở y tế này đang không tồn tại!'))
        vals['name'] = sequence

        res = super(SHealthPatientEvaluation, self).create(vals)
        return res

    def write(self, vals):
        res = super(SHealthPatientEvaluation, self).write(vals)
        for record in self.with_env(self.env(su=True)):
            if vals.get(' evaluation_start_date') or vals.get('evaluation_end_date'):
                evaluation_start_date = vals.get('evaluation_start_date') or record.evaluation_start_date
                evaluation_end_date = vals.get('evaluation_end_date') or record.evaluation_end_date

                # format to date
                if isinstance(evaluation_start_date, str):
                    evaluation_start_date = datetime.datetime.strptime(evaluation_start_date, '%Y-%m-%d %H:%M:%S')
                if isinstance(evaluation_end_date, str):
                    evaluation_end_date = datetime.datetime.strptime(evaluation_end_date, '%Y-%m-%d %H:%M:%S')

                if evaluation_start_date and evaluation_end_date and ( evaluation_start_date > evaluation_end_date):
                    raise UserError(_('Thông tin không hợp lệ! Ngày giờ bắt đầu phải trước ngày kết thúc!'))

            if vals.get('services'):
                # check dịch vụ đổi trong phiếu chuyên khoa: nếu xóa sẽ xóa dv sẽ xóa ở dv ở thành viên tham gia
                # thành viên tham gia
                for evaluation_mem in record.evaluation_team.mapped('service_performances').ids:
                    if evaluation_mem not in record.services.ids:
                        record.evaluation_team.write({'service_performances': [(3, evaluation_mem)]})

                # vtth
                for evaluation_sur in record.supplies.mapped('services').ids:
                    if evaluation_sur not in record.services.ids:
                        record.supplies.write({'services': [(3, evaluation_sur)]})

        return res

    @api.onchange('height','weight')
    def onchange_height_weight(self):
        res = {}
        if self.height:
            self.bmi = self.weight / ((self.height/100)**2)
        else:
            self.bmi = 0
        return res

    @api.onchange('loc_motor','loc_eyes','loc_verbal')
    def onchange_loc(self):
        res = {}
        self.loc = self.loc_motor + self.loc_eyes + self.loc_verbal
        return res

# vat tu tieu hao cho moi lan tham kham ...
class SHealthEvaluationSupply(models.Model):
    _name = "sh.medical.evaluation.supply"
    _description = "Supplies related to the evaluation"

    MEDICAMENT_TYPE = [
        ('Medicine', 'Medicine'),
        ('Supplies', 'Supplies'),
    ]

    name = fields.Many2one('sh.medical.evaluation', string='Evaluation')
    qty = fields.Float(string='Initial Quantity',digits=dp.get_precision('Product Unit of Measure'), required=True, help="Initial Quantity", default=lambda *a: 0)
    # qty_used = fields.Integer(string='Quantity',digits=dp.get_precision('Product Unit of Measure'), required=True, help="Quantity used", default=lambda *a: 0)
    uom_id = fields.Many2one('uom.uom', 'Unit of Measure')
    supply = fields.Many2one('sh.medical.medicines', string='Supply', required=True, help="Supply to be used in this evaluation", domain=lambda self:[('categ_id','child_of',self.env.ref('shealth_all_in_one.sh_sci_medical_product').id)])
    notes = fields.Char(string='Notes')

    qty_avail = fields.Float(string='Số lượng khả dụng', required=True, help="Số lượng khả dụng trong toàn viện",
                             compute='compute_available_qty_supply')
    qty_in_loc = fields.Float(string='Số lượng tại tủ', required=True, help="Số lượng khả dụng trong tủ trực",
                              compute='compute_available_qty_supply_in_location')
    is_warning_location = fields.Boolean('Cảnh báo tại tủ', compute='compute_available_qty_supply_in_location')
    qty_used = fields.Float(string='Actual quantity used', required=True, help="Actual quantity used",
                            default=lambda *a: 1,digits=dp.get_precision('Product Unit of Measure'))
    location_id = fields.Many2one('stock.location', 'Stock location', domain="[('usage', '=', 'internal')]")
    medicament_type = fields.Selection(MEDICAMENT_TYPE, related="supply.medicament_type", string='Medicament Type',
                                       store=True)

    sequence = fields.Integer('Sequence',
                              default=lambda self: self.env['ir.sequence'].next_by_code('sequence'))  # Số thứ tự

    services = fields.Many2many('sh.medical.health.center.service', 'sh_evaluation_supply_service_rel',
                                track_visibility='onchange',
                                string='Dịch vụ thực hiện')
    service_related = fields.Many2many('sh.medical.health.center.service', 'sh_evaluation_supply_service_related_rel',
                                       related="name.services",
                                       string='Dịch vụ liên quan')

    @api.depends('supply', 'uom_id')
    def compute_available_qty_supply(self):  # so luong kha dung toan vien
        for record in self:
            if record.supply:
                record.qty_avail = record.uom_id._compute_quantity(record.supply.qty_available,
                                                                   record.supply.uom_id) if record.uom_id != record.supply.uom_id else record.supply.qty_available
            else:
                record.qty_avail = 0

    @api.depends('supply', 'location_id', 'qty_used', 'uom_id')
    def compute_available_qty_supply_in_location(self):  # so luong kha dung tai tu
        for record in self:
            if record.supply:
                quantity_on_hand = self.env['stock.quant'].with_user(1)._get_available_quantity(
                    record.supply.product_id,
                    record.location_id)  # check quantity trong location

                record.qty_in_loc = record.uom_id._compute_quantity(quantity_on_hand,
                                                                    record.supply.uom_id) if record.uom_id != record.supply.uom_id else quantity_on_hand
            else:
                record.qty_in_loc = 0

            record.is_warning_location = True if record.qty_used > record.qty_in_loc else False

    @api.onchange('qty_used', 'supply')
    def onchange_qty_used(self):
        if self.qty_used <= 0 and self.supply:
            raise UserError(_("Số lượng nhập phải lớn hơn 0!"))

    @api.onchange('supply')
    def _change_product_id(self):
        self.uom_id = self.supply.uom_id
        self.services = self.name.services
        domain = {'domain': {'uom_id': [('category_id', '=', self.supply.uom_id.category_id.id)]}}
        if self.medicament_type == 'Medicine':
            self.location_id = self.name.room.location_medicine_stock.id
            domain['domain']['location_id'] = [('location_institution_type', '=', 'medicine'),
                                               ('company_id', '=', self.name.institution.his_company.id)]
        elif self.medicament_type == 'Supplies':
            self.location_id = self.name.room.location_supply_stock.id
            domain['domain']['location_id'] = [('location_institution_type', '=', 'supply'),
                                               ('company_id', '=', self.name.institution.his_company.id)]

        print(domain)
        return domain

    @api.onchange('uom_id')
    def _change_uom_id(self):
        if self.uom_id.category_id != self.supply.uom_id.category_id:
            self.uom_id = self.supply.uom_id
            raise Warning(
                _('The Supply Unit of Measure and the Material Unit of Measure must be in the same category.'))

# Inheriting Patient module to add "Evaluation" screen reference
class SHealthPatient(models.Model):
    _inherit = 'sh.medical.patient'

    evaluation_ids = fields.One2many('sh.medical.evaluation', 'patient', string='Evaluation')

# Inheriting Prescription module to add "Evaluation" screen reference
class SHealthPrescriptionEvaluation(models.Model):
    _inherit = 'sh.medical.prescription'

    evaluation = fields.Many2one('sh.medical.evaluation', string='Thăm khám', ondelete='cascade')


# Inheriting Appointment module to add "Evaluation" screen reference
class SHealthAppointment(models.Model):
    _inherit = 'sh.medical.appointment'

    evaluation_ids = fields.One2many('sh.medical.evaluation', 'appointment', string='Evaluation', readonly=True, states={'Scheduled': [('readonly', False)]})
