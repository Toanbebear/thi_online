# -*- coding: utf-8 -*- 
###################################################################################
from odoo import models, fields

from odoo import api, fields, models, _
from odoo.tools import float_round
from xmlrpc.client import dumps, loads
import xmlrpc.client
import logging
import ssl
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    erp_id = fields.Integer()

    def _sync_hr_department(self):
        url = "https://baocao.scigroup.com.vn"
        db = '2022_11_24_05_00_01'
        username = 'hungtn@scigroup.com.vn'
        password = '123@123'

        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url), verbose=False, use_datetime=True, context=ssl._create_unverified_context())

        # Login
        uid = common.authenticate(db, username, password, {})

        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url), verbose=False, use_datetime=True, context=ssl._create_unverified_context())

        hr_departments = models.execute_kw(db, uid, password,
                                        'hr.department', 'search_read',
                                        [[['root_code', '!=', False], ]],
                                        {'fields': ['id', 'name', 'root_code', 'company_id', 'sector_id']})


        Company = self.env['res.company']
        # Dict vị trí công việc
        companies = self.get_companies()
        departments, department_codes = self.get_departments()

        # Sector = self.env['hr.department.sector']
        for info in hr_departments:
            if info['id'] in departments:
                record = departments[info['id']]
                record.sudo().write({
                    'root_code': info['root_code'],
                    'name': info['name'],
                    # 'active': info['active'],
                })
            else:
                company = info['company_id'][0] if info['company_id'] else False
                company_id = companies.get(company)
                if not company_id:
                    _logger.error("Vui lòng đồng bộ 1.HR: Đồng công ty %s" % info['name'])
                    raise UserError("Vui lòng đồng bộ 1.HR: Đồng công ty")

                if info['root_code'] in department_codes:
                    record = department_codes[info['root_code']]
                    record.sudo().write({
                        'name': info['name'],
                        'company_id': company_id.id,
                        'active': info['active'],
                        'erp_id': info['id']
                    })
                else:
                    val = {
                        'root_code': info['root_code'],
                        'name': info['name'],
                        'company_id': company_id.id,
                        'active': info['active'],
                        'erp_id': info['id']
                    }
                    rec = self.env['hr.department'].create(val)
                    _logger.info('Create department: %s', rec.name)
        _logger.info('Đồng bộ vị trí phòng ban thành công.')

    def get_companies(self):
        companies = self.env['res.company'].search([])
        return dict((company.erp_id, company) for company in companies)

    def get_departments(self):
        hr_departments = self.env['hr.department'].search([])
        departments = dict((department.erp_id, department) for department in hr_departments)
        department_codes = dict((department.root_code, department) for department in hr_departments)
        return departments, department_codes
