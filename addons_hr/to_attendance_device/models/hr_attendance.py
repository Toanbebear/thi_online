from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    def _get_employee_id(self):
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return employee_rec.id

    checkin_device_id = fields.Many2one('attendance.device', string='Checkin Device', readonly=True, index=True,
                                        help='The device with which user took check in action')
    checkout_device_id = fields.Many2one('attendance.device', string='Checkout Device', readonly=True, index=True,
                                         help='The device with which user took check out action')
    activity_id = fields.Many2one('attendance.activity', string='Attendance Activity',
                                  help='This field is to group attendance into multiple Activity (e.g. Overtime, Normal Working, etc)')
    company_id = fields.Many2one('res.company', 'Company', related="employee_id.company_id", readonly=True, store= True)

    department_id = fields.Many2one('hr.department', string="Department", related="employee_id.department_id",
                                    readonly=True, store= True)
    reason = fields.Text(string="Giải trình", help='Giải trình những trường hợp quên chấm, lý do dữ liệu không khớp...')
    workday = fields.Selection([('1', 'Cả ngày'), ('0.5', 'Nửa ngày'), ('1.5', 'Cả ngày + Trực')],
                             string='Ngày công', default='1')
    name = fields.Char(default='X', string='Loại công')
    state = fields.Selection([
        ('draft', 'Chưa xác nhận'),
        ('confirm', 'Xác nhận'),
        ('refuse', 'Từ chối'),
        ('validate', 'Đã phê duyệt')
    ], string='Trạng thái', readonly=True, tracking=True, copy=False, default='draft')
    approver_id = fields.Many2one('hr.employee', string='Người phê duyệt', readonly=True, copy=False, default=_get_employee_id)
    resign_confirm_date = fields.Datetime(string="Ngày phê duyệt", default=datetime.now())

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        if not self.env.context.get('synch_ignore_constraints', False):
            super(HrAttendance, self)._check_validity()

    def action_attendance_approve(self):
        if self.workday == '1':
            name = 'X'
        elif self.workday == '1.5':
            name = 'XT'
        elif self.workday == '0.5':
            name = 'X/2'
        else:
            raise ValidationError("Ngày bắt đầu không hợp lệ!!!")

        check_in = self.check_in if self.check_in else self.check_out
        check_out = self.check_out if self.check_out else self.check_in
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        self.write({'state': 'validate', 'approver_id': current_employee.id, 'resign_confirm_date': datetime.now(),
                    'workday': self.workday, 'name': name, 'check_in': check_in, 'check_out': check_out})
        return True

    def action_attendance_refuse(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        self.write({'state': 'refuse', 'approver_id': current_employee.id, 'resign_confirm_date': datetime.now()})
        return True

    def action_attendance_cancel(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        self.write({'state': 'draft', 'approver_id': current_employee.id, 'resign_confirm_date': datetime.now()})

        return True

    def name_get(self):
        res = super(HrAttendance, self).name_get()
        if self.env.context.get('show_name'):
            return [(attendance.id, attendance.name) for attendance in self]
        return res

    def set_confirm_NB(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        self.env['hr.leave.allocation'].sudo().create({'name': 'Nghỉ bù ngày công: ' + str(self.check_in.date()),
                                                    'state': 'validate',
                                                    'first_approver_id': current_employee.id,
                                                    'holiday_type': 'employee',
                                                    'number_of_days': self.workday,
                                                    'holiday_status_id': self.env.ref('hr_holidays.holiday_status_comp').id,
                                                    'employee_id': self.employee_id.id})
        self.reason = 'Chuyển nghỉ bù!!!'
        self.state = 'confirm'
        self.approver_id = current_employee.id
        self.resign_confirm_date = datetime.now()
        return {'type': 'ir.actions.act_window',
                'name': 'Bảng công',
                'res_model': 'hr.attendance',
                'view_mode': 'gantt',
                'context': {'search_default_group_department': 1, 'search_default_employee': 1, 'show_name': 1, 'default_state': 'validate'},
				'domain': [('state', '=', 'validate')],
                'views': [[self.env.ref('to_attendance_device.hr_work_entry_gantt').id, 'gantt']],
                }

    def open_hr_leave_wizard(self):
        return {
            'name': "Tạo mới nghỉ phép nhân viên",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.leave',
            'context': {'default_employee_id': self.employee_id.id, 'open_hr_leave': 1},
            'target': 'new'
        }