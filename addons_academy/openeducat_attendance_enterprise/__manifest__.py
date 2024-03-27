# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

{
    'name': 'OpenEduCat Attendance Enterprise',
    'version': '13.0',
    'category': 'Education',
    "sequence": 3,
    'summary': 'Manage Attendances',
    'complexity': "easy",
    'description': """
        This module provide feature of Attendance Management.

    """,
    'author': 'Tech Receptives',
    'website': 'http://www.openeducat.org',
    'depends': [
        'openeducat_attendance',
        'openeducat_core_enterprise'
    ],
    'data': [
        'security/op_security.xml',
        'views/attendance_sheet_view.xml',
        'views/openeducat_dashboard_view.xml',
    ],
    'demo': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': [
        'static/description/openeducat_attendance_enterprise_banner.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 75,
    'currency': 'EUR',
    'license': 'OPL-1',
    'live_test_url': 'https://www.openeducat.org/plans'
}
