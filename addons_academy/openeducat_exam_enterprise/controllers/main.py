# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import http
from odoo.http import request


class Exam(http.Controller):

    @http.route("/get_exam_counts", type="json", auth="user")
    def get_exams(self):
        Exam = request.env['op.exam']
        all_exams = Exam.search_count([])
        done_exams = Exam.search_count([('state', '=', 'done')])
        pending_exams = Exam.search_count([('state', '=', 'draft')])
        all_exams_sessions = request.env['op.exam.session'].search_count([])

        return {
            'all_exams': all_exams,
            'pending_exams': pending_exams,
            'done_exams': done_exams,
            'all_exams_sessions': all_exams_sessions
        }

    def get_details(self, domain, subject=False):
        data = []
        for exam in request.env['op.exam'].search(domain):
            pass_count = 0
            res = {}
            for attendant in exam.attendees_line.filtered(
                    lambda att: att.marks >= exam.min_marks):
                pass_count += 1
            length = len(exam.attendees_line) if exam.attendees_line else 1
            ratio = (pass_count / length) * 100
            if subject:
                res = {
                    'id': exam.id,
                    'name': exam.subject_id.name,
                    'exam': exam.name,
                    'code': exam.exam_code,
                    'start_time': exam.start_time or False,
                    'end_time': exam.end_time or False,
                    'min_marks': exam.min_marks or 0.0,
                    'total_marks': exam.total_marks or 0.0,
                }
            else:
                res = {
                    'name': exam.name,
                    'ratio': ratio
                }
            data.append(res)
        return data

    @http.route("/get_exam_chart_details", type="json", auth="user")
    def get_exam_chart_details(self):
        return self.get_details([('attendees_line', '!=', False)])

    @http.route("/get_subject_details", type="json", auth="user")
    def get_subject_details(self, session_id):
        return self.get_details([
            ('session_id', '=', int(session_id))], subject=True)

    @http.route("/get_exam_sessions", type="json", auth="user")
    def get_exam_sessions(self):
        return {
            'session_ids': request.env['op.exam.session'].search_read(
                [], ['id', 'name'])
        }
