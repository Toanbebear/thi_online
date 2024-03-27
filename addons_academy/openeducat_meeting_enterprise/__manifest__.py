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
    'name': 'OpenEduCat Meeting Enterprise',
    'version': '13.0',
    'category': 'Education',
    "sequence": 3,
    'summary': 'Manage Meeting',
    'complexity': "easy",
    'description': """
        This module provide Meeting system.
    """,
    'author': 'Tech Receptives',
    'website': 'http://www.openeducat.org',
    'depends': [
        'calendar',
        'openeducat_parent',
        'openeducat_core_enterprise',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/op_meeting_wizard_view.xml',
        'views/op_meeting_view.xml',
        'views/res_partner_category_data.xml',
    ],
    'demo': [
        'demo/calendar_event_type_data.xml',
        'demo/op_meeting_demo.xml',
    ],
    'test': [
        'test/res_users_test.yml',
        'test/parent_faculty_meeting.yml'
    ],
    'images': [
        'static/description/openeducat_meeting_enterprise_banner.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 75,
    'currency': 'EUR',
    'license': 'OPL-1',
    'live_test_url': 'https://www.openeducat.org/plans'
}
