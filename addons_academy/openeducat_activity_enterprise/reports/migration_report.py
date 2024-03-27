# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import fields, models, tools


class MigrationReport(models.Model):
    _name = "migration.report"
    _description = "Migration Report"
    _auto = False

    student_id = fields.Many2one('op.student', 'Student', readonly=True)
    date = fields.Date('Date', default=fields.Date.today(), readonly=True)
    faculty_id = fields.Many2one('op.faculty', 'Faculty', readonly=True)
    create_uid = fields.Many2one('res.users', 'Created By', readonly=True)
    create_date = fields.Datetime('Creation Date', readonly=True)
    write_uid = fields.Many2one('res.users', 'Updated By', readonly=True)
    write_date = fields.Datetime('Updated Date', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'migration_report')
        self._cr.execute("""
           CREATE VIEW migration_report as (
               SELECT
                   a.id as id,
                   a.student_id as student_id,
                   a.date as date,
                   a.faculty_id as faculty_id,
                   a.create_uid as create_uid,
                   a.create_date as create_date,
                   a.write_uid as write_uid,
                   a.write_date as write_date
               FROM op_activity a
               INNER JOIN op_activity_type t
               ON (a.type_id = t.id and t.name ilike 'Migration'))
        """)
