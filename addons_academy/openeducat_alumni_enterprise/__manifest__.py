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
    'name': 'OpenEduCat Alumni Enterprise',
    'version': '13.0',
    'category': 'Education',
    "sequence": 3,
    'summary': 'Manage Alumni',
    'complexity': "easy",
    'description': """
        This module provide alumni management system.
    """,
    'author': 'Tech Receptives',
    'website': 'http://www.openeducat.org',
    'depends': [
        'openeducat_core_enterprise',
    ],
    'data': [
        'views/alumni_view.xml'
    ],
    'demo': [
        'demo/student_demo.xml',
    ],
    'images': [
        'static/description/openeducat_alumni_enterprise_banner.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 50,
    'currency': 'EUR',
    'license': 'OPL-1',
    'live_test_url': 'https://www.openeducat.org/plans'
}
