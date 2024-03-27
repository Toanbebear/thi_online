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
    'name': 'OpenEduCat ERP Enterprise',
    'version': '1.0',
    'category': 'Education',
    "sequence": 8,
    'summary': 'Manage Students, Faculties and Education Institute',
    'complexity': "easy",
    'author': 'Tech Receptives',
    'website': 'http://www.openeducat.org',
    'depends': [
        'openeducat_erp',
        'openeducat_achievement_enterprise',
        'openeducat_activity_enterprise',
        'openeducat_admission_enterprise',
        'openeducat_alumni_enterprise',
        'openeducat_assignment_enterprise',
        'openeducat_attendance_enterprise',
        'openeducat_bigbluebutton',
        # 'openeducat_campus_enterprise',
        'openeducat_classroom_enterprise',
        # 'openeducat_discipline',
        'openeducat_exam_enterprise',
        'openeducat_facility_enterprise',
        # 'openeducat_fees_enterprise',
        'openeducat_health_enterprise',
        # 'openeducat_library_barcode',
        # 'openeducat_library_enterprise',
        'openeducat_lms',
        'openeducat_lms_blog',
        'openeducat_lms_forum',
        'openeducat_lms_gamification',
        'openeducat_lms_sale',
        'openeducat_lms_survey',
        # 'openeducat_meeting_enterprise',
        'openeducat_online_admission',
        'openeducat_parent_enterprise',
        'openeducat_placement_enterprise',
        # 'openeducat_scholarship_enterprise',
        'openeducat_timetable_enterprise',
        #'openeducat_transportation_enterprise',
    ],
    'images': [
        'static/description/openeducat_erp_banner.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
    'live_test_url': 'https://www.openeducat.org/plans'
}
