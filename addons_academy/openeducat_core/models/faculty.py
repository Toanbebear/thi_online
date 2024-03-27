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


class OpFaculty(models.Model):
    _name = "op.faculty"
    _description = "OpenEduCat Faculty"
    _inherit = "mail.thread"
    _inherits = {"res.partner": "partner_id"}

    partner_id = fields.Many2one('res.partner', 'Partner',
                                 required=True, ondelete="cascade")
    middle_name = fields.Char('Middle Name', size=128)
    last_name = fields.Char('Last Name', size=128)
    birth_date = fields.Date('Birth Date', required=True)
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
        ('male', 'Male'),
        ('female', 'Female')
    ], 'Gender', required=True)
    nationality = fields.Many2one('res.country', 'Nationality')
    emergency_contact = fields.Many2one(
        'res.partner', 'Emergency Contact')
    visa_info = fields.Char('Visa Info', size=64)
    id_number = fields.Char('ID Card Number', size=64)
    login = fields.Char(
        'Login', related='partner_id.user_id.login', readonly=1)
    last_login = fields.Datetime('Latest Connection', readonly=1,
                                 related='partner_id.user_id.login_date')
    faculty_subject_ids = fields.Many2many('op.subject', string='Subject(s)',
                                           track_visibility='onchange')
    emp_id = fields.Many2one('hr.employee', 'HR Employee', domain=[('faculty_id', '=', False)])  # add domain for unique emp

    internal = fields.Boolean('Internal', default=True)  # employee as faculty for internal course
    emergency_contact2 = fields.Char('Emergency Contact')
    emergency_phone = fields.Char('Emergency Phone')
    location_id = fields.Many2one('stock.location')
    full_time = fields.Boolean('Full time')
    institute = fields.Many2one('op.institute', 'Institute')

    _sql_constraints = [  # sql constrain for emp id
        ('employee_unique', 'unique(emp_id)',
         'This employee is already linked to a faculty profile.'),
    ]

    @api.onchange('internal')
    def _onchange_internal(self):
        if not self.internal:
            self.emp_id = False

    @api.onchange('internal', 'emp_id')
    def _onchange_emp_id(self):
        if self.internal and self.emp_id:
            self.image_1920 = self.emp_id.image_1920 or False
            self.name = self.emp_id.name
            self.user_id = self.emp_id.user_id
            # self.last_name = str(self.emp_id.name).split(None, 1)[1] if ' ' in self.emp_id.name else '.'
            self.gender = self.emp_id.gender
            self.email = self.emp_id.work_email or False
            self.phone = self.emp_id.work_phone or False
            self.mobile = self.emp_id.mobile_phone or False
            self.birth_date = self.emp_id.birthday or False
            self.nationality = self.country_id or False
        else:
            self.name = False
            self.last_name = False
            self.gender = False
            self.email = False
            self.phone = False
            self.mobile = False
            self.birth_date = False
            self.nationality = False

    @api.constrains('birth_date')
    def _check_birthdate(self):
        for record in self:
            if record.birth_date > fields.Date.today():
                raise ValidationError(_(
                    "Birth Date can't be greater than current date!"))

    def create_employee(self):
        for record in self:
            vals = {
                'name': record.name,
                'country_id': record.nationality.id,
                'gender': record.gender,
                'address_home_id': record.partner_id.id
            }
            emp_id = self.env['hr.employee'].create(vals)
            record.write({'internal': True,
                          'emp_id': emp_id.id})
            record.partner_id.write({'supplier': True, 'employee': True})

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Faculties'),
            'template': '/openeducat_core/static/xls/op_faculty.xls'
        }]

    def open_stock_quant(self):
        return {
            'name': _('Faculty stock'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'stock.quant',
            'context': {'search_default_productgroup': 1},
            'domain': [('location_id', '=', self.location_id.id)],
        }

    @api.model
    def create(self, vals):
        if vals.get('full_time') and vals.get('user_id') and vals.get('institute'):
            partner = self.env['res.users'].browse(vals.get('user_id')).partner_id
            institute = self.env['op.institute'].browse(vals.get('institute'))
            vals.update({'partner_id': partner.id})
            self.env.ref('openeducat_core.group_op_faculty').users = [(4, vals.get('user_id'))]
            if not vals.get('location_id'):
                faculty_stock_location = self.env['stock.location'].create({'name': vals.get('name'),
                                                                            'posx': 0,
                                                                            'location_id': institute.location.id})
                vals.update({'location_id': faculty_stock_location.id})
                faculty = super(OpFaculty, self).create(vals)
                faculty_stock_location.update({'faculty_id': faculty.id})
        elif not vals.get('full_time') and vals.get('user_id') and vals.get('institute'):
            partner = self.env['res.users'].browse(vals.get('user_id')).partner_id
            vals.update({'partner_id': partner.id})
            self.env.ref('openeducat_core.group_op_faculty').users = [(4, vals.get('user_id'))]
            faculty = super(OpFaculty, self).create(vals)
        return faculty

    def write(self, vals):
        for record in self:
            res = super(OpFaculty, self).write(vals)
            if record.user_id and record.user_id.partner_id != record.partner_id:
                record.partner_id = record.user_id.partner_id
            location_vals = {'name': record.partner_id.name,
                             'posx': 0,
                             'faculty_id': record.id,
                             'location_id': record.institute.location.id}
            if not record.location_id and record.user_id and record.institute and record.full_time:
                faculty_stock_location = self.env['stock.location'].create(location_vals)
                record.location_id = faculty_stock_location
            elif record.location_id:
                record.location_id.write(location_vals)
            return res

    # @api.multi
    # def write(self, vals):
    #     for record in self:
    #         current_location = record.location_id
    #         if current_location and vals.get('name'):
    #             current_location.name = vals.get('name')
    #         if vals.get('user_id'):
    #             partner = self.env['res.users'].browse(vals.get('user_id')).partner_id
    #             vals.update({'partner_id': partner.id})
    #             self.env.ref('openeducat_core.group_op_faculty').users = [(4, vals.get('user_id'))]
    #             if (vals.get('full_time') or record.full_time) and (vals.get('institute') or record.institute) and not record.location_id:
    #                 faculty_stock_location = self.env['stock.location'].create({'name': vals.get('name') or partner.name,
    #                                                                             'posx': 0,
    #                                                                             'partner_id': partner.id,
    #                                                                             'location_id': record.institute.location.id})
    #                 vals.update({'location_id': faculty_stock_location.id})
    #         elif vals.get('full_time'):
    #             if record.user_id and not record.location_id:
    #                 faculty_stock_location = self.env['stock.location'].create(
    #                     {'name': vals.get('name') or record.user_id.partner_id.name,
    #                      'posx': 0,
    #                      'partner_id': record.user_id.partner_id.id,
    #                      'location_id': self.env.ref('openeducat_core.stock_warehouse_academy').lot_stock_id.id})
    #                 vals.update({'location_id': faculty_stock_location.id})
    #     return super(OpFaculty, self).write(vals)
