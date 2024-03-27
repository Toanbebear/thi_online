# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, api


class OpBatch(models.Model):
    _inherit = 'op.batch'

    def open_generate_timetable(self):
        self.ensure_one()
        action = self.env.ref(
            'openeducat_timetable.act_open_generate_time_table_view').read()[0]
        action.update({'context': "{'default_batch_id': " +
                       str(self.id) + ", 'default_course_id': " +
                       str(self.course_id.id) + "}"})
        return action

    def open_generate_timetable_reports(self):
        self.ensure_one()
        action = self.env.ref(
            'openeducat_timetable.act_open_time_table_report_view').read()[0]
        action.update({'context':
                       "{'default_state': 'student','default_batch_id': " +
                       str(self.id) + ", 'default_course_id': " +
                       str(self.course_id.id) + "}"})
        return action
