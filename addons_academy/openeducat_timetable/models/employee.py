# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Employee(models.Model):
    _inherit = 'hr.employee'

    unpaid_sessions_count = fields.Integer('Unpaid sessions', compute='_get_unpaid_sessions_count')

    def _get_unpaid_sessions_count(self):
        for record in self:
            if not record.faculty_id.full_time:
                record.unpaid_sessions_count = self.env['op.session'].search_count([('faculty_id', '=', record.faculty_id.id),
                                                                                  ('paid', '=', False),
                                                                                  ('state', 'in', ['done', 'confirm']),
                                                                                  ('end_datetime', '<', fields.Datetime.now())])
            else:
                record.unpaid_sessions_count = 0
