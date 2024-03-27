# -*- coding: utf-8 -*-
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': "Web of Admission",
    'version': '13.0',
    'license': 'LGPL-3',
    'category': 'Education',
    'sequence': 3,
    'summary': "Web Admissions""",
    'complexity': "easy",
    'author': 'Tech Receptives',
    'website': 'http://www.openeducat.org',
    'depends': [ 'openeducat_core',
                 'openeducat_fees',
                 'portal',
                 'website_mail',
                 'website_rating',
                 'auth_signup',
                 'openeducat_admission',
                 ],
    'data': [
        'views/ofcourse.xml',
        'views/ofcourse_detail.xml',
        'views/website_ofcourse.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'images': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
