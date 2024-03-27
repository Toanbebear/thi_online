# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

{
    'name': 'OpenEduCat Campus Enterprise',
    'version': '13.0',
    'category': 'Education',
    "sequence": 3,
    'summary': 'Manage Campus',
    'complexity': "easy",
    'description': """
        This module adds campus management
        feature to OpenEduCat_Core_Enterprise.
    """,
    'author': 'Tech Receptives',
    'website': 'http://www.openeducat.org',
    'depends': [
        'account',
        'openeducat_core_enterprise',
    ],
    'data': [
        'security/op_security.xml',
        'security/ir.model.access.csv',
        'wizard/facility_create_invoice_view.xml',
        'views/facility_type_view.xml',
        'views/facility_allocation_view.xml',
        'views/facility_view.xml',
        # 'menus/op_menu.xml',
    ],
    'demo': [
        'demo/product_demo.xml',
        'demo/facility_type_demo.xml',
        'demo/facility_demo.xml',
        'demo/facility_allocation_demo.xml',
    ],
    'test': [
        'test/facility_invoice_creation.yml',
    ],
    'images': [
        'static/description/openeducat_campus_enterprise_banner.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 75,
    'currency': 'EUR',
    'license': 'OPL-1',
    'live_test_url': 'https://www.openeducat.org/plans'
}
