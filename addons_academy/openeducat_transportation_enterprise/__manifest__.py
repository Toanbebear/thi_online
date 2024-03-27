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
    'name': 'OpenEduCat Transportation Enterprise',
    'version': '13.0',
    'category': 'Education',
    "sequence": 3,
    'summary': 'Manage Transportations',
    'complexity': "easy",
    'description': """
        This module provide feature of Transportations.
    """,
    'author': 'Tech Receptives',
    'website': 'http://www.openeducat.org',
    'depends': [
        # 'fleet',
        'openeducat_core_enterprise',
    ],
    'data': [
        'security/op_security.xml',
        'security/ir.model.access.csv',
        'views/sequence.xml',
        'views/stop_view.xml',
        'views/route_line_view.xml',
        'views/stop_line_view.xml',
        'views/route_view.xml',
        'views/vehicle_view.xml',
        # 'menus/op_menu.xml',
    ],
    'test': [
        'test/res_users_test.yml',
        'test/transport_sub_value.yml'
    ],
    'demo': [
        'demo/vehicle_demo.xml',
        'demo/route_demo.xml',
        'demo/route_line_demo.xml',
        'demo/stop_demo.xml',
        'demo/res_demo.xml'
    ],
    'images': [
        'static/description/openeducat_transportation_enterprise_banner.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 100,
    'currency': 'EUR',
    'license': 'OPL-1',
    'live_test_url': 'https://www.openeducat.org/plans'
}
