# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

import calendar
from datetime import datetime, date

from odoo import fields
from odoo import http
from odoo.http import request


class OpenEduCatController(http.Controller):

    @http.route('/openeducat_core_enterprise/get_main_dash_data',
                type='json', auth='user')
    def compute_main_dashboard_data(self):
        ser = 0
        es = 0
        mfr = '0:0'
        spr = 0

        adm_ref = request.env['op.admission']
        student_ref = request.env['op.student']
        admission = request.env['ir.model'].search(
            [('model', '=', 'op.admission')])
        if admission:
            total_admsn = adm_ref.search_count([
                ('state', '=', 'done')])
            if total_admsn:
                ser = round(total_admsn * 100 / adm_ref.search_count([]), 2)
                es = adm_ref.search_count([('state', '=', 'done')])
        m_student = student_ref.search_count([('gender', '=', 'm')])
        f_student = student_ref.search_count([('gender', '=', 'f')])
        mfr = str(m_student) + ':' + str(f_student)
        total_faculty = request.env['op.faculty'].search_count([])
        spr = str(m_student + f_student) + ':' + str(total_faculty)
        return {'student_enroll_rate': ser, 'erolled_students': es,
                'mf_ratio': mfr, 'sp_ratio': spr}

    @http.route('/openeducat_core_enterprise/fetch_batch',
                type='json', auth='user')
    def fetch_openeducat_batches(self):
        return {'batch_ids': request.env['op.batch'].search_read(
            [], ['id', 'name'], order='name')}

    @http.route('/openeducat_core_enterprise/compute_openeducat_batch_graph',
                type='json', auth='user')
    def compute_openeducat_batch_graph(self, batch_id):
        data = []
        last_day = datetime.today().replace(
            day=calendar.monthrange(date.today().year,
                                    date.today().month)[1])
        for d in range(1, last_day.day + 1):
            attendance_sheet = request.env['ir.model'].search(
                [('model', '=', 'op.attendance.sheet')])
            if attendance_sheet and batch_id:
                value = request.env['op.attendance.sheet'].search([
                    ('batch_id', '=', int(batch_id)),
                    ('attendance_date', '=',
                     fields.date.today().replace(day=d))])
                data.append({'label': str(d),
                             'value': value and value[0].total_present or 0})
        return data

    @http.route('/openeducat_core_enterprise/get_batch_dashboard_data',
                type='json', auth='user')
    def compute_batch_dashboard_data(self, batch_id):
        tar = 0
        ts = 0
        tbl = 0
        ta = 0
        ir_model_ref = request.env['ir.model']
        op_attn_sheet_ref = request.env['op.attendance.sheet']
        attendance_sheet = ir_model_ref.search([
            ('model', '=', 'op.attendance.sheet')])
        if attendance_sheet and batch_id:
            tarp = op_attn_sheet_ref.search(
                [('batch_id', '=', int(batch_id)),
                 ('attendance_date', '=', fields.date.today())])
            tara = op_attn_sheet_ref.search(
                [('batch_id', '=', int(batch_id)),
                 ('attendance_date', '=', fields.date.today())])
            tar = tarp and str(tarp[0].total_present) or '0'
            tar += ':'
            tar += tara and str(tara[0].total_absent) or '0'
        if batch_id:
            ts = request.env['op.student'].search_count([
                ('course_detail_ids.batch_id', '=', int(batch_id))])
        session = ir_model_ref.search([('model', '=', 'op.session')])
        if session and batch_id:
            tbl = request.env['op.session'].search_count(
                [('batch_id', '=', int(batch_id)),
                 ('start_datetime', '>=',
                  datetime.today().strftime('%Y-%m-%d 00:00:00')),
                 ('start_datetime', '<=',
                  datetime.today().strftime('%Y-%m-%d 23:59:59'))])
        assignment = ir_model_ref.search([('model', '=', 'op.assignment')])
        if assignment and batch_id:
            ta = request.env['op.assignment'].search_count(
                [('batch_id', '=', int(batch_id))])
        return {'tar': tar, 'tbl': tbl, 'ts': ts, 'ta': ta}
