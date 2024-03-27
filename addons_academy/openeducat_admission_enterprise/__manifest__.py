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
    'name': "OpenEduCat Admission Enterprise",
    'version': '13.0',
    'category': 'Education',
    'sequence': 3,
    'summary': "Manage Admissions""",
    'complexity': "easy",
    'description': """
        This is gives the feature of admission process.
    """,
    'author': 'Tech Receptives',
    'website': 'http://www.openeducat.org',
    'depends': [
        'openeducat_admission',
        'openeducat_core_enterprise'
    ],
    'data': [
        'security/op_security.xml',
        'data/invoice_cron.xml',
        'views/admission_view.xml',
        'views/openeducat_dashboard_view.xml',
    ],
    'demo': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': [
        'static/description/openeducat_admission_enterprise_banner.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 75,
    'currency': 'EUR',
    'license': 'OPL-1',
    'live_test_url': 'https://www.openeducat.org/plans'
}
