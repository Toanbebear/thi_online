# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

{
    'name': 'Library Barcode Scanning System',
    'version': '13.0',
    'category': 'Education',
    'description': """Library barcode.""",
    'author': 'Tech Receptives',
    'website': 'http://www.openeducat.org',
    'depends': [
        'barcodes',
        'openeducat_library',
        'openeducat_core_enterprise',
    ],
    'installable': True,
    'auto_install': False,
    'data': [
        'views/openeducat_library_barcode_template.xml',
        'views/library_barcode.xml',
        # 'views/barcode_view.xml',
    ],
    'qweb': [
        "static/src/xml/openeducat_library_barcode_template.xml"
    ],
    'images': [
        'static/description/openeducat_library_barcode_banner.jpg',
    ],
    'application': False,
    "sequence": 3,
    'price': 150,
    'currency': 'EUR',
    'license': 'OPL-1',
    'live_test_url': 'https://www.openeducat.org/plans'
}
