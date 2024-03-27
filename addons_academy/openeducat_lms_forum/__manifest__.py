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
    'name': 'OpenEduCat LMS Forum',
    'version': '13.0',
    'category': 'Education',
    "sequence": 3,
    'summary': 'LMS',
    'complexity': "easy",
    'description': """
        This module provide feature of LMS Forum.
    """,
    'author': 'Tech Receptives',
    'website': 'http://www.openeducat.org',
    'depends': [
        'website_forum',
        'openeducat_lms',
    ],
    'data': [
        'security/op_sequrity.xml',
        'security/ir.model.access.csv',
        'views/course_view.xml',
        'views/lms_forum_view.xml',
    ],
    'demo': [
        'demo/op_course_forum_data.xml',
    ],
    'images': [
        'static/description/openeducat_lms_forum_banner.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 35,
    'currency': 'EUR',
    'license': 'OPL-1',
    'live_test_url': 'https://www.openeducat.org/plans'
}
