# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class EmployeeAdmission(models.TransientModel):
    _name = 'op.admission.enroll'
    _description = 'Enroll multiple admission'

    def _get_batch_domain(self):
        records = self.env['op.admission'].browse(self.env.context.get('active_ids'))
        if len(records) > 0:
            return [('course_id', '=', records[0].course_id.id)]

    batch_id = fields.Many2one('op.batch', string='Choose batch', domain=lambda self: self._get_batch_domain())

    def enroll_students(self):
        self.ensure_one()
        records = self.env['op.admission'].browse(self.env.context.get('active_ids'))
        for i in range(1, len(records)):
            if records[i].course_id.id != records[0].course_id.id:
                raise ValidationError(_('Selected application are from different courses.'))
        if self.batch_id:
            for record in records:
                if record.student_id and record.state != 'done':
                    record.batch_id = self.batch_id
                    record.enroll_student()
        elif not self.batch_id:
            raise ValidationError(_('Please choose a batch.'))

