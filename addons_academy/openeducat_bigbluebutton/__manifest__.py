# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

{
    'name': 'OpenEduCat Bigbluebutton Integration',
    'version': '13.0',
    'category': 'Education',
    "sequence": 3,
    'summary': 'BigBlueButton',
    'complexity': "easy",
    'description': """
        This module provide BigBlueButton Integration
    """,
    'author': 'Tech Receptives',
    'website': 'http://www.openeducat.org',
    'depends': [
        'openeducat_timetable',
        'openeducat_core_enterprise',
    ],
    'data': [
        "wizard/meeting_view.xml",
        "wizard/meeting_link_view.xml",
        "views/session_view.xml",
    ],
    'images': [
        'static/description/openeducat_bigbluebutton_banner.jpg',
    ],
    'demo': [],
    'css': [],
    'qweb': [],
    'js': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 75,
    'currency': 'EUR',
    'license': 'OPL-1',
    'live_test_url': 'https://www.openeducat.org/plans'
}
