# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

{
    'name': 'Admission Blog',
    'version': '13.0',
    'category': 'Education',
    "sequence": 3,
    'summary': 'Admission blog',
    'complexity': "easy",
    'description': """
        This module provide feature of LMS Blog.
    """,
    'author': 'Tech Receptives',
    'website': 'http://www.openeducat.org',
    'depends': [
        'website_blog',
        'openeducat_admission',
    ],
    'data': [
        # 'security/op_sequrity.xml',
        # 'security/ir.model.access.csv',
        # 'views/blog_post_view.xml',
        'views/course_view.xml',
        'views/web_admission_blog_view.xml',
    ],
    'demo': [
    ],
    'images': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 35,
    'currency': 'EUR',
    'license': 'OPL-1',
    'live_test_url': 'https://www.openeducat.org/plans'
}
