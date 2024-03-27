# -*- coding: utf-8 -*- 
###################################################################################
from odoo import models, fields

from odoo import models, fields

from odoo import api, fields, models, _
from odoo.tools import float_round
from xmlrpc.client import dumps, loads
import xmlrpc.client
import logging
import ssl
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class HrJob(models.Model):
    _inherit = 'hr.job'

    erp_id = fields.Integer()
    active = fields.Boolean(default=True)

    def _sync_hr_job(self):
        url = "https://baocao.scigroup.com.vn"
        db = '2022_11_24_05_00_01'
        username = 'hungtn@scigroup.com.vn'
        password = '123@123'

        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url), verbose=False, use_datetime=True, context=ssl._create_unverified_context())

        # Login
        uid = common.authenticate(db, username, password, {})

        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url), verbose=False, use_datetime=True, context=ssl._create_unverified_context())

        hr_jobs = models.execute_kw(db, uid, password,
                                    'hr.job', 'search_read',
                                    [[['name', '!=', False],
                                      ['active', '=', True]]],
                                    {'fields': ['id', 'name', 'department_id', 'company_id']})

        # department = self.env['hr.department']
        # company = self.env['res.company']

        # Dict vị trí công việc
        companies = self.get_companies()

        departments = self.get_departments()
        jobs = self.get_jobs()

        for info in hr_jobs:
            print(info)
            company = info['company_id'][0] if info['company_id'] else False
            company_id = companies.get(company)
            if not company_id:
                _logger.error("Vui lòng đồng bộ 1.HR: Đồng công ty")
                raise UserError("Vui lòng đồng bộ 1.HR: Đồng công ty")

            department = info['department_id'][0] if info['department_id'] else False
            department_id = departments.get(department)
            print(department_id)
            if not department_id:
                print(info)
                _logger.error("Vui lòng đồng bộ 2.HR: Đồng bộ phòng ban %s" % info['id'])
                raise UserError("Vui lòng đồng bộ 2.HR: Đồng bộ phòng ban %s" % info['name'])

            if info['id'] in jobs:
                # update lại từ hệ thống ERP
                # print('update lại từ hệ thống ERP')
                # print(info['id'])
                record = jobs[info['id']]
                record.sudo().write({
                    'name': info['name'],
                    'department_id': department_id.id,
                    'company_id': company_id.id,
                    # 'erp_id': info['id'],-
                })
            else:
                # Thêm mới
                val = {
                    'name': info['name'],
                    'department_id': department_id.id,
                    'company_id': company_id.id,
                    'erp_id': info['id'],
                }
                print(val)
                rec = self.env['hr.job'].create({
                    'name': info['name'],
                    'department_id': department_id.id,
                    'company_id': company_id.id,
                    'erp_id': info['id'],
                })
                _logger.info('Create job: %s tại chi nhánh: %s', rec.name, rec.company_id.name)
        _logger.info('Đồng bộ vị trí công việc thành công.')

    def get_companies(self):
        companies = self.env['res.company'].search([])
        return dict((company.erp_id, company) for company in companies)

    def get_departments(self):
        departments = self.env['hr.department'].search([])
        return dict((department.erp_id, department) for department in departments)

    def get_jobs(self):
        jobs = self.env['hr.job'].search([])
        return dict((job.erp_id, job) for job in jobs)
