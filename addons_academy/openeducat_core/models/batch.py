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
from datetime import date


class OpBatch(models.Model):
    _name = "op.batch"
    _inherit = "mail.thread"
    _description = "OpenEduCat Batch"

    def faculty_domain(self):
        if self._context.get('internal'):
            return [('full_time', '=', False)]
        else:
            return [('full_time', '=', True)]

    code = fields.Char('Code', required=True, copy=False)
    name = fields.Char('Name', required=True)
    start_date = fields.Date(
        'Start Date', required=True, default=date.today())
    end_date = fields.Date('End Date')
    course_id = fields.Many2one('op.course', 'Course', required=True)

    max_absence = fields.Integer('Maximum absences')
    min_attendance = fields.Integer('Minimum attendance')
    student_course = fields.One2many('op.student.course', 'batch_id', 'Student details')
    tutor_fee = fields.Float('Tutor fee per lesson')
    num_lessons = fields.Integer('Number of lessons')
    teacher_cost = fields.Float('Total tutor cost', compute='_get_teacher_cost')
    faculty_bom_cost = fields.Float('Faculty BOM cost', compute='_get_faculty_bom_cost')
    currency_id = fields.Many2one(
        'res.currency', 'Currency',
        default=lambda self: self.env.user.company_id.currency_id.id,
        required=True)
    academic_year = fields.Many2one('op.academic.year', string='Academic year')

    trial = fields.Boolean('Học thử')
    internal = fields.Boolean('Internal', related='course_id.internal', store=True)
    emp_ids = fields.Many2many('hr.employee', string='Employees')
    faculty_bom = fields.One2many('products.line', 'batch_id', string='Faculty BOM')
    products_domain = fields.Many2many('product.product', string='P domain', compute='_get_products_domain')

    institute = fields.Many2one('op.institute', string='Institute')
    faculty_id = fields.Many2one('op.faculty', string='Main faculty', domain=lambda self: self.faculty_domain())
    num_students = fields.Integer('Number of students', compute='_get_num_students_status', store=True)  # for reporting
    status = fields.Selection([('ongoing', 'Ongoing'), ('finish', 'Finished')], 'Status', default='ongoing',
                              compute='_get_num_students_status')

    _sql_constraints = [
        ('unique_batch_code',
         'unique(code)', 'Code should be unique per batch!')]

    @api.depends('student_course')
    def _get_num_students_status(self):
        for record in self:
            record.num_students = len(record.student_course)
            if len(record.student_course) > 0 and len(record.student_course) == len(
                    record.student_course.filtered(lambda s: s.status == 'finish')):
                record.status = 'finish'
            else:
                record.status = 'ongoing'

    def name_get(self):
        return [(batch.id, batch.code + ' - ' + batch.name) for batch in self]

    @api.depends('faculty_bom')
    def _get_products_domain(self):
        for record in self:
            if len(record.faculty_bom) > 0:
                record.products_domain = [
                    (6, 0, [product.product.id for product in record.faculty_bom if product.product])]
            else:
                record.products_domain = False

    def enroll_employee(self):
        self.ensure_one()
        if self.emp_ids:
            for emp in self.emp_ids:
                if not emp.student_id:
                    vals = {'image_1920': emp.image_1920,
                            'name': emp.name,
                            'internal': True,
                            'emp_id': emp.id,
                            'student_id': emp.employee_id,
                            'department_id': emp.department_id.id,
                            'gender': list(emp.gender)[0],
                            'email': emp.work_email or '%s email' % emp.name,
                            'phone': emp.work_phone,
                            'mobile': emp.mobile_phone or 'mobile',
                            'birth_date': emp.birthday or '1990-01-01',
                            'nationality': emp.country_id.id or False}
                    if emp.user_id:
                        vals.update({'user_id': emp.user_id.id,
                                     'partner_id': emp.user_id.partner_id.id})
                    student = self.env['op.student'].sudo().create(vals)
                    course_list = self.env['op.course'].search(['|', ('department_ids', 'in', [emp.department_id.id]),
                                                                ('job_ids', 'in', [emp.job_id.id])])
                    for course in course_list:
                        student_course = self.env['op.student.course'].create({'student_id': student.id,
                                                                               'status': 'not'})
                        student_course.write({'course_id': course.id})
                if not self.env['op.student.course'].search(
                        [('batch_id', '=', self.id), ('student_id', '=', emp.student_id[0].id)]):
                    exist_pre_course = self.env['op.student.course'].search([('course_id', '=', self.course_id.id),
                                                                             ('student_id', '=', emp.student_id.id),
                                                                             ('status', '=', 'not')])
                    if not exist_pre_course:
                        self.env['op.student.course'].create({'student_id': emp.student_id.id,
                                                              'batch_id': self.id,
                                                              'course_id': self.course_id.id})
                    else:
                        exist_pre_course.write({'batch_id': self.id,
                                                'status': 'study'})
        else:
            raise ValidationError(_('There is no employee selected.'))

    @api.onchange('course_id', 'start_date', 'institute')
    def _onchange_course_id(self):
        if self.course_id:
            self.num_lessons = self.course_id.num_lessons
            self.min_attendance = self.course_id.min_attendance
            self.tutor_fee = self.course_id.tutor_fee
            # self.equipment_cost = self.course_id.equipment_cost
            self.code = self.course_id.code + '-' + str(self.start_date).split('-')[2] + \
                        str(self.start_date).split('-')[1] + str(self.start_date).split('-')[0][-2:] + (
                            '-' + self.institute.code if self.institute else '')

    @api.constrains('num_lessons', 'min_attendance')
    def constrain_lesson_absence(self):
        for record in self:
            if record.num_lessons < 1 or record.num_lessons > 999:
                raise ValidationError(_('Invalid Number of lessons'))
            if record.min_attendance < 0 or (record.min_attendance > record.num_lessons):
                raise ValidationError(_('Invalid Maximum absence'))

    @api.depends('tutor_fee', 'num_lessons')
    def _get_teacher_cost(self):
        for record in self:
            record.teacher_cost = record.tutor_fee * record.num_lessons

    @api.depends('faculty_bom')
    def _get_faculty_bom_cost(self):
        for record in self:
            record.faculty_bom_cost = sum([product.quantity * product.cost for product in record.faculty_bom])

    @api.constrains('start_date', 'end_date')
    def check_dates(self):
        for record in self:
            start_date = fields.Date.from_string(record.start_date)
            end_date = fields.Date.from_string(record.end_date)
            year_start_date = fields.Date.from_string(record.academic_year.start_date)
            year_end_date = fields.Date.from_string(record.academic_year.end_date)
            if end_date:
                if start_date > end_date:
                    raise ValidationError(
                        _("End Date cannot be set before Start Date."))
                elif record.academic_year and (start_date < year_start_date or end_date > year_end_date):
                    raise ValidationError(
                        _("Batch's time should be in academic year."))

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self.env.context.get('get_parent_batch', False):
            lst = []
            lst.append(self.env.context.get('course_id'))
            courses = self.env['op.course'].browse(lst)
            while courses.parent_id:
                lst.append(courses.parent_id.id)
                courses = courses.parent_id
            batches = self.env['op.batch'].search([('course_id', 'in', lst)])
            return batches.name_get()
        return super(OpBatch, self).name_search(
            name, args, operator=operator, limit=limit)
