# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class EmployeeAdmission(models.TransientModel):
    _name = 'employee.admission'
    _description = 'Employee admission wizard'

    def _get_emps_domain(self):
        # course = self.env['op.batch'].browse(self.env.context.get('active_id')).course_id
        # learned_emps = self.env['op.student.course'].search([('course_id', '=', course.id), ('status', 'in', ('study', 'finish'))])
        # needed_emps = self.env['hr.employee'].search(['|', ('department_id', 'in', course.department_ids.ids),
        #                                               ('job_id', 'in', course.job_ids.ids)])
        # emp_list = [emp.id for emp in needed_emps if emp.id not in learned_emps.mapped('student_id.emp_id.id')]
        # if self.env.user.has_group('openeducat_core.group_op_back_office'):   # Todo: redo this later
        #     emp_list = self.env['hr.employee'].search([('id', 'not in', learned_emps.mapped('student_id.emp_id.id'))]).ids
        # domain = [('id', 'in', emp_list)]
        batch = self.env['op.batch'].browse(self.env.context.get('active_id'))
        domain = [('id', 'not in', batch.emp_ids.ids)]
        if not self.env.user.has_group('openeducat_core.group_op_back_office'):
            domain += [('id', 'child_of', self.env['hr.employee'].search([('user_id', '=', self.env.uid)]).id)]
        if batch.course_id.department_ids:
            domain += [('id', 'in',
                        self.env['hr.employee'].search(
                            [('department_id', 'in', batch.course_id.department_ids.ids)]).ids)]
        return domain

    manager_ids = fields.Many2many('hr.employee', 'admission_hr_manager_rel', 'ad_id', 'emp_id',
                                   string='Choose managers', domain=[('child_ids', '!=', False)])
    emp_ids = fields.Many2many('hr.employee', 'admission_hr_emp_rel', 'ad_id', 'emp_id', string='Choose employees',
                               domain=lambda self: self._get_emps_domain())

    def add_employee(self):
        record = self.env['op.batch'].browse(self.env.context.get('active_id'))
        for emp in self.emp_ids:
            if emp not in record.emp_ids:
                record.sudo().write({'emp_ids': [(4, emp.id)]})

    def remove_employee(self):
        record = self.env['op.batch'].browse(self.env.context.get('active_id'))
        for emp in self.emp_ids:
            if emp in record.emp_ids:
                if not self.env['op.student.course'].search(
                        [('batch_id', '=', record.id), ('student_id', '=', emp.student_id.id)]):
                    record.sudo().write({'emp_ids': [(3, emp.id)]})
                else:
                    raise ValidationError(_('Employee(s) already enrolled.'))

    def email_managers(self):
        if self.manager_ids:
            batch = self.env['op.batch'].browse(self.env.context.get('active_id'))
            course = batch.course_id
            mail_template = self.env.ref('openeducat_core.batch_email_managers')
            learned_emps = self.env['op.student.course'].search(
                [('course_id', '=', course.id), ('status', 'in', ('study', 'finish'))])
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            for manager in self.manager_ids:
                emp_list = self.env['hr.employee'].search(['|', ('department_id', 'in', course.department_ids.ids),
                                                           ('job_id', 'in', course.job_ids.ids),
                                                           ('id', 'child_of', manager.id),
                                                           ('id', 'not in',
                                                            [record.student_id.emp_id.id for record in learned_emps])])
                if emp_list:
                    values = {'model': 'op.batch',
                              'res_id': batch.id,
                              'subject': 'Khóa học nội bộ - %s' % (batch.name),
                              'parent_id': None,
                              'email_from': self.env.user.email or None,
                              'email_to': manager.work_email or None,
                              'auto_delete': False,
                              }
                    gender = ('Anh', 'Chị')[manager.gender == 'female']
                    body_html = '<p>Kính gửi %s %s,</p>' % (gender, manager.name) + \
                                '<p>Dưới đây là danh sách nhân viên chưa học khóa %s dưới quyền quản lý của %s:</p>' % (
                                course.name, gender) + \
                                '<table style="width:100%;" cellpadding="6" border="1">' + \
                                '<tr><td>ID</td><td>Tên</td><td>Vị trí</td></tr>'
                    for emp in emp_list:
                        body_html += '<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (
                        emp.employee_id, emp.name, emp.job_id.name)
                    body_html += '</table>' + \
                                 '<p>%s vui lòng vào link <a href="%s/web#view_type=form&amp;model=op.batch&amp;id=%s">này</a> để đăng ký học cho nhân viên của mình.</p>' % (
                                 gender, base_url, batch.id) + \
                                 '<p>Trân trọng,</p>' + \
                                 '<p>Học viện SCI.</p>'
                    values['body_html'] = body_html
                    mail = self.env['mail.mail'].create(values)
                    mail.send()
            return {'name': 'Emails',
                    'type': 'ir.actions.act_window',
                    'view_mode': 'tree,form',
                    'res_model': 'mail.mail',
                    'domain': [('res_id', '=', batch.id)]}
        else:
            raise ValidationError(_('Please choose recipients.'))
