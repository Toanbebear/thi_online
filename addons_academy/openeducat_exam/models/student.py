from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SCIstudentcourse(models.Model):
    _inherit = 'op.student.course'

    # batch_status = fields.Selection([('ongoing', 'Ongoing'), ('closed', 'Closed')], string='Batch status', compute='_get_batch_status')
    percentage = fields.Char('Average', compute='_get_percentage', store=True)
    grade = fields.Char('Grade', compute='_get_grade')
    result_lines = fields.One2many('op.result.line', 'student_course_id', 'Results')

    @api.depends('result_lines.marks')
    def _get_percentage(self):
        for record in self:
            total_result_lines = record.result_lines
            if record.status != 'reserve':
                reserve_student_course_ids = self.env['op.student.course'].search([('course_id', '=', record.course_id.id),
                                                                                   ('status', '=', 'reserve')])
                for student_course in reserve_student_course_ids:
                    total_result_lines += student_course.result_lines
            if total_result_lines:
                total_marks = sum([int(line.marks) for line in total_result_lines])
                total_exam_marks = sum([int(line.exam_id.total_marks) for line in total_result_lines])
                record.percentage = str(round(total_marks/total_exam_marks*10, 2))
            else:
                record.percentage = False

    @api.depends('percentage')
    def _get_grade(self):
        for record in self:
            record.grade = False
            if record.result_lines:
                grades = self.env['op.grade.configuration'].search([])
                record.grade = False
                for grade in grades:
                    if grade.min_per <= float(record.percentage) < grade.max_per:
                        record.grade = grade.result

    # @api.one
    # @api.depends('marksheet')
    # def _get_status(self):
    #     self.status = self.marksheet.status or False


    # @api.one
    # @api.depends('batch_id')
    # def _get_batch_status(self):
    #     self.batch_status = ('ongoing', 'closed')[self.batch_id.end_date < fields.Date.today()]
