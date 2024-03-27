from odoo import api, fields, models


class OpStudentCourse(models.Model):
    _inherit = "op.student.course"
    _description = "Student Course Details"

    @api.model
    def create_internal_student_cron(self):
        emp_not_student = self.env['hr.employee'].search([('student_id', '=', False)],
                                                         limit=150)
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
                    'phone': emp.work_phone or False,
                    'mobile': emp.mobile_phone or False,
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

    def cancel_course(self):
        self.status = 'cancel'
        order = self.env['sale.order'].search(
            [('partner_id', '=', self.student_id.partner_id.id),
             ('order_line.product_id', '=', self.course_id.product_id.id)], order='id desc', limit=1)
        if order:
            order.sudo().action_cancel()
        crm_line = self.env['crm.line'].search([('crm_id', '=', order.booking_id.id),
                                                ('product_id', '=', order.order_line.product_id.id)])
        if crm_line:
            crm_line.sudo().write({'cancel': True})
