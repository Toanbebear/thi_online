# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

{
    'name': 'OpenEduCat Classroom Enterprise',
    'version': '13.0',
    'category': 'Education',
    "sequence": 3,
    'summary': 'Manage Classroom',
    'complexity': "easy",
    'description': """
        This module adds classroom management feature to OpenEduCat_Core.
    """,
    'author': 'Tech Receptives',
    'website': 'http://www.openeducat.org',
    'depends': [
        'openeducat_classroom',
        'openeducat_core_enterprise',
    ],
    'data': [
        'security/op_security.xml',
    ],
    'demo': [
    ],
    'images': [
        'static/description/openeducat_classroom_enterprise_banner.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 75,
    'currency': 'EUR',
    'license': 'OPL-1',
    'live_test_url': 'https://www.openeducat.org/plans'
}
