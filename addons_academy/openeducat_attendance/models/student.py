from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SCIstudentcourse(models.Model):
    _inherit = 'op.student.course'

    # absence = fields.Char('Absence', compute='_get_absence', size=4)
    attendance = fields.Char('Attendance', compute='_get_attendance', size=40, store=True)
    progress = fields.Char('Progress', compute='_get_attendance', store=True)
    attendance_lines = fields.One2many('op.attendance.line', inverse_name='student_detail')

    @api.depends('student_id', 'batch_id', 'attendance_lines')
    def _get_attendance(self):
        for record in self:
            if record.batch_id:
                reserve_text = ''
                attendance_lines = record.attendance_lines
                if record.status != 'reserve':
                    reserve_student_course_ids = self.env['op.student.course'].search(
                        [('student_id', '=', record.student_id.id), ('course_id', '=', record.course_id.id),
                         ('status', '=', 'reserve')])
                    for student_course in reserve_student_course_ids:
                        attendance_lines += self.env['op.attendance.line'].search(
                            [('student_id', '=', record.student_id.id), ('batch_id', '=', student_course.batch_id.id),
                             '|', ('present', '=', True), ('catch_up', '!=', False)])
                    reserve_attendance = sum(
                        line.sudo().attendance_id.session_id.lesson_count for line in attendance_lines if
                        line.batch_id != record.batch_id)
                    if reserve_attendance > 0:
                        reserve_text = '(include ' + str(reserve_attendance) + ' reserved)'
                total_attendance = sum(line.sudo().attendance_id.session_id.lesson_count for line in attendance_lines)
                if total_attendance == record.batch_id.num_lessons:
                    record.write({'status': 'finish'})
                    order = self.env['sale.order'].search(
                        [('partner_id', '=', record.student_id.partner_id.id),
                         ('order_line.product_id', '=', record.course_id.product_id.id),
                         ('state', '=', 'draft')])
                    if order:
                        # Xác nhận SO
                        order.action_confirm()
                        # Tạo hóa đơn dạng nháp
                        if order.invoice_status == 'to invoice':
                            wizard = self.env['sale.advance.payment.inv'].sudo().with_context(
                                {'active_ids': [order.id], 'partner_id': order.partner_id.id,
                                 'company_id': order.company_id.id}).create({})
                            wizard.create_invoices()
                elif total_attendance:
                    record.write({'status': 'study'})
                record.attendance = str(total_attendance) + '/' + str(record.batch_id.num_lessons) + reserve_text
                record.progress = str(round(total_attendance / record.batch_id.num_lessons * 100)) + ' %'
            else:
                record.attendance = False
                record.progress = False
