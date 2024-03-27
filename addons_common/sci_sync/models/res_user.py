# -*- coding: utf-8 -*-
###################################################################################
from odoo import models, fields

from odoo import api, fields, models, _
from odoo.tools import float_round
from xmlrpc.client import dumps, loads
import xmlrpc.client
import logging
import ssl

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'res.users'

    erp_id = fields.Integer()

    def _sync_hr_employee(self):
        url = "https://baocao.scigroup.com.vn"
        db = '2022_11_04_05_00_01'
        username = 'hungtn@scigroup.com.vn'
        password = '123@123'

        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url), verbose=False, use_datetime=True, context=ssl._create_unverified_context())

        # Login
        uid = common.authenticate(db, username, password, {})

        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url), verbose=False, use_datetime=True, context=ssl._create_unverified_context())

        employees = models.execute_kw(db, uid, password,
                                      'res.users', 'search_read',
                                      [],
                                      {'fields': ['id', 'name', 'login', 'employee_id', 'company_id']})

        company = self.env['res.company']

        for employee in employees:
            if employee['work_email']:
                domain = ['|', ('work_email', '=', employee['work_email']), ('erp_id', '=', employee['id'])]
            else:
                domain = ['|', ('code', '=', employee['employee_code']), ('erp_id', '=', employee['id'])]

            records = self.env['hr.employee'].search(domain)

            if records:
                print(domain)
                _logger.info('Update: %s', records)
                record = records[0]
                record.write({
                    'code': employee['employee_code'],
                    'name': employee['name'],
                    'work_email': employee['work_email'],
                    'company_id': company.search([('erp_id', '=', employee['company_id'][0])]).id,
                    'erp_id': employee['id'],
                })
            else:
                # Thêm mới
                rec = self.env['hr.employee'].create({
                    'code': employee['employee_code'],
                    'name': employee['name'],
                    'work_email': employee['work_email'],
                    'company_id': company.search([('erp_id', '=', employee['company_id'][0])]).id,
                    'erp_id': employee['id'],
                })
                _logger.info('Create: %s', rec)
