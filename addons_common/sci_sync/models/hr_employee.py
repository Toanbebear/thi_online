# -*- coding: utf-8 -*- 
###################################################################################
from odoo import models, fields
from datetime import datetime
from dateutil import relativedelta
from odoo import api, fields, models, _
from odoo.tools import float_round
from xmlrpc.client import dumps, loads
from odoo.exceptions import UserError
import calendar
from datetime import date

import numpy as np
from dateutil import relativedelta
import xmlrpc.client
import logging
import ssl

_logger = logging.getLogger(__name__)


# email_archive = ['lybm@scigroup.com.vn', 'luongnth@scigroup.com.vn', 'phuongntm@scigroup.com.vn',
#                  'huongptt1@scigroup.com.vn', 'phuongtn@scigroup.com.vn', 'hangnplm@scigroup.com.vn',
#                  'hoangth@scigroup.com.vn', 'yennth@kangnam.com.vn', 'hoangnd@scigroup.com.vn',
#                  'xuanttt@scigroup.com.vn', 'thaovtt@kangnam.com.vn', 'thaoptt@scigroup.com.vn',
#                  'huykq@scigroup.com.vn', 'chungdt@scigroup.com.vn', 'lenth@dongabeauty.vn', 'thoanht@scigroup.com.vn',
#                  'nghiatt@scigroup.com.vn', 'kimhth@scigroup.com.vn',
#                  'anhlt@scigroup.com.vn', 'anhdn@scigroup.com.vn', 'nhungpt@scigroup.com.vn', 'liennt@dongabeauty.vn',
#                  'yenpth@nhakhoaparis.vn', 'anhptp@dongabeauty.vn',
#                  'thanhbt@scigroup.com.vn', 'dungntp@scigroup.com.vn']


# class HrEmployeePublic(models.Model):
#     _inherit = 'hr.employee.public'
#
#     joining_date = fields.Date(string='Ngày vào làm')
#     resign_date = fields.Date('Ngày từ chức', readonly=True)
#     erp_id = fields.Integer()


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # Đồng bộ bộ phận nhân viên
    def _sync_hr_employee_job(self):
        url = "https://erp.scigroup.com.vn"
        db = 'sci_erp'
        username = 'toannh@scigroup.com.vn'
        password = '123@123'

        _logger.info('%s %s %s %s' % (url, db, username, password))
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url), verbose=False, use_datetime=True,
                                           context=ssl._create_unverified_context())
        # Login
        uid = common.authenticate(db, username, password, {})
        _logger.info('Login thành công')

        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url), verbose=False, use_datetime=True,
                                           context=ssl._create_unverified_context())

        info_employees = models.execute_kw(db, uid, password, 'hr.employee', 'search_read',
                                           [[['work_email', '!=', False], ['active', '=', True]]], {
                                               'fields': ['id', 'name', 'employee_code', 'work_email',
                                                          'company_id', 'active', 'group_job', 'gender', 'birthday'
                                                          ]})
        jobs = self.get_group_jobs()
        employees, work_emails, codes, employee_ids = self.get_employees()
        for info in info_employees:
            job = info['group_job'][0] if info['group_job'] else False
            job_id = jobs.get(job)
            if job_id:
                if info['work_email'] in work_emails:
                    print('work_email update lại từ hệ thống ERP và cập nhật lại erp_id')
                    record = work_emails[info['work_email']]
                    record.sudo().write({
                        'gender': info['gender'],
                        'birthday': info['birthday'],
                        'group_job': job_id.id,
                    })
            else:
                if info['work_email'] in work_emails:
                    print('work_email update lại từ hệ thống ERP và cập nhật lại erp_id')
                    record = work_emails[info['work_email']]
                    record.sudo().write({
                        'gender': info['gender'],
                        'birthday': info['birthday'],
                    })
        _logger.info('Đồng bộ nhân viên thành công')

    # Đồng bộ nhân viên mới, 30p 1 lần
    def _sync_hr_employee(self):
        hr_employee = self.env['hr.employee']
        # Lấy erp_id lớn nhất
        self.env.cr.execute("select max(erp_id) from hr_employee")
        erp_id = self.env.cr.fetchone()[0]

        url = "https://baocao.scigroup.com.vn"
        db = 'sci_erp'
        username = 'toannh@scigroup.com.vn'
        password = '123@123'

        _logger.info('%s %s %s %s' % (url, db, username, password))
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url), verbose=False, use_datetime=True,
                                           context=ssl._create_unverified_context())
        # Login
        uid = common.authenticate(db, username, password, {})
        _logger.info('Login thành công')

        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url), verbose=False, use_datetime=True,
                                           context=ssl._create_unverified_context())

        info_employees = models.execute_kw(db, uid, password, 'hr.employee', 'search_read',
                                           [[['work_email', '!=', False], ['active', '=', True]]], {
                                               'fields': ['id', 'name', 'employee_code', 'work_email',
                                                          'company_id',
                                                          'user_id', 'active', 'department_id', 'job_id',
                                                          'joining_date', 'resign_date'
                                                          ]})
        # Dict vị trí công việc
        companies = self.get_companies()
        users = self.get_users()
        employees, work_emails, codes, employee_ids = self.get_employees()
        query = ''
        for info in info_employees:
                if info['work_email'] in work_emails:
                    print('work_email update lại từ hệ thống ERP và cập nhật lại erp_id')
                    record = work_emails[info['work_email']]
                    record.sudo().write({
                        'erp_id': info['id'],
                    })
                else:
                    if info['employee_code'] in codes:
                        print('employee_code update lại từ hệ thống ERP và cập nhật lại erp_id')
                        record = codes[info['employee_code']]
                        record.sudo().write({
                            'erp_id': info['id'],
                        })
                    else:
                        print('Thêm người dùng mới')
                        # Thêm mới
                        company = info['company_id'][0] if info['company_id'] else False
                        company_id = companies.get(company)
                        if not company_id:
                            _logger.error("Vui lòng đồng bộ 1.HR: Đồng công ty")
                            raise UserError("Vui lòng đồng bộ 1.HR: Đồng công ty")
                        vals = {
                            # 'employee_id': info['employee_id'],
                            'employee_code': info['employee_code'],
                            'name': info['name'],
                            'work_email': info['work_email'],
                            'company_id': company_id.id,
                            'department_id': False,
                            'job_id': False,
                            'active': info['active'],
                            'erp_id': info['id'],
                            'joining_date': info['joining_date'],
                            'resign_date': info['resign_date']
                        }
                        rec = hr_employee.sudo().create(vals)
                        _logger.info('Create employee thành công: %s', rec.name)
                        # Kiểm tra xem có user chưa?
                        if info['work_email'] in users:
                            user = users[info['work_email']]
                            user.sudo().write(
                                {
                                    'employee': True,
                                    'employee_ids': [(6, 0, [rec.id])],
                                }
                            )
                        else:
                            # Tạo user
                            # Tạo người tài khoản người dùng
                            user_vals = {
                                'login': info['work_email'],
                                'password': '1',
                                'name': info['name'],
                                'company_id': rec.company_id.id,
                            }
                            uid = self.env['res.users'].sudo().with_context(allowed_company_ids=[rec.company_id.id]).create(user_vals)
                            _logger.info('Create user: %s thành công, email: %s', uid.name, uid.login)

        _logger.info('Đồng bộ nhân viên thành công')

        # list_employees = self.env['hr.employee'].search([('user_id', '=', False), ('work_email', '!=', False)])
        # for emp in list_employees:
        #     if emp.work_email in users:
        #         print('tồn tại user hay không', emp.work_email)
        #     else:
        #         print(emp.work_email)
        #         user_vals = {
        #             'login': emp.work_email,
        #             'password': '1',
        #             'name': emp.name,
        #             'company_id': emp.company_id.id,
        #         }
        #         uid = self.env['res.users'].sudo().with_context(allowed_company_ids=[emp.company_id.id]).create(user_vals)
        #         _logger.info('Create user: %s thành công, email: %s', uid.name, uid.login)

        _logger.info(query)
        self.env.cr.execute("""update hr_employee set user_id = res_users.id
                                from res_users
                                where res_users.login = hr_employee.work_email
                                and hr_employee.user_id is null""")

    def get_companies(self):
        companies = self.env['res.company'].search([])
        return dict((company.erp_id, company) for company in companies)

    def get_departments(self):
        departments = self.env['hr.department'].search([])
        return dict((department.erp_id, department) for department in departments)

    def get_jobs(self):
        jobs = self.env['hr.job'].search([])
        return dict((job.erp_id, job) for job in jobs)

    def get_employees(self):
        employees = self.env['hr.employee'].search([])
        result = dict((employee.erp_id, employee) for employee in employees)
        work_emails = dict((employee.work_email, employee) for employee in employees)
        codes = dict((employee.employee_code, employee) for employee in employees)
        employee_ids = dict((employee.employee_id, employee) for employee in employees)
        return result, work_emails, codes, employee_ids

    def get_users(self):
        users = self.env['res.users'].sudo().search([])
        return dict((user.login, user) for user in users)

    def get_group_jobs(self):
        jobs = self.env['hr.group.job'].search([])
        return dict((job.erp_id, job) for job in jobs)

class InheritGroupJob(models.Model):
    _inherit = 'hr.group.job'

    active = fields.Boolean('Active', default=True)
    erp_id = fields.Integer()

    def _sync_res_group_job(self):
        url = "https://baocao.scigroup.com.vn"
        db = '2022_12_27_05_00_01'
        username = 'hungtn@scigroup.com.vn'
        password = '123@123'

        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url), verbose=False, use_datetime=True, context=ssl._create_unverified_context())

        # Login
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url), verbose=False, use_datetime=True, context=ssl._create_unverified_context())

        res_job = models.execute_kw(db, uid, password,
                                      'hr.group.job', 'search_read',
                                      [[['name', '!=', True]]],
                                      {'fields': ['id', 'name']})

        companies, job_erp_name = self.get_companies()

        for job in res_job:
            if job['id'] in companies:
                record = companies[job['id']]
                record.sudo().write({
                    'name': job['name'],
                })
            else:
                if job['name'] in job_erp_name:
                    record = job_erp_name[job['name']]
                    record.sudo().write({
                        'id': job['id'],
                        'erp_id': job['id'],
                        'name': job['name'],
                    })
                else:
                    rec = self.env['hr.group.job'].create({
                        'name': job['name'],
                        'erp_id': job['id'],
                    })
                    _logger.info('Create Bộ phận %s thành công.' % rec.name)

        _logger.info('Sync company %s thành công.')

    def get_companies(self):
        companies = self.env['hr.group.job'].search([])
        job_erp_ids = dict((job.erp_id, job) for job in companies)
        job_erp_name = dict((job.name, job) for job in companies)
        return job_erp_ids, job_erp_name

