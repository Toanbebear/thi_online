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


class MisbehaviourTypeReport(models.AbstractModel):
    _name = "report.openeducat_discipline.misbehaviour_type_report"
    _description = "Misbehaviour Type Report"

    def get_data(self, data):
        if data:
            return data

    def get_object(self, data):
        discipline_search = self.env['op.discipline'].search(
            [('misbehaviour_type', '=', data['misbehaviour_type']),
             ('date', '>=', data['from_date']),
             ('date', '<=', data['to_date'])],
            order='date asc')

        lst = []
        for record in discipline_search:
            dic = {
                'name': record.student_id.name,
                'middle_name': record.student_id.middle_name,
                'last_name': record.student_id.last_name,
                'misbehaviour_category_id': record
                .misbehaviour_category_id.name,
                'misbehaviour_sub_category_id': record
                .misbehaviour_sub_category_id.name,
                'date': record.date,
                'state': record.state
            }
            lst.append(dic)
        return [{'record': lst}]

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['op.discipline'].browse(docids)
        docargs = {
            'doc_model': 'op.discipline',
            'docs': docs,
            'time': time,
            'get_data': self.get_data(data),
            'get_object': self.get_object(data),
        }
        return docargs
