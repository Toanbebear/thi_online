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


class OpCourse(models.Model):
    _name = "op.course"
    _inherit = "mail.thread"
    _description = "OpenEduCat Course"

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True, copy=False)
    parent_id = fields.Many2one('op.course', 'Parent Course')
    section = fields.Char('Section', size=32)
    evaluation_type = fields.Selection(
        [('normal', 'Normal'), ('GPA', 'GPA'),
         ('CWA', 'CWA'), ('CCE', 'CCE')],
        'Evaluation Type', default="normal")
    subject_ids = fields.Many2many('op.subject', string='Subject(s)')
    max_unit_load = fields.Float("Maximum Unit Load")
    min_unit_load = fields.Float("Minimum Unit Load")

    # added for sci academy
    category_id = fields.Many2one('op.category', string='Category code')
    bom = fields.Many2one('product.bundle', 'Student BOM', domain="[('bom_type', '=', 'gift_bom')]")
    course_bom = fields.Many2one('product.bundle', 'Course BOM', domain="[('bom_type', '=', 'course_bom')]")
    max_absence = fields.Integer('Maximum absences')
    min_attendance = fields.Integer('Minimum attendance')
    internal = fields.Boolean('Internal course')
    tutor_fee = fields.Float('Tutor fee per lesson')
    faculty_bom = fields.One2many('products.line', 'course_id', string='Faculty BOM')
    # equipment_cost = fields.Float('Equipment cost')
    currency_id = fields.Many2one(
        'res.currency', 'Currency',
        default=lambda self: self.env.user.company_id.currency_id.id,
        required=True)
    products_domain = fields.Many2many('product.product', string='Duma', compute='_get_products_domain')
    category_code = fields.Char('Category', related='category_id.code')

    # added for internal courses
    department_ids = fields.Many2many('hr.department', 'dept_course_rel', 'course_id', 'dept_id', string='Departments')
    job_ids = fields.Many2many('hr.job', 'job_course_rel', 'course_id', 'job_id', string='Job positions')

    _sql_constraints = [
        ('unique_course_code',
         'unique(code)', 'Code should be unique per course!')]

    @api.onchange('min_attendance', 'num_lessons')
    def check_min_attendance(self):
        for rec in self:
            if rec.min_attendance > rec.num_lessons:
                raise ValidationError(
                    _('The minimum number of periods must not be greater than the total number of periods '))

    @api.onchange('course_bom')
    def get_faculty_bom(self):
        if self.course_bom.products:
            for product in self.course_bom.products:
                self.faculty_bom = [
                    (0, 0, {'product': product.product.id, 'quantity': product.quantity, 'uom_id': product.uom_id.id})]

    @api.onchange('category_id')
    def _onchange_category(self):
        for record in self:
            if record.category_id:
                record.code = record.category_id.name + '/' if record.category_id else False

    @api.depends('faculty_bom')
    def _get_products_domain(self):
        for record in self:
            if len(record.faculty_bom) > 0:
                record.products_domain = [
                    (6, 0, [product.product.id for product in record.faculty_bom if product.product])]
            else:
                record.products_domain = False

    @api.constrains('num_lessons', 'min_attendance')
    def constrain_lesson_absence(self):
        # if not self.internal:
        for record in self:
            if record.num_lessons < 1 or record.num_lessons > 999:
                raise ValidationError(_('Invalid Number of lessons'))
            if record.min_attendance < 0 or record.min_attendance > record.num_lessons:
                raise ValidationError(_('Invalid Maximum absence'))

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Courses'),
            'template': '/openeducat_core/static/xls/op_course.xls'
        }]

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('code', operator, name)]
        course_ids = self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
        return self.browse(course_ids).name_get()

    def name_get(self):
        if self._context.get('code_only'):
            return [(rec.id, rec.code) for rec in self]
        elif self._context.get('code_and_name'):
            return [(rec.id, rec.code + ' - ' + rec.name) for rec in self]
        else:
            return [(rec.id, rec.name) for rec in self]
