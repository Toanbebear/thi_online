# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

{
    'name': 'OpenEduCat Scholarship Enterprise',
    'version': '3.0.0',
    'category': 'Education',
    "sequence": 3,
    'summary': 'Manage Scholarship',
    'complexity': "easy",
    'description': """
        This module adds the feature of scholarship in Openeducat
    """,
    'author': 'Tech Receptives',
    'website': 'http://www.openeducat.org',
    'depends': ['openeducat_core_enterprise'],
    'data': [
        'security/op_security.xml',
        'security/ir.model.access.csv',
        'views/scholarship_view.xml',
        'views/scholarship_type_view.xml',
        'menus/op_menu.xml',
    ],
    'demo': [
        'demo/scholarship_type_demo.xml',
        'demo/scholarship_demo.xml',
    ],
    'images': [
        'static/description/openeducat_scholarship_enterprise_banner.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 50,
    'currency': 'EUR',
    'license': 'OPL-1',
    'live_test_url': 'https://www.openeducat.org/plans'
}
