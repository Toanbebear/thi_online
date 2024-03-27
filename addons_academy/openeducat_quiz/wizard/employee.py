from odoo import models, fields, api


class Employee(models.TransientModel):
    _name = "employee.wizard"
    _description = "Thêm nhân viên vào bài thi"

    employee_id = fields.Many2many('hr.employee', string='Employee', domain="[('company_id', '=', company_id)]")
    company_id = fields.Many2many('res.company', string='Company')
    quiz_id = fields.Many2one('op.quiz', string='Bài kiểm tra')

    def action_confirm(self):
        for rec in self:
            quiz = self.env['op.quiz'].browse(rec.quiz_id.id)
            quiz.employee_id = [(4, employee_id.id) for employee_id in rec.employee_id]
