# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

{
    'name': 'OpenEduCat Library Enterprise',
    'version': '13.0',
    'category': 'Education',
    "sequence": 3,
    'summary': 'Manage Library',
    'complexity': "easy",
    'description': """
        This module provide feature of Library Management.
    """,
    'author': 'Tech Receptives',
    'website': 'http://www.openeducat.org',
    'depends': [
        'openeducat_library',
        'openeducat_core_enterprise',
    ],
    'data': [
        'security/op_security.xml',
        'security/ir.model.access.csv',
        'wizards/barcode_issue_media_view.xml',
        'views/media_view.xml',
        'views/media_unit_view.xml',
        'views/media_movement_view.xml',
        'views/library_dashboard_view.xml',
    ],
    'demo': [
    ],
    'images': [
        'static/description/openeducat_library_enterprise_banner.jpg',
    ],
    'qweb': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 100,
    'currency': 'EUR',
    'license': 'OPL-1',
    'live_test_url': 'https://www.openeducat.org/plans'
}
