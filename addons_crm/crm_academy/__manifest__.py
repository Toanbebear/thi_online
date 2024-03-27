# -*- coding: utf-8 -*-
#############################################################################
#
#    SCI SOFTWARE
#
#    Copyright (C) 2019-TODAY SCI Software(<https://www.scisoftware.xyz>)
#    Author: SCI Software(<https://www.scisoftware.xyz>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

{
    'name': 'CRM Academy',
    'version': '1.0',
    'category': 'CRM with Education',
    "sequence": 5,
    'author': 'Hai Nguyen Ngoc',

    'depends': ['openeducat_erp_enterprise', 'openeducat_erp', 'openeducat_core_enterprise', 'survey_base', 'crm_base'
                ],
    'data': [
        'security/ir.model.access.csv',
        'security/rule.xml',
        'views/view_lead.xml',
        'views/op_course.xml',
        'views/tuition_view.xml',
        'views/check_partner_form.xml',
        'views/op_batch.xml',
        'wizard/request_payment.xml',
        'views/crm_debt_review.xml',
        'wizard/request_debt.xml',
        'views/template_attachment.xml',
        'views/student_view.xml',
        'views/internal_batch_survey.xml',
        'views/session_view.xml',
        'wizard/student_from_booking.xml',
        'report/internal_general_report.xml',
        'report/student_report.xml',
        'report/training_qualify_reports.xml',
        'report/materials_report_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
