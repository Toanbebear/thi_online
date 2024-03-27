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
    'name': 'OpenEduCat Achievement Enterprise',
    'version': '13.0',
    'category': 'Education',
    "sequence": 3,
    'summary': 'Manage Achievement',
    'complexity': "easy",
    'description': """
        This module adds the feature of achievement in Openeducat
    """,
    'author': 'Tech Receptives',
    'website': 'http://www.openeducat.org',
    'depends': [
        'openeducat_core_enterprise'
    ],
    'data': [
        'security/op_security.xml',
        'security/ir.model.access.csv',
        'views/achievement_view.xml',
        'views/achievement_type_view.xml',
        'menus/op_menu.xml',
    ],
    'images': [
        'static/description/openeducat_achievement_enterprise_banner.jpg',
    ],
    'demo': [
        'demo/achievement_type_demo.xml',
        'demo/achievement_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 50,
    'currency': 'EUR',
    'license': 'OPL-1',
    'live_test_url': 'https://www.openeducat.org/plans'
}
