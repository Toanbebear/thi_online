# -*- coding: utf-8 -*-

from odoo import fields, api, models
from odoo.exceptions import UserError
from odoo.tools.translate import _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, AccessError, Warning
from werkzeug import urls

class Applicant(models.Model):
    _inherit = "hr.applicant"

    recruit_period = fields.Many2one('hr.recruitment.period', 'Recruitment period', compute='_get_recruit_period', store=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')], string='Giới tính', default="male")
    birthday = fields.Date('Ngày sinh')
    address = fields.Char('Địa chỉ')
    qualification = fields.Char('Trình độ(kinh nghiệm)')
    college = fields.Char('Trường học')
    last_workplace = fields.Char('Nơi làm việc gần nhất')
    workplace = fields.Char('Tỉnh/thành muốn làm việc')
    social_facebook = fields.Char('Facebook')
    part = fields.Selection([('100', 'Care 100%'), ('75', 'Care 75%'), ('50', 'Care 50%'), ('25', 'Care 25%')], string='Vai trò',
                              default="100")
    applicant_state = fields.One2many('hr.applicant.state', 'applicant_id', 'Giai đoạn')
    marital = fields.Selection([
        ('single', 'Chưa kết hôn'),
        ('married', 'Đã kết hôn'),
        ('cohabitant', 'Đồng giới'),
        ('widower', 'Góa'),
        ('divorced', 'Ly hôn')
    ], string='Tình trạng hôn nhân', groups="hr.group_hr_user", default='single')
    salary_expected = fields.Integer("Mức lương mong đợi", help="Salary Expected by Applicant")
    salary_proposed = fields.Integer("Mức lương đề xuất", help="Salary Proposed by the Organisation")
    created_date = fields.Datetime("Ngày tạo", default=fields.Datetime.now())

    @api.onchange('applicant_state')
    def action_change_state(self):
        for rec in self.applicant_state:
            if rec.result == 'pass':
                self.stage_id = rec.stage_id


    @api.depends('job_id')
    def _get_recruit_period(self):
        for record in self:
            if record.job_id and not record.emp_id and record.job_id.periods:
                record.recruit_period = record.job_id.periods[-1]
                # if record.job_id and record.job_id.periods:
                #     if record.job_id.periods[-1].expected_recruitment == record.job_id.periods[-1].employees_num:
                #         raise UserError(_('No recruitment currently opened for this job.'))
                #     else:
                #         record.recruit_period = record.job_id.periods[-1]
                # else:
                #     raise UserError(_('No recruitment currently opened for this job.'))
            else:
                record.recruit_period = False

    def website_form_input_filter(self, request, values):
        if 'partner_name' in values:
            values.setdefault('name', values['partner_name'])
        return values

    def archive_applicant(self):
        self.write({'active': False})
        template = self.env.ref('hr_recruitment.email_template_data_applicant_refuse')
        mail_values = template.generate_email(self.id)
        mail_values['email_from'] = self.env['ir.mail_server'].sudo().search([], limit=1).smtp_user  # Todo: check back later
        mail = self.env['mail.mail'].create(mail_values)
        mail.send()

    @api.model
    def create(self, vals):
        partner_id = self.env['res.partner'].create({
            'name': vals.get('name'),
            'email': vals.get('email_from'),
            'phone': vals.get('partner_phone'),
            'mobile': vals.get('partner_mobile')
        })
        vals['partner_id'] = partner_id.id
        return super(Applicant, self).create(vals)

    def write(self, vals):
        for record in self:
            if vals.get('description'):
                if 'g-recaptcha-response' in vals.get('description'):
                    template = self.env.ref('hr_recruitment.email_template_data_applicant_congratulations')
                    mail_values = template.generate_email(record.id)
                    mail_values['email_from'] = self.env['ir.mail_server'].sudo().search([], limit=1).smtp_user  # Todo: check back later
                    mail = self.env['mail.mail'].create(mail_values)
                    mail.send()
                    return
            else:
                return super(Applicant, record).write(vals)

    def action_get_created_employee(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window'].for_xml_id('hr', 'open_view_employee_list')
        action['res_id'] = self.mapped('emp_id').ids[0]
        return action

    def create_employee_from_applicant(self):
        """ Create an hr.employee from the hr.applicants """
        employee = False
        for applicant in self:
            contact_name = False
            if applicant.partner_id:
                contact_name = applicant.partner_id.name_get()[0][1]
            else:
                new_partner_id = self.env['res.partner'].create({
                    'name': applicant.name,
                    'email': applicant.email_from,
                    'phone': applicant.partner_phone,
                    'mobile': applicant.partner_mobile
                })
            if applicant.job_id and (applicant.partner_name or contact_name):
                applicant.job_id.write({'no_of_hired_employee': applicant.job_id.no_of_hired_employee + 1})
                employee = self.env['hr.employee'].create({
                    'name': applicant.name,
                    'job_id': applicant.job_id.id,
                    'group_job': applicant.job_id.group_job.id,
                    'hr_user_id': applicant.user_id.id,
                    'emergency_contact': applicant.address,
                    'department_id': applicant.department_id.id or False,
                    'email': self.email_from,
                    'gender': applicant.gender,
                    'study_school': applicant.college,
                    'study_field': applicant.qualification,
                    'birthday': applicant.birthday,
                    'marital': applicant.marital,
                    'company_id': applicant.company_id.id,
                    'mobile_phone': self.partner_phone})
                applicant.write({'emp_id': employee.id})
                applicant.job_id.message_post(
                    body=_(
                        'New Employee %s Hired') % applicant.partner_name if applicant.partner_name else applicant.name,
                    subtype="hr_recruitment.mt_job_applicant_hired")
            else:
                raise UserError(_('You must define an Applied Job and a Contact Name for this applicant.'))

        employee_action = self.env.ref('hr.open_view_employee_list')
        dict_act_window = employee_action.read([])[0]
        dict_act_window['context'] = {'form_view_initial_mode': 'edit'}
        dict_act_window['res_id'] = employee.id
        return dict_act_window

class ApplicantState(models.Model):
    _name = "hr.applicant.state"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Giai đoạn ứng viên"

    applicant_id = fields.Many2one('hr.applicant', string='Ứng viên')
    stage_id = fields.Many2one('hr.recruitment.stage', string="Giai đoạn", domain=[('id', '!=', '1')])
    result = fields.Selection([('fail', 'Loại'), ('wait', 'Chờ xét thêm'), ('pass', 'Đạt')], string='Kết quả')
    partner_ids = fields.Many2many('hr.employee', string='Người phỏng vấn')
    start = fields.Datetime('Ngày bắt đầu', required=True, help="Start date of an event, without time for full days events")
    stop = fields.Datetime('Ngày kết thúc', required=True, help="Stop date of an event, without time for full days events")
    location = fields.Char('Địa điểm', help="Location of Event")
    description = fields.Text('Ghi chú')
    attachment_ids = fields.Many2many('ir.attachment', string='File đính kèm')
    partner_id = fields.Many2one('res.partner', string='Ứng viên', related='applicant_id.partner_id')
    user_id = fields.Many2one('res.users', string='Phụ trách', related='applicant_id.user_id')

    _sql_constraints = [
        ('applicant_stage_uniq', 'unique(applicant_id, stage_id)',
         'Đã tồn tại giai đoạn phỏng vấn với ứng viên này!!!!'),
    ]

    @api.constrains('start', 'stop')
    def _check_value(self):
        for item in self:
            if item.stop < item.start:
                raise ValidationError("Ngày bắt đầu không hợp lệ!!!")

    def action_applicant_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('sci_hrms', 'email_template_aplicant_state')[1]
        except ValueError:
            template_id = False
        try:
            # compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
            compose_form_id = self.env.ref('email_compose_message_wizard_form').id
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'hr.applicant.state',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
