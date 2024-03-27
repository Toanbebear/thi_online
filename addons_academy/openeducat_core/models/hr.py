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

from odoo import models, api, fields, _


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    faculty_id = fields.One2many('op.faculty', 'emp_id', string='Faculty ID')  # link employee with faculty
    student_id = fields.One2many('op.student', 'emp_id', string='Student ID')  # link employee with student

    def sci_create(self):
        if not self.user_id:
            if self.work_email:
                user_vals = ({'name': self.name,
                              'image_1920': self.image_1920,
                              'login': self.work_email,
                              'email': self.work_email})
                op_group = self.env['res.groups']
                if self.student_id:
                    user_vals.update({'partner_id': self.student_id[0].partner_id.id})
                    op_group = self.env.ref('openeducat_core.group_op_student')
                if self.faculty_id:
                    user_vals.update({'partner_id': self.faculty_id[0].partner_id.id})
                    op_group = self.env.ref('openeducat_core.group_op_faculty')
                user = self.env['res.users'].create(user_vals)
                self.user_id = user.id
                if self.student_id or self.faculty_id:
                    op_group.users = [(4, user.id)]
            else:
                raise Warning(_('Please fill work email address before creating an account.'))
        else:
            return {
                'name': 'User',  # Lable
                'res_id': self.user_id.id,
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_id': self.env.ref('base.view_users_form').id,
                'res_model': 'res.users',  # your model
                'target': 'new',  # if you want popup
            }

    @api.onchange('user_id')
    def onchange_user(self):
        if self.user_id:
            self.user_id.partner_id.supplier = True
            self.work_email = self.user_id.email
            self.identification_id = False

    @api.onchange('address_id')
    def onchange_address_id(self):
        if self.address_id:
            self.work_phone = self.address_id.phone
            self.mobile_phone = self.address_id.mobile


# class HrJob(models.Model):
#     _inherit = 'hr.job'
#
#     course_ids = fields.Many2many('op.course', 'job_course_rel', 'job_id', 'course_id', string='Courses')
