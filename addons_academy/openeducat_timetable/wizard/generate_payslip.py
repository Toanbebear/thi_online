# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import datetime


class GeneratePayslip(models.TransientModel):
    _name = 'generate.payslip'
    _description = 'Generate payslip'

    def _get_faculty_id(self):
        return self.env['hr.employee'].browse(self.env.context.get('active_ids')).faculty_id

    def _get_default_unpaid_sessions(self):
        faculty = self.env['hr.employee'].browse(self.env.context.get('active_ids')).faculty_id
        return self.env['op.session'].search([('faculty_id', '=', faculty.id),
                                              ('paid', '=', False),
                                              ('state', 'in', ['done', 'confirm']),
                                              ('end_datetime', '<', fields.Datetime.now())])

    faculty_id = fields.Many2one('op.faculty', string='Faculty ID', default=_get_faculty_id, readonly=True)
    unpaid_sessions = fields.Many2many('op.session', string='Unpaid sessions',
                                       default=_get_default_unpaid_sessions)

    def pay_for_it(self):
        self.ensure_one()
        if self.unpaid_sessions:
            employee = self.env['hr.employee'].browse(self.env.context.get('active_ids'))
            teaching_contract = self.env['hr.contract'].search([('employee_id', '=', employee.id),
                                                                ('name', '=', 'Teaching contract')])
            if not teaching_contract:
                teaching_contract = self.env['hr.contract'].create({'name': 'Teaching contract',
                                                                    'employee_id': employee.id,
                                                                    'type_id': self.env.ref('hr_contract.hr_contract_type_emp').id,
                                                                    'date_start': fields.Date.today(),
                                                                    'wage': 0.0,
                                                                    'company_id': 1,
                                                                    'struct_id': self.env.ref('openeducat_timetable.teaching_salary_structure').id,
                                                                    # 'resource_calendar_id': self.env['res.company']._company_default_get().resource_calendar_id.id})
                                                                    'resource_calendar_id': 1,
                                                                    'schedule_pay': 'monthly'})
            sessions_start = []
            sessions_end = []
            vals = []
            batches = {}
            for record in self.unpaid_sessions:
                sessions_start.append(record.start_datetime)
                sessions_end.append(record.end_datetime)
                record.paid = True
                if record.batch_id.name not in batches.keys():
                    batches[record.batch_id.name] = [record.tutor_fee * record.lesson_count, record.lesson_count]
                else:
                    batches[record.batch_id.name][0] += record.tutor_fee * record.lesson_count
                    batches[record.batch_id.name][1] += record.lesson_count
            date_from = min(sessions_start).date()
            date_to = max(sessions_end).date()
            for key, value in batches.items():
                vals.append((0, 0, {'name': '%s - %s lesson(s)' % (key, value[1]),
                                    'sequence': 10,
                                    'code': 'input%s' % (list(batches.keys()).index(key) + 1),
                                    'amount': value[0],
                                    'contract_id': teaching_contract.id}))
            vals.append((0, 0, {'name': 'Total teaching salary',
                                'sequence': 100,
                                'code': 'TOTALTEACHING',
                                'amount': sum(value[0] for value in batches.values()),
                                'contract_id': teaching_contract.id}))
            payslip = self.env['hr.payslip'].create({'employee_id': employee.id,
                                                     'date_from': date_from,
                                                     'date_to': date_to,
                                                     'name': 'Teaching salary slip for %s from %s to %s' % (employee.name, date_from, date_to),
                                                     'contract_id': teaching_contract.id,
                                                     'struct_id': self.env.ref('openeducat_timetable.teaching_salary_structure').id,
                                                     'input_line_ids': vals})
            payslip.action_payslip_done()
            return {
                'name': 'Payslip',
                'res_id': payslip.id,
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'hr.payslip'
            }
        else:
            raise ValidationError(_('Please choose sessions'))
