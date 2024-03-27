# -*- coding: utf-8 -*-
###############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech-Receptives(<http://www.techreceptives.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression


class OpStudentCourse(models.Model):
    _name = "op.student.course"
    _description = "Student Course Details"

    def get_student_domain(self):
        domain = [('internal', '=', True)] if self.env.context.get('default_internal') else [('internal', '=', False)]
        return domain

    student_id = fields.Many2one('op.student', 'Student', ondelete="cascade",
                                 domain=lambda self: self.get_student_domain())
    course_id = fields.Many2one('op.course', 'Course', related='batch_id.course_id', store=True)
    course_code = fields.Char('Course code', related='course_id.code', store=True)
    batch_id = fields.Many2one('op.batch', 'Batch')
    batch_code = fields.Char('Batch code', related='batch_id.code')
    roll_number = fields.Char('Roll Number')
    subject_ids = fields.Many2many('op.subject', string='Subjects')
    status = fields.Selection(
        [('not', 'Not learned'), ('trial', 'Trial'), ('reserve', 'Reserved'), ('study', 'Studying'),
         ('finish', 'Finished'), ('cancel', 'Cancel')],
        string='Status', default='not')
    batch_start_date = fields.Date('Start date', related='batch_id.start_date', store=True)

    # added for internal course
    department_id = fields.Many2one('res.brand', 'Department')
    job_id = fields.Many2one('hr.job', 'Job position', related='student_id.job_id', store=True)
    faculty_id = fields.Many2one('op.faculty', 'Faculty', related='batch_id.faculty_id', store=True)

    @api.onchange('student_id')
    def onchange_student_id(self):
        if self.student_id and self.student_id.emp_id and self.student_id.emp_id.root_department:
            self.department_id = self.student_id.emp_id.root_department
        else:
            self.department_id = False

    @api.model
    def create_internal_student_cron(self):
        emp_not_student = self.env['hr.employee'].search([('student_id', '=', False)], limit=150)
        for emp in emp_not_student:
            course_list = self.env['op.course'].search(['|', ('department_ids', 'in', [emp.department_id.id]),
                                                        ('job_ids', 'in', [emp.job_id.id])])
            vals = {'image_1920': emp.image_1920,
                    'name': emp.name,
                    'internal': True,
                    'emp_id': emp.id,
                    'student_id': emp.employee_id,
                    'department_id': emp.department_id.id,
                    'gender': list(emp.gender)[0],
                    'email': emp.work_email or '%s email' % emp.name,
                    'phone': emp.work_phone,
                    'mobile': emp.mobile_phone,
                    'hometown': emp.place_of_birth,
                    'birth_date': emp.birthday or '1990-01-01',
                    'nationality': emp.country_id.id or False}
            if emp.user_id:
                vals.update({'user_id': emp.user_id.id,
                             'partner_id': emp.user_id.partner_id.id})
            student = self.env['op.student'].create(vals)
            for course in course_list:
                student_course = self.env['op.student.course'].create({'student_id': student.id,
                                                                       'status': 'not'})
                student_course.write({'course_id': course.id})

    @api.model
    def update_internal_student_course(self):
        # todo: try to reduce search results
        internal_students = self.env['op.student'].search([('internal', '=', True)])
        for student in internal_students:
            needed_courses_list = self.env['op.course'].search(
                ['|', ('department_ids', 'in', [student.emp_id.department_id.id]),
                 ('job_ids', 'in', [student.emp_id.job_id.id])])
            student_courses = self.env['op.student.course'].search([('student_id', '=', student.id)])
            registered_course = [record.course_id.id for record in student_courses]
            for record in student_courses:
                if record.course_id not in needed_courses_list and record.status == 'not':
                    record.unlink()
            for course in needed_courses_list:
                if course.id not in registered_course:
                    student_course = self.env['op.student.course'].create({'student_id': student.id,
                                                                           'status': 'not'})
                    student_course.write({'course_id': course.id})

    _sql_constraints = [
        ('unique_name_roll_number_id',
         'unique(roll_number,course_id,batch_id,student_id)',
         'Roll Number & Student must be unique per Batch!'),
        ('unique_name_roll_number_course_id',
         'unique(roll_number,course_id,batch_id)',
         'Roll Number must be unique per Batch!'),
        ('unique_name_roll_number_student_id',
         'unique(student_id,course_id,batch_id)',
         'Student must be unique per Batch!'),
    ]


class OpStudent(models.Model):
    _name = "op.student"
    _description = "Student"
    _inherit = "mail.thread"
    _inherits = {"res.partner": "partner_id"}

    def _default_student_id(self):
        if not self.env.context.get('default_internal'):
            return self.env['ir.sequence'].next_by_code('op.student')

    middle_name = fields.Char('Middle Name', size=128)
    last_name = fields.Char('Last Name', size=128)
    birth_date = fields.Date('Birth Date')
    blood_group = fields.Selection([
        ('A+', 'A+ve'),
        ('B+', 'B+ve'),
        ('O+', 'O+ve'),
        ('AB+', 'AB+ve'),
        ('A-', 'A-ve'),
        ('B-', 'B-ve'),
        ('O-', 'O-ve'),
        ('AB-', 'AB-ve')
    ], string='Blood Group')
    gender = fields.Selection([
        ('m', 'Male'),
        ('f', 'Female'),
        ('o', 'Other')
    ], 'Gender', required=True, default='m')
    nationality = fields.Many2one('res.country', 'Nationality')
    emergency_contact = fields.Many2one('res.partner', 'Emergency Contact')
    visa_info = fields.Char('Visa Info', size=64)
    id_number = fields.Char('ID Card Number', size=64)
    already_partner = fields.Boolean('Already Partner')
    partner_id = fields.Many2one('res.partner', 'Partner',
                                 required=True, ondelete="cascade")
    gr_no = fields.Char("GR Number", size=20)
    category_id = fields.Many2one('op.category', 'Category')
    course_detail_ids = fields.One2many('op.student.course', 'student_id',
                                        'Course Details',
                                        track_visibility='onchange')

    internal = fields.Boolean('Internal')
    emp_id = fields.Many2one('hr.employee', string='Employee', domain=[('student_id', '=', False)])
    department_id = fields.Many2one('hr.department', string='Department', related='emp_id.department_id', store=True)
    job_id = fields.Many2one('hr.job', string='Job position', related='emp_id.job_id', store=True)
    academic_year = fields.Many2one('op.academic.year', string='Academic year')

    hometown = fields.Char('Home town')
    ethnic = fields.Char('Ethnic')
    religion = fields.Char('Religion')
    communist_date = fields.Date('Ngày vào Đảng')
    official_communist = fields.Date('Ngày chính thức')
    youth_union_date = fields.Date('Ngày vào Đoàn')
    academic_level = fields.Char('Academic level')
    objects = fields.Char('Thuộc diện đối tượng')
    job = fields.Char('Job')
    father = fields.Char('Father')
    father_job = fields.Char('Job')
    mother = fields.Char('Mother')
    mother_job = fields.Char("Job")
    spouse = fields.Char('Spouse')
    spouse_job = fields.Char('Job')
    emergency_contact2 = fields.Char('Emergency contact')
    emergency_phone = fields.Char('Emergency phone')

    student_id = fields.Char('Student ID', default=_default_student_id)
    institute = fields.Selection([('hn', 'Hà Nội'), ('hcm', 'Hồ Chí Minh')])
    institute_id = fields.Many2one('op.institute', 'Institute')

    _sql_constraints = [
        ('unique_visa',
         'unique(visa_info)',
         'Visa / ID number must be unique per student!'),
        ('employee_unique',  # constrain for unique emp_id
         'unique(emp_id)',
         'This employee is already linked to a student profile.')
    ]

    # onchange emp_id
    @api.onchange('internal')
    def _onchange_internal(self):
        if not self.internal:
            self.emp_id = False

    @api.onchange('internal', 'emp_id')
    def _onchange_emp_id(self):
        if self.internal and self.emp_id:
            self.student_id = self.emp_id.id
            self.image_1920 = self.emp_id.image_1920 or False
            self.name = str(self.emp_id.name).split()[0] or self.emp_id.name
            self.last_name = str(self.emp_id.name).split(None, 1)[1] if ' ' in self.emp_id.name else '.'
            self.gender = list(self.emp_id.gender)[0] or False
            self.email = self.emp_id.work_email or False
            self.phone = self.emp_id.work_phone or False
            self.mobile = self.emp_id.mobile_phone or False
            self.birth_date = self.emp_id.birthday or False
            self.nationality = self.country_id or False
            self.department_id = self.emp_id.department_id or False
        else:
            self.name = False
            self.last_name = False
            self.gender = False
            self.email = False
            self.phone = False
            self.mobile = False
            self.birth_date = False
            self.nationality = False
            self.department_id = False

    # @api.multi
    # @api.constrains('birth_date')
    # def _check_birthdate(self):
    #     for record in self:
    #         if record.birth_date > fields.Date.today():
    #             raise ValidationError(_(
    #                 "Birth Date can't be greater than current date!"))

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Students'),
            'template': '/openeducat_core/static/xls/op_student.xls'
        }]

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', '|', '|', ('name', operator, name), ('student_id', operator, name),
                      ('email', operator, name), ('phone', operator, name)]
        students = self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
        return self.browse(students).name_get()

    def name_get(self):
        res = []
        for student in self:
            if student.student_id:
                name = '[' + student.student_id + '] ' + student.name
            else:
                name = student.name
            res.append((student.id, name))
        return res
