# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from datetime import datetime
from datetime import date

from odoo.http import request

from odoo import http, fields
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request


class OpeneducatQuizRender(http.Controller):

    def get_quiz_result_data(self, values):
        wrong_answers = []
        not_attempt_answer = []
        right_answers = []
        result = request.env['op.quiz.result'].browse(int(values['ExamID']))
        result_line_answer = request.env['op.quiz.result.line.answers']
        for line in result.line_ids:
            if ('question' + str(line.id)) in values:
                given_answer_id = int(values['question' + str(line.id)])
                answer = result_line_answer.browse(
                    given_answer_id)
                line.given_answer = answer.name
                if answer.grade_id and answer.grade_id.value == 100.0:
                    right_answers.append({
                        'question': line.name, 'answer': answer.name
                    })
                    line.mark = line.question_mark or 0.0
                else:
                    wrong_answers.append({
                        'question': line.name,
                        'given_answer': answer.name,
                        'answer': line.answer or '',
                    })
                    line.mark = answer.grade_id.value * \
                                line.question_mark / 100
            elif ('blank' + str(line.id)) in values:
                line.given_answer = values['blank' + str(line.id)]
                if line.case_sensitive:
                    if line.answer == line.given_answer:
                        received_mark = (
                                                line.question_mark * (
                                                line.grade_true_id.value or 0.0)) / 100
                        line.mark = received_mark
                    else:
                        received_mark = (
                                                line.question_mark * (
                                                line.grade_false_id.value or 0.0)) / 100
                        line.mark = received_mark
                else:
                    if line.answer.lower() == line.given_answer.lower():
                        received_mark = (
                                                line.question_mark * (
                                                line.grade_true_id.value or 0.0)) / 100
                        line.mark = received_mark
                    else:
                        received_mark = (
                                                line.question_mark * (
                                                line.grade_false_id.value or 0.0)) / 100
                        line.mark = received_mark
            elif ('descriptive' + str(line.id)) in values:
                line.given_answer = values['descriptive' + str(line.id)]
            else:
                not_attempt_answer.append({
                    'question': line.name, 'answer': line.answer or ''})
        score = result.score or 0.0
        quiz = result.quiz_id
        message = ''
        is_message = 0
        for msg in quiz.quiz_message_ids:
            result_to = msg.result_to
            result_from = msg.result_from
            if (score <= result_to) and (score >= result_from):
                message = msg.message
                is_message = 1
        display_wrong_ans = 0
        if quiz.wrong_ans and wrong_answers:
            display_wrong_ans = 1
        display_true_ans = 0
        if quiz.right_ans and right_answers:
            display_true_ans = 1
        not_attempt_ans = 0
        if quiz.not_attempt_ans and not_attempt_answer:
            not_attempt_ans = 1
        result.finish_date = datetime.today()
        return {
            'wrong_answer': wrong_answers,
            'not_attempt_answer': not_attempt_answer,
            'right_answers': right_answers,
            'total_question': result.total_question,
            'total_correct': result.total_correct,
            'total_incorrect': result.total_incorrect,
            'total_marks': result.total_marks,
            'received_marks': result.received_marks,
            'percentage': score,
            'display_wrong_ans': display_wrong_ans,
            'display_true_ans': display_true_ans,
            'not_attempt_ans': not_attempt_ans,
            'message': message,
            'is_message': is_message,
            'state': 'done'
        }

    @http.route('/users/result-overview', type="http", auth="user",
                website=True)
    def get_result_overview(self, **post):
        quiz_result = request.env['op.quiz.result']
        user = request.env['res.users'].browse(request.env.uid)
        post['user'] = user
        attempt = quiz_result.sudo().search(
            [('user_id', '=', user.id)])
        total_exam = 0
        progress = 0
        if attempt:
            total_result = sum([val.score for val in attempt])
            total_exam = len(attempt.ids)
            progress = int(total_result) / int(len(attempt))
        post['total_exam'] = total_exam
        post['progress'] = progress
        post['result_btn'] = 0
        data = []
        attempt = attempt.filtered(lambda r: r.state == 'done')
        for res in attempt:
            data.append({
                'name': res.quiz_id.name,
                'ttl_que': res.total_question or 0,
                'ttl_crct': res.total_correct or 0,
                'ttl_incrct': res.total_incorrect or 0,
                'ttl_marks': res.total_marks or 0,
                'rec_marks': res.received_marks or 0,
                'score': str(res.score or 0) + ' %',
                'finish_date': res.finish_date,
            })
        post['result_data'] = data
        return http.request.render('openeducat_quiz.my_result', post)

    @http.route('/online-exams', type="http", auth="user", website=True)
    def get_exam_details(self, **post):
        quiz_result = request.env['op.quiz.result']
        user = request.env['res.users'].browse(request.env.uid)
        post['user'] = user
        attempt = quiz_result.sudo().search(
            [('user_id', '=', user.id)])
        progress = 0
        quiz_attempt = {}
        total_exam = 0
        now = fields.datetime.now()
        if attempt:
            total_result = sum([val.score for val in attempt])
            total_exam = len(attempt.ids)
            progress = int(total_result) / int(len(attempt))
        post['total_exam'] = total_exam
        post['progress'] = round(progress, 2)
        post['result_btn'] = 1

        exam_auth_required_employee = request.env['op.quiz'].search([
            ('state', '=', 'open'),
            ('start_date', '<=', now),
            ('end_date', '>=', now),
            ('employee_id.user_id', '=', user.id),
            ('auth_required', '=', True),
            ('quiz_employee', '=', True),
        ])
        exam_auth_required_student = request.env['op.quiz'].search([
            ('state', '=', 'open'),
            ('start_date', '<=', now),
            ('end_date', '>=', now),
            ('student_id.user_ids', 'in', user.id),
            ('auth_required', '=', True),
            ('academy_exam', '=', True),
        ])
        exam_not_auth_required = request.env['op.quiz'].search([
            ('state', '=', 'open'),
            ('start_date', '<=', now),
            ('end_date', '>=', now),
            ('auth_required', '=', False)
        ])
        exams = exam_auth_required_employee.union(exam_auth_required_student, exam_not_auth_required)

        for exam in exams:
            ttl_atmp = quiz_result.sudo().search(
                [('quiz_id', '=', exam.id)])
            ttl_res = 0
            allow = exam.quiz_allow()
            if ttl_atmp:
                ttl_res = sum([atmp_res.score for atmp_res in ttl_atmp])
                ttl_res = ttl_res / len(ttl_atmp.ids)
            quiz_attempt.update({exam.id: {
                'ttl_atmp': len(ttl_atmp.ids),
                'avg_res': int(ttl_res),
                'allow': allow
            }})
        post['quiz_attempt'] = quiz_attempt
        post['exams'] = exams
        return http.request.render('openeducat_quiz.online_exam_page', post)

    #bấm nút bắt đầu thi đầu tiên
    @http.route('/exam/start/<model("op.quiz"):quiz>',
                type="http", auth="public", website=True)
    def start_exam(self, quiz):
        exam_link = quiz.redirect_exam()
        return request.redirect(exam_link)

    @http.route('/quiz/submit/<model("op.quiz.result"):result>',
                type="http", auth="public", website=True)
    def get_result_submit(self, result):
        if not result.quiz_id.show_result:
            return http.request.render(
                'openeducat_quiz.quiz_completed', {})
        return request.redirect('/exam/score/%s' % (result.id))

    # bấm nút bắt đầu thi đầu tiên
    @http.route('/quiz/rules/<model("op.quiz.result"):result>', type="http",
                auth="public", website=True)
    def get_quiz_start(self, result, **post):
        print('quiz')
        exam = result.quiz_id
        if exam.auth_required:
            print('xxxxxxx')
            if request.env.user._is_public():
                return request.render("openeducat_quiz.auth_required", {'quiz': exam, 'result': result})
            else:
                if result.user_id.id != request.env.uid:
                    for rec in result.line_ids:
                        if rec.given_answer:
                            return http.request.render('openeducat_quiz.quiz_warning_page', post)
                        else:
                            if exam.quiz_employee == True:
                                employee_data=[]
                                for ret in exam.employee_id:
                                    employee_data.append(ret.user_id.id)
                                if request.env.uid in employee_data:
                                    exam_link = exam.redirect_exam()
                                    return request.redirect(exam_link)
                                else:
                                    return http.request.render('openeducat_quiz.quiz_error_page', post)

                            elif exam.academy_exam == True:
                                student_data= []
                                for c in exam.student_id:
                                    student_data.append(c.user_id.id)
                                if request.env.uid in student_data:
                                    exam_link = exam.redirect_exam()
                                    return request.redirect(exam_link)
                                else:
                                    return http.request.render('openeducat_quiz.quiz_error_page', post)
                else:
                    result.write({
                        'user_id': request.env.user.id
                    })

        audio = False
        video = False
        html = False
        if exam.start_view == 'audio' and exam.quiz_audio:
            audio = '<audio controls controlsList="nodownload" \
            class="col-md-12"><source \
            src="data:audio/mp3;base64,%s"></audio>' % exam.quiz_audio
        elif exam.start_view == 'video' and exam.quiz_video:
            video = '<video controls controlsList="nodownload" \
            style="height: 450px;" class="col-md-12"><source \
            src="data:video/mp4;base64,%s"></video>' % exam.quiz_video
        elif exam.start_view == 'html':
            html = exam.quiz_html

        post.update({
            'audio': audio,
            'exam': exam,
            'video': video,
            'html': html,
            'result': result,
            'user': request.env.user
        })
        single_page = 0
        if not result.quiz_id.single_que:
            single_page = 1
        post.update({'single_page': single_page})
        return http.request.render('openeducat_quiz.quiz_starting_page', post)

    # Submit the Single page single question form submition
    #mỗi khi bấm tiếp theo trong bảng trả lời câu hỏi
    @http.route('/quiz/attempt/record', type="http", auth="public",
                website=True)
    def quiz_result_attempt(self, **kwargs):
        print('kết thúc bài thi')
        if kwargs.get('question', False):
            result_line = request.env['op.quiz.result.line']
            line = result_line.browse(
                int(kwargs['question']))
            if 't_spent_time' in kwargs and kwargs['t_spent_time']:
                if line.result_id.quiz_id.time_config:
                    time_val = kwargs['t_spent_time'].split(':')
                    line.result_id.write({
                        'time_spent_hr': time_val[0],
                        'time_spent_minute': time_val[1],
                        'time_spent_second': time_val[2]
                    })
            if 'answer' in kwargs and kwargs['answer']:
                if line.que_type == 'optional':
                    answer = request.env[
                        'op.quiz.result.line.answers'].browse(
                        int(kwargs['answer']))
                    line.given_answer = answer.name
                    line.mark = answer.grade_id.value * \
                                line.question_mark / 100
                elif line.que_type == 'blank':
                    line.given_answer = str(kwargs['answer'])
                    if line.case_sensitive:
                        if line.answer == line.given_answer:
                            received_mark = (line.question_mark * (
                                    line.grade_true_id.value or 0.0)) / 100
                            line.mark = received_mark
                        else:
                            received_mark = (line.question_mark * (
                                    line.grade_false_id.value or 0.0)) / 100
                            line.mark = received_mark
                    else:
                        if line.answer.lower() == line.given_answer.lower():
                            received_mark = (line.question_mark * (
                                    line.grade_true_id.value or 0.0)) / 100
                            line.mark = received_mark
                        else:
                            received_mark = (line.question_mark * (
                                    line.grade_false_id.value or 0.0)) / 100
                            line.mark = received_mark
                elif line.que_type == 'descriptive':
                    line.given_answer = str(kwargs['answer'])
            line_val = line.result_id.get_prev_next_result(line.id)
            if line_val['next_result']:
                return request.redirect('/quiz/attempt/%s/question/%s' % (
                    line.result_id.id, int(line_val['next_result'])))
            else:
                result_line.search_count(
                    [('result_id', '=', line.result_id.id),
                     ('que_type', '=', 'descriptive')])
                line.result_id.state = 'done'
                if not line.result_id.quiz_id.show_result:
                    return http.request.render(
                        'openeducat_quiz.quiz_completed', {})
                return request.redirect('/exam/score/%s' % (line.result_id.id))

    #bấm nút kết thúc sẽ chạy đến hàm này
    @http.route('/exam/score/<model("op.quiz.result"):result>', type='http',
                auth='user', website=True)
    def exam_final_result(self, result, **post):
        print('kết thúc')
        result.state = 'done'
        result.finish_date = datetime.now()
        data = result.get_answer_data()
        return http.request.render(
            'openeducat_quiz.quiz_results', data)

    #bấm bắt đầu thi lần t2
    #bấm nút tiếp theo mỗi lần muốn nhảy qua câu hỏi tiếp theo
    @http.route([
        '/quiz/attempt/<model("op.quiz.result"):result>',
        '/quiz/attempt/<model("op.quiz.result"):result>/question/<model(\
        "op.quiz.result.line"):line>',
        '/quiz/attempt/<model("op.quiz.result"):result>/question/<model(\
        "op.quiz.result.line"):line>/prev/<string:spent_time>',
    ], type='http', auth='user', website=True)
    def render_quiz(self, result, line=False, spent_time=None, **post):
        exam = result.quiz_id
        result.start_quiz = datetime.now()
        print(result.start_quiz)
        print(exam.time_limit_minute)
        if exam.auth_required and request.env.user._is_public():
            return request.render("openeducat_quiz.auth_required", {'quiz': exam, 'result': result})

        if result.user_id.id != request.env.uid:
            return http.request.render('openeducat_quiz.quiz_warning_page', post)

        if spent_time:
            print(spent_time, 'spent time')
            time_val = spent_time.split(':')
            result.write({
                'time_spent_hr': time_val[0],
                'time_spent_minute': time_val[1],
                'time_spent_second': time_val[2]
            })
        post['exam'] = result.quiz_id
        post['user'] = request.env.user
        next_allow = 0
        prev_allow = 0
        if line:
            print(line, 'line')
            result_val = result.get_prev_next_result(line.id)
            if result_val['next_result']:
                next_allow = 1
            if result_val['prev_result']:
                prev_allow = 1
            post.update({
                'next_result': result_val['next_result'],
                'prev_result': result_val['prev_result'],
                'question_no': result_val['question_no'],
                'next_allow': next_allow,
                'line': line
            })
        else:
            for qline in result.line_ids:
                if qline.given_answer:
                    line = qline
            if line:
                result_val = result.get_prev_next_result(line.id)
                if result_val['next_result']:
                    next_allow = 1
                if result_val['prev_result']:
                    prev_allow = 1
                post.update({
                    'next_result': result_val['next_result'],
                    'prev_result': result_val['prev_result'],
                    'question_no': result_val['question_no'],
                    'next_allow': next_allow,
                    'line': line
                })
            else:
                prev_result = False
                next_result = False
                if not result.line_ids:
                    return True
                if len(result.line_ids) > 1:
                    next_result = request.env['op.quiz.result.line'].browse(
                        result.line_ids.ids[1])
                line = request.env['op.quiz.result.line'].browse(
                    result.line_ids.ids[0])
                if next_result:
                    next_allow = 1
                post.update({
                    'next_result': next_result,
                    'prev_result': prev_result,
                    'question_no': 1,
                    'next_allow': next_allow,
                    'line': line
                })
        given_answer_id = line.get_line_answer()
        post['given_answer'] = given_answer_id
        is_required = 0
        is_readonly = 0
        is_prev = 0
        if given_answer_id > 0:
            if line.result_id.quiz_id.prev_readonly:
                is_readonly = 1
        if line.result_id.quiz_id.que_required:
            is_required = 1
        if line.result_id.quiz_id.prev_allow and prev_allow:
            is_prev = 1
        if line.result_id.quiz_id.prev_readonly and line.given_answer:
            is_readonly = 1
        post.update({
            'is_required': is_required,
            'is_readonly': is_readonly,
            'prev_allow': is_prev,
            'grid_data': line.result_id.get_quiz_grid_data(line),
            'progress': line.result_id.get_progress_data()
        })
        time_hr = 0
        time_minute = 0
        time_spent_hr = 0
        time_spent_minute = 0
        time_spent_second = 0
        if result.quiz_id.time_config:
            time_hr = result.quiz_id.time_limit_hr or 0
            time_minute = result.quiz_id.time_limit_minute or 0
            if result.time_spent_hr:
                time_spent_hr = result.time_spent_hr or 0
            if result.time_spent_minute:
                time_spent_minute = result.time_spent_minute or 0
            if not time_spent_hr and not time_spent_minute:
                time_spent_hr = time_hr
                time_spent_minute = time_minute
            time_spent_second = result.time_spent_second or 0
        post.update({
            'time_hr': time_hr,
            'time_minute': time_minute
        })
        timer = 1 if time_hr or time_minute else 0
        post.update({
            'timer': timer,
            'time_spent_hr': time_spent_hr,
            'time_spent_minute': time_spent_minute,
            'time_spent_second': time_spent_second,
        })
        return request.render("openeducat_quiz.quiz_render_form_view", post)

    @http.route('/quiz/<model("op.quiz.result"):result>', type='http',
                auth='user', website=True)
    def quiz_render_question(self, result, **post):
        post.update({
            'exam': result.quiz_id,
            'result': result,
            'total_question': result.total_question
        })
        if not result.quiz_id.single_que:
            return request.render("openeducat_quiz.quiz_web_page", post)
        return request.render(
            "openeducat_quiz.quiz_web_page_single", post)

    @http.route('/quiz/results', type="http", auth="public", website=True)
    def quiz_result(self, **kwargs):
        print('finish')
        values = {}
        for field_name, field_value in kwargs.items():
            values[field_name] = field_value
        result = request.env['op.quiz.result'].browse(int(values['ExamID']))
        result.state = 'done'
        quiz = result.quiz_id
        value = self.get_quiz_result_data(values)
        if not quiz.show_result:
            return http.request.render('openeducat_quiz.quiz_completed', {})
        return http.request.render('openeducat_quiz.quiz_results', value)

    # bấm bắt đầu thi lần t2
    # sau mỗi lần next câu hỏi thì chạy đến đây
    @http.route('/quiz/configuration', type="json", auth="public", website=True)
    def quiz_configuration(self, result_id, **kwargs):
        if result_id:
            result = request.env['op.quiz.result'].browse(int(result_id))
            quiz = result.quiz_id
            data = {
                'prev_allow': 1 if quiz.prev_allow else 0,
                'prev_readonly': 1 if quiz.prev_readonly else 0,
                'que_required': 1 if quiz.que_required else 0,
                'single_que': 1 if quiz.single_que else 0,
            }
            return data
        return {}


class CustomerPortal(CustomerPortal):

    @http.route()
    def home(self, **kw):
        """ Add sales documents to main account page """
        response = super(CustomerPortal, self).home(**kw)
        user = request.env['res.users'].browse(request.env.uid)
        exam_count = request.env['op.quiz.result'].sudo().search_count(
            [('user_id', '=', user.id), ('state', '=', 'done')])
        response.qcontext.update({
            'exam_count': exam_count
        })
        return response
