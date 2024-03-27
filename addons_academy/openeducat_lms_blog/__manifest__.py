# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

{
    'name': 'OpenEduCat LMS Blog',
    'version': '13.0',
    'category': 'Education',
    "sequence": 3,
    'summary': 'LMS',
    'complexity': "easy",
    'description': """
        This module provide feature of LMS Blog.
    """,
    'author': 'Tech Receptives',
    'website': 'http://www.openeducat.org',
    'depends': [
        'website_blog',
        'openeducat_lms',
    ],
    'data': [
        'security/op_sequrity.xml',
        'security/ir.model.access.csv',
        'views/blog_post_view.xml',
        'views/course_view.xml',
        'views/lms_blog_view.xml',
    ],
    'demo': [
        'demo/blog_demo_data.xml',
        'demo/blog_tag_demo_data.xml',
        'demo/blog_post_demo_data.xml'
    ],
    'images': [
        'static/description/openeducat_lms_blog_banner.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 35,
    'currency': 'EUR',
    'license': 'OPL-1',
    'live_test_url': 'https://www.openeducat.org/plans'
}
