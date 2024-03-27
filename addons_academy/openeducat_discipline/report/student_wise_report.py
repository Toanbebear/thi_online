# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

import time

from odoo import models, api


class StudentWiseReport(models.AbstractModel):
    _name = "report.openeducat_discipline.student_wise_report"
    _description = "Student Wise Report"

    def get_data(self, data):
        if data:
            return data

    def get_object(self, data):
        discipline_search = self.env['op.discipline'].search(
            [('student_id', '=', data['student_id'][0]),
             ('date', '>=', data['from_date']),
             ('date', '<=', data['to_date'])],
            order='date asc')

        lst = []
        for record in discipline_search:
            dic = {
                'date': record.date,
                'misbehaviour_type': record.misbehaviour_type,
                'misbehaviour_category_id': record
                .misbehaviour_category_id.name,
                'misbehaviour_sub_category_id': record
                .misbehaviour_sub_category_id.name,
                'misbehaviour_action': record.misbehaviour_action,
                'state': record.state
            }
            lst.append(dic)
        return [{'record': lst}]

    @api.model
    def get_report_values(self, docids, data=None):
        docs = self.env['op.discipline'].browse(docids)
        docargs = {
            'doc_model': 'op.discipline',
            'docs': docs,
            'time': time,
            'get_object': self.get_object(data),
            'get_data': self.get_data(data),
        }
        return docargs
