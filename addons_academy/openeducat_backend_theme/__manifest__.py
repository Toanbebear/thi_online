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
    'name': 'OpenEduCat Backend Theme',
    'category': 'Education',
    'version': '13.0',
    'author': 'Tech Receptives',
    'website': 'http://www.openeducat.org',
    'summary': 'Backend Theme',
    'description': """Backend Theme""",

    'depends': [
        'web'
    ],

    'data': [
        'views/assets.xml',
        'views/home.xml',
    ],

    'qweb': [
        'static/src/xml/*.xml'
    ],
    'images': ['static/description/openeducat_backend_theme_banner.jpg'],
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 100,
    'currency': 'EUR',
    'license': 'OPL-1',
    'live_test_url': 'https://www.openeducat.org/plans'
}
