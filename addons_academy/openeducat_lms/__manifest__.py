# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

{
    'name': 'OpenEduCat LMS',
    'version': '13.0',
    'category': 'Education',
    "sequence": 3,
    'summary': 'LMS',
    'complexity': "easy",
    'description': """
        This module provide feature of LMS.
    """,
    'author': 'Tech Receptives',
    'website': 'http://www.openeducat.org',
    'depends': [
        'portal',
        'website_mail',
        'website_rating',
        'auth_signup',
        'openeducat_core',
        'openeducat_quiz',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'wizard/course_invitation_view.xml',
        'data/course_invitation.xml',
        'data/material_reminder.xml',
        'data/auth_signup.xml',
        'views/quiz_view.xml',
        'views/course_catagory_view.xml',
        'views/course_view.xml',
        'views/faculty_view.xml',
        'views/course_detail.xml',
        'views/course_material.xml',
        'views/course_enrollment_view.xml',
        'views/website_lms.xml',
        'views/lms_embed.xml',
        # 'views/rating_template.xml',
        'views/material_detail_view.xml',
        'views/my_courses.xml',
        'dashboard/openeducat_lms_dashboard_view.xml',
        'menus/op_menu.xml',
    ],
    'demo': [
        'demo/op_course_category_data.xml',
        'demo/op_material_data.xml',
        'demo/op_course_data.xml',
        'demo/op_course_section_data.xml',
        'demo/op_course_material_data.xml',
        'demo/res_users_data.xml',
        'demo/enrollement_demo_data.xml',
        'demo/rating_message_data.xml',
    ],
    'images': [
        'static/description/openeducat_lms_banner.jpg',
    ],
    'qweb': [
        'static/src/xml/openeducat_lms_dashboard.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 150,
    'currency': 'EUR',
    'license': 'OPL-1',
    'live_test_url': 'https://www.openeducat.org/plans'
}
