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
    'name': 'OpenEduCat LMS Gamification',
    'version': '13.0',
    'category': 'Education',
    "sequence": 3,
    'summary': 'LMS',
    'complexity': "easy",
    'description': """
        This module provide feature of LMS Gamification.
    """,
    'author': 'Tech Receptives',
    'website': 'http://www.openeducat.org',
    'depends': [
        'gamification',
        'openeducat_lms',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/course_view.xml',
        'views/gamification_badges_view.xml',
        # 'menus/op_menu.xml',
    ],
    'demo': [
        'demo/challenges_data.xml'
    ],
    'images': [
        'static/description/openeducat_lms_gamification_banner.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 30,
    'currency': 'EUR',
    'license': 'OPL-1',
    'live_test_url': 'https://www.openeducat.org/plans'
}
