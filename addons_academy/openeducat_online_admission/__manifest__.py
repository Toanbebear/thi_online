# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

{
    'name': 'OpenEduCat Online Admission',
    'version': '13.0',
    'category': 'Education',
    "sequence": 3,
    'summary': 'Online Admission',
    'complexity': "easy",
    'description': """
        This module provide Online Admission Details
    """,
    'author': 'Tech Receptives',
    'website': 'http://www.openeducat.org',
    'depends': [
        'website_sale',
        'website_payment',
        'openeducat_admission',
        'openeducat_core_enterprise'
    ],
    'data': [
        'views/admission_view.xml',
        'views/course_view.xml',
        'views/admission_website_view.xml',
    ],
    'images': [
        'static/description/openeducat_online_admission_banner.jpg',
    ],
    'demo': [],
    'css': [],
    'qweb': [],
    'js': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 125,
    'currency': 'EUR',
    'license': 'OPL-1',
    'live_test_url': 'https://www.openeducat.org/plans'
}
