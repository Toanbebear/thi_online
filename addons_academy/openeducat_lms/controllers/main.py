# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

import base64
import calendar
import werkzeug
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo import fields, tools
from odoo import http
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.openeducat_quiz.controllers.main import OpeneducatQuizRender
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import AccessError
from odoo.http import request

PPG = 12  # Products Per Page
PPR = 4  # Products Per Row


class OpeneducatQuizRenderInherit(OpeneducatQuizRender):

    def get_quiz_result_data(self, values):
        res = super(OpeneducatQuizRenderInherit, self).get_quiz_result_data(
            values)
        res['course_val'] = False
        res['material_val'] = False
        res['section_val'] = False
        return res

    @http.route()
    def quiz_result(self, **kwargs):
        val = super(OpeneducatQuizRenderInherit, self).quiz_result(**kwargs)
        values = {}
        for field_name, field_value in kwargs.items():
            values[field_name] = field_value
        result = request.env['op.quiz.result'].browse(int(values['ExamID']))
        if result.quiz_id.lms and values['CourseID']:
            course = request.env['op.course'].browse(
                int(values['CourseID']))
            material = request.env['op.material'].browse(
                int(values['MaterialID']))
            section = request.env['op.course.section'].browse(
                int(values['SectionID']))
            return request.redirect(
                '/course/%s/section/%s/material/%s/result/%s' % (
                    course.id, section.id, material.id, result.id))
        return val


class OpenEduCatLms(http.Controller):
    # --------------------------------------------------
    # MAIN / SEARCH
    # --------------------------------------------------

    @http.route(['/become-instructor'], type='http', auth="user",
                website=True, csrf=False)
    def register_faculty(self, **kwargs):
        faculty_group = request.env.ref('openeducat_core.group_op_faculty')
        faculty_ref = request.env['op.faculty']
        faculty = faculty_ref.sudo().search(
            [('user_id', '=', request.env.uid)])
        if not faculty:
            faculty = faculty_ref.sudo().create(
                {'partner_id': request.env.user.partner_id.id,
                 'last_name': kwargs.get('last_name', False),
                 'gender': kwargs.get('gender', False),
                 'birth_date': kwargs.get('birth_date', False),
                 'bio_data': kwargs.get('bio_data', False),
                 'designation': kwargs.get('designation', False)})
            faculty.sudo().user_id = request.env.user.id
            group_ids = faculty.user_id.groups_id.ids
            group_ids.append(faculty_group.id)
            faculty.user_id.sudo().groups_id = [[6, 0, list(set(group_ids))]]
        elif not faculty.user_id.has_group('openeducat_core.group_op_faculty'):
            group_ids = faculty.user_id.groups_id.ids
            group_ids.append(faculty_group.id)
            faculty.user_id.sudo().groups_id = [[6, 0, list(set(group_ids))]]
        return request.redirect('/courses')

    @http.route(['''/course/enroll/<model("op.course"):course>'''],
                type='http', auth="user", website=True)
    def enroll_course(self, course, **kwargs):
        course_ref = request.env['op.course.enrollment']
        student_ref = request.env['op.student']
        enrollment = course_ref.sudo().search(
            [('user_id', '=', request.env.user.id),
             ('course_id', '=', course.id)])
        if not enrollment:
            course_ref.sudo().create({
                'user_id': request.env.user.id,
                'course_id': course.id,
                'enrollment_date': fields.Datetime.now(),
                'state': 'in_progress'})
        student = student_ref.sudo().search(
            [('user_id', '=', request.env.uid)])
        if not student:
            student = request.env['op.student'].sudo().create(
                {'name': request.env.user.name,
                 'partner_id': request.env.user.partner_id.id,
                 'user_id': request.env.uid})
        return request.redirect('/my-courses')

    @http.route([
        '/courses',
        '/courses/page/<int:page>',
        '/courses/category/<model("op.course.category"):category>',
        '/courses/category/<model(\
        "op.course.category"):category>/page/<int:page>'
    ], type='http', auth="public", website=True)
    def courses(self, search='', category=False, page=0, ppg=False, **post):
        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG
        domain = [('online_course', '=', True)]
        url = "/courses"
        if search:
            post["search"] = search
            for srch in search.split(" "):
                domain += [('name', 'ilike', srch)]
        if category:
            url = "/courses/category/%s" % slug(category)
            domain += [('category_ids', 'in', [category.id])]
        course_domain = domain + [
            ('visibility', 'in', ['public', 'logged_user']),
            ('state', '=', 'open')]
        course_ref = request.env['op.course']
        courses = course_ref.sudo().search(course_domain)
        invited_domain = domain + [
            ('invited_users_ids', 'in', [request.env.uid]),
            ('state', '=', 'open')]
        invited_courses = course_ref.sudo().search(invited_domain)
        total_count = len(courses) + len(invited_courses)
        pager = request.website.pager(
            url=url, total=total_count, page=page, step=ppg, scope=7,
            url_args=post)
        all_course_ids = [x.id for x in courses]
        all_course_ids += [x.id for x in invited_courses]
        all_courses = course_ref.sudo().search(
            [('id', 'in', all_course_ids)], limit=ppg, offset=pager['offset'])
        course_category_ref = request.env['op.course.category']
        if category:
            categories = course_category_ref.search(
                [('parent_id', '=', category.id)])
        else:
            categories = course_category_ref.sudo().search(
                [('parent_id', '=', False)])
        values = {
            'search': search,
            'pager': pager,
            'search_count': total_count,
            'courses': all_courses,
            'category': category,
            'categories': categories,
            'rows': 3,
            'user': request.env.user,
            'is_instructor': request.env.user.has_group(
                'openeducat_core.group_op_faculty')
        }
        return request.render("openeducat_lms.courses", values)

    def my_corse_details(self, enrollments):
        courses = []
        for en in enrollments:
            per = 0
            if en and en.course_id.training_material > 0:
                viewed_material = request.env[
                    'op.course.enrollment.material'].sudo().search_count(
                    [('completed', '=', True),
                     ('course_id', '=', en.course_id.id),
                     ('enrollment_id', '=', en.id)])
                per = viewed_material * 100 / en.course_id.training_material
            courses.append({
                'course': en.course_id,
                'enrolled': en.state in [
                    'in_progress', 'done'] and True or False,
                'completed_percentage': per, })
        return {
            'courses': courses,
            'user': request.env.user,
            'is_public_user': request.env.user == request.website.user_id
        }

    @http.route('/my-courses', type='http', auth="public", website=True)
    def my_courses(self, *args, **post):
        # Show Courses To Logged in User
        enrollments = request.env['op.course.enrollment'].sudo().search(
            [('user_id', '=', request.env.uid),
             ('state', 'in', ['in_progress', 'done'])])

        if not enrollments:
            return request.render('openeducat_lms.course_not_found')
        data = self.my_corse_details(enrollments)
        return request.render('openeducat_lms.my-courses', data)

    @http.route('''/course-detail/<model("op.course"):course>''', type='http',
                auth="public", website=True)
    def course(self, course, **kw):
        course = request.env['op.course'].sudo().browse([course.id])
        sections = request.env['op.course.section'].sudo().search(
            [('course_id', '=', course.id)], order='sequence asc')
        enrollment = request.env['op.course.enrollment'].sudo().search(
            [('user_id', '=', request.env.uid),
             ('course_id', '=', course.id),
             ('state', 'in', ['in_progress', 'done'])])
        completed_percentage = enrollment and \
            enrollment.completed_percentage or 0
        ratings = request.env['rating.rating'].sudo().search([
            ('message_id', 'in', course.website_message_ids.ids)])
        rating_message_values = dict(
            [(record.message_id.id, record.rating) for record in ratings])
        rating_course = course.rating_get_stats()
        values = {
            'course': course,
            'enrolled': enrollment and True or False,
            'completed_percentage': completed_percentage,
            'sections': sections,
            'user': request.env.user,
            'is_public_user': request.env.user == request.website.user_id,
            'rating_message_values': rating_message_values,
            'rating_course': rating_course
        }
        return request.render('openeducat_lms.course_detail', values)

    @http.route(['''/course/<model("op.course"):course>''',
                 '''/course/<model("op.course"):course>/section/<model(\
                 "op.course.section"):section>''',
                 '''/course/<model("op.course"):course>/section/<model(\
                 "op.course.section"):section>/material/<model(\
                 "op.material"):material>''',
                 '''/course/<model("op.course"):course>/section/<model(\
                 "op.course.section"):section>/material/<model(\
                 "op.material"):material>/<next>''',
                 '''/course/<model("op.course"):course>/section/<model(\
                 "op.course.section"):section>/material/<model(\
                 "op.material"):material>/result/<model(\
                 "op.quiz.result"):result>'''],
                type='http', auth="user", website=True)
    def get_course_material(self, course, section=None, material=None,
                            result=None, next=None, **kwargs):
        enrollment = request.env['op.course.enrollment'].sudo().search(
            [('course_id', '=', course.id),
             ('user_id', '=', request.env.user.id)], limit=1)

        if not enrollment or not course.sudo().course_section_ids:
            return request.render('openeducat_lms.course_not_found')
        course_enroll_material_ref = request.env[
            'op.course.enrollment.material']
        if section:
            if material:
                if next:
                    next_material = False
                    for x, y in enumerate(section.section_material_ids):
                        if material == y.material_id and x + 1 != len(
                                section.section_material_ids):
                            next_material = section.section_material_ids[
                                x + 1].material_id
                            break

                    if not next_material:
                        next_section = self.get_next_section(course, section)
                        if next_section:
                            return request.redirect('/course/%s/section/%s' % (
                                course.id, next_section.id))
                        else:
                            enrollment.sudo().write(
                                {'completion_date': fields.Datetime.now(),
                                 'state': 'done'})
                        return request.redirect('/my-courses')

                    next_material_access = self.check_material_access(
                        enrollment, next_material)
                    if not next_material_access:
                        return request.redirect(
                            '/course/%s/section/%s/material/%s/1' % (
                                course.id, section.id,
                                next_material.id))

                    cem_id = course_enroll_material_ref.sudo().search(
                        [('course_id', '=', course.id),
                         ('section_id', '=', section.id),
                         ('material_id', '=', next_material.id),
                         ('enrollment_id', '=', enrollment.id)], limit=1)

                    if cem_id:
                        cem_id.sudo().last_access_date = fields.Datetime.now()
                    else:
                        cem_id = self.create_course_enrollment_material(
                            enrollment.id, section.id, next_material.id)

                    return request.redirect(
                        '/course/%s/section/%s/material/%s' % (
                            course.id, section.id, next_material.id))
                else:
                    cem_id = course_enroll_material_ref.sudo().search([
                        ('course_id', '=', course.id),
                        ('section_id', '=', section.id),
                        ('material_id', '=', material.id),
                        ('enrollment_id', '=', enrollment.id)], limit=1)

                    if cem_id:
                        cem_id.sudo().last_access_date = fields.Datetime.now()
                    else:
                        cem_id = self.create_course_enrollment_material(
                            enrollment.id, section.id, material.id)

                    material = material
            else:
                if section.section_material_ids:
                    cem_id = course_enroll_material_ref.sudo().search(
                        [('course_id', '=', course.id),
                         ('section_id', '=', section.id),
                         ('material_id', '=',
                          section.section_material_ids[0].material_id.id),
                         ('enrollment_id', '=', enrollment.id)])
                    if not cem_id:
                        cem_id = self.create_course_enrollment_material(
                            enrollment.id, section.id,
                            section.section_material_ids[0].material_id.id)
                    else:
                        cem_id.sudo().last_access_date = fields.Datetime.now()
                    material = section.section_material_ids[0].material_id

                    material_access = self.check_material_access(
                        enrollment, material)
                    if not material_access:
                        return request.redirect(
                            '/course/%s/section/%s/material/%s/1' % (
                                course.id, section.id, material.id))
                else:
                    next_section = self.get_next_section(course, section)
                    if next_section:
                        return request.redirect('/course/%s/section/%s' % (
                            course.id, next_section.id))
                    else:
                        return request.render(
                            'openeducat_lms.course_not_found')
        else:
            # Display first material of first section
            section_ids = request.env['op.course.section'].search(
                [('course_id', '=', course.id)], order='sequence asc')

            if section_ids and section_ids[0].section_material_ids:
                section = section_ids[0]

                cm_id = request.env['op.course.material'].search(
                    [('course_id', '=', course.id),
                     ('section_id', '=', section.id)],
                    order='sequence asc', limit=1)

                material_access = self.check_material_access(
                    enrollment, cm_id.material_id)
                if not material_access:
                    return request.redirect(
                        '/course/%s/section/%s/material/%s/1' % (
                            course.id, section.id, cm_id.material_id.id))

                cem_id = course_enroll_material_ref.sudo().search(
                    [('course_id', '=', course.id),
                     ('section_id', '=', section.id),
                     ('material_id', '=', cm_id.material_id.id),
                     ('enrollment_id', '=', enrollment.id)], limit=1)

                if cem_id:
                    cem_id.sudo().last_access_date = fields.Datetime.now()
                else:
                    cem_id = self.create_course_enrollment_material(
                        enrollment.id, section.id, cm_id.material_id.id)

                material = cm_id.material_id
            else:
                next_section = self.get_next_section(course, section)
                if next_section:
                    return request.redirect(
                        '/course/%s/section/%s' % (course.id, next_section.id))
                else:
                    return request.render('openeducat_lms.course_not_found')

        related_materials = self.get_related_materials(course, enrollment)
        material = request.env['op.material'].sudo().browse([material.id])
        last_material = False
        if not self.get_next_section(course, section):
            last_material = material == section.section_material_ids[
                                        -1:].material_id and True or False
        data = {
            'course': course,
            'section': section,
            'material': material,
            'user': request.env.user,
            'related_materials': related_materials,
            'last_material': last_material
        }
        # ############ Material if type == Quiz ###########
        if material.sudo().material_type and \
                material.sudo().material_type == 'quiz':
            quiz_limit = 0
            result_val = False
            if material.sudo().quiz_id.no_of_attempt > 0 and not result:
                total_result_ids = 0
                attempt_ids = request.env['op.quiz.result'].search([
                    ('user_id', '=', request.env.uid),
                    ('quiz_id', '=', material.sudo().quiz_id.id)])
                for attempt in attempt_ids:
                    total_correct = attempt.total_correct
                    total_incorrect = attempt.total_incorrect
                    if not total_correct and not total_incorrect:
                        result_val = attempt
                    else:
                        total_result_ids += 1
                if material.sudo().quiz_id.no_of_attempt <= total_result_ids:
                    quiz_limit = 1
            if quiz_limit == 0 and not result:
                if not result_val:
                    result_val = material.sudo().quiz_id.get_result_id()
                data['exam'] = result_val.quiz_id
                data['result'] = result_val
                data['total_question'] = result_val.total_question
                data['course_val'] = course.id
                data['material_val'] = material.sudo().id
                data['section_val'] = section.id
            data['quiz_limit'] = quiz_limit
        is_result = 0
        is_thanks = 0
        if result:
            is_result = 1
            if not result.quiz_id.show_result:
                is_thanks = 1
            else:
                result_data = result.get_answer_data()
                for key in result_data.keys():
                    data.update({key: result_data[key]})
        data['is_result'] = is_result
        data['is_thanks'] = is_thanks
        return request.render('openeducat_lms.material_detail_view', data)

    def check_material_access(self, enrollment, material):
        if not material.website_published:
            return False
        elif material.website_published and not material.auto_publish:
            return True
        elif material.website_published and material.auto_publish:
            if material.auto_publish_type == 'wait_until':
                wait_until_date = datetime.strptime(
                    material.wait_until_date,
                    tools.DEFAULT_SERVER_DATE_FORMAT).date()
                return wait_until_date < date.today() and True or False
            elif material.auto_publish_type == 'wait_until_duration':
                allowed = False
                enrollment_date = datetime.strptime(
                    enrollment.enrollment_date,
                    tools.DEFAULT_SERVER_DATETIME_FORMAT)
                if material.wait_until_duration_period == 'minutes':
                    access_time = enrollment_date + \
                        relativedelta(minutes=material.wait_until_duration)
                    allowed = access_time < datetime.today() and True or False
                elif material.wait_until_duration_period == 'hours':
                    access_time = enrollment_date + \
                            relativedelta(hours=material.wait_until_duration)
                    allowed = access_time < datetime.today() and True or False
                elif material.wait_until_duration_period == 'days':
                    access_time = enrollment_date + \
                            relativedelta(days=material.wait_until_duration)
                    allowed = access_time < datetime.today() and True or False
                elif material.wait_until_duration_period == 'weeks':
                    access_time = enrollment_date + \
                            relativedelta(weeks=material.wait_until_duration)
                    allowed = access_time < datetime.today() and True or False
                elif material.wait_until_duration_period == 'months':
                    access_time = enrollment_date + \
                            relativedelta(months=material.wait_until_duration)
                    allowed = access_time < datetime.today() and True or False
                elif material.wait_until_duration_period == 'years':
                    access_time = enrollment_date + \
                            relativedelta(years=material.wait_until_duration)
                    allowed = access_time < datetime.today() and True or False
                return allowed and True or False

    def create_course_enrollment_material(self, enrollment_id, section_id,
                                          material_id):
        cem_id = request.env['op.course.enrollment.material'].sudo().create(
            {'enrollment_id': enrollment_id,
             'section_id': section_id,
             'material_id': material_id,
             'completed': True,
             'completed_date': fields.Datetime.now(),
             'last_access_date': fields.Datetime.now()})
        return cem_id

    def get_related_materials(self, course, enrollment):
        enroll_material_ref = request.env['op.course.enrollment.material']
        if course.navigation_policy == 'free_learn':
            cs_ids = request.env['op.course.section'].sudo().search([
                ('course_id', '=', course.id)], order='sequence asc')
            data = []
            for x in cs_ids:
                for y in x.section_material_ids:
                    cem_id = enroll_material_ref.sudo().search(
                        [('enrollment_id', '=', enrollment.id),
                         ('section_id', '=', x.id),
                         ('material_id', '=', y.material_id.id)], limit=1)
                    material_access = self.check_material_access(
                        enrollment, y.material_id)
                    if material_access:
                        data.append(
                            {'section': x,
                             'material': y.material_id,
                             'completed': (cem_id and cem_id.completed
                                           ) and True or False})
            return data
        else:
            cem_ids = enroll_material_ref.sudo().search(
                [('enrollment_id', '=', enrollment.id)],
                order='completed_date asc')
            return [{'section': x.section_id, 'material': x.material_id,
                     'completed': x.completed} for x
                    in cem_ids]

    def get_next_section(self, course, section):
        section_ids = request.env['op.course.section'].search(
            [('course_id', '=', course.id)], order='sequence asc')
        next_section = False
        for x, y in enumerate(section_ids):
            if section == y and x + 1 != len(section_ids):
                next_section = section_ids[x + 1]
                break
        return next_section

    @http.route('''/course/material/<model( \
                "op.material", "[('datas', '!=', False), ( \
                'material_type', '=', 'document')]"):material>/pdf_content''',
                type='http', auth="public", website=True)
    def material_get_pdf_content(self, material):
        response = werkzeug.wrappers.Response()
        response.data = material.datas and \
            base64.b64decode(material.datas) or b''
        response.mimetype = 'application/pdf'
        return response

    # --------------------------------------------------
    # EMBED IN THIRD PARTY WEBSITES
    # --------------------------------------------------
    @http.route('/materials/embed/<int:material_id>', type='http',
                auth='public', website=True)
    def materials_embed(self, material_id, page="1", **kw):
        try:
            template = 'openeducat_lms.embed_material'
            material = request.env['op.material'].browse(material_id)
        except AccessError:
            template = 'openeducat_lms.embed_material_forbidden'
            material = request.env['op.material'].sudo().browse(material_id)
        return request.render(template, {'material': material})

    # Dashboard Controllers

    @http.route('/openeducat_lms/fetch_course', type='json', auth='user')
    def fetch_openeducat_lms_course(self):
        course_ids = request.env['op.course'].search_read(
            [('online_course', '=', True)], ['id', 'name'], order='name')
        return {'course_ids': course_ids}

    @http.route('/openeducat_lms/get_lms_dash_data', type='json', auth='user')
    def compute_lms_course_dashboard_data(self, course_id=None):
        enrolled_users = 0
        days_since_launch = 0
        course_duration = 0
        training_material = 0
        course_to_begin = 0
        course_in_progress = 0
        course_completed = 0

        if course_id:
            course = request.env['op.course'].browse([int(course_id)])
            enrolled_users = course.enrolled_users
            days_since_launch = course.days_since_launch
            course_duration = course.display_time
            training_material = course.training_material
            course_to_begin = course.course_to_begin
            course_in_progress = course.course_in_progress
            course_completed = course.course_completed

        return {'enrolled_users': enrolled_users,
                'days_since_launch': days_since_launch,
                'course_duration': course_duration,
                'training_material': training_material,
                'course_to_begin': course_to_begin,
                'course_in_progress': course_in_progress,
                'course_completed': course_completed}

    @http.route('/openeducat_lms/compute_openeducat_graph',
                type='json', auth='user')
    def compute_openeducat_lms_graph(self):
        data = []
        last_day = datetime.today().replace(day=calendar.monthrange(
            datetime.today().year, datetime.today().month)[1])
        for d in range(1, last_day.day + 1):
            label = str(d)
            start_date = datetime.now().replace(
                day=d).strftime('%Y-%m-%d 00:00:00')
            end_date = datetime.now().replace(
                day=d).strftime('%Y-%m-%d 23:59:59')
            count = request.env['op.course.enrollment'].sudo().search_count(
                [('enrollment_date', '>=', start_date),
                 ('enrollment_date', '<=', end_date)])
            data.append({'label': label,
                         'value': count and count or 0})
        return data

    @http.route('/openeducat_lms/compute_openeducat_course_graph',
                type='json', auth='user')
    def compute_openeducat_lms_course_graph(self, course_id=None):
        data = []
        if course_id:
            last_day = datetime.today().replace(
                day=calendar.monthrange(datetime.today().year,
                                        datetime.today().month)[1])
            for d in range(1, last_day.day + 1):
                start_date = datetime.now().replace(
                    day=d).strftime('%Y-%m-%d 00:00:00')
                end_date = datetime.now().replace(
                    day=d).strftime('%Y-%m-%d 23:59:59')
                count = request.env[
                    'op.course.enrollment'].sudo().search_count(
                    [('course_id', '=', int(course_id)),
                     ('enrollment_date', '>=', start_date),
                     ('enrollment_date', '<=', end_date)])
                data.append({'label': str(d), 'value': count and count or 0})
        return data

    @http.route(['/my/course'], type='http', auth='public', website=True)
    def my_lms_profile(self, **post):
        enrollments = request.env['op.course.enrollment'].sudo().search(
            [('user_id', '=', request.env.uid),
             ('state', 'in', ['in_progress', 'done'])])
        data = {'user': request.env.user}
        if enrollments:
            data = self.my_corse_details(enrollments)
        return request.render("openeducat_lms.my_profile", data)


class CustomerPortal(CustomerPortal):

    @http.route()
    def home(self, **kw):
        """ Add sales documents to main account page """
        response = super(CustomerPortal, self).home(**kw)
        count = request.env['op.course.enrollment'].sudo().search_count(
            [('user_id', '=', request.env.uid),
             ('state', 'in', ['in_progress', 'done'])])
        response.qcontext.update({
            'course_count': count
        })
        return response
