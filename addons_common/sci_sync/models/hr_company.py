# -*- coding: utf-8 -*- 
###################################################################################
from odoo import models, fields

from odoo import api, fields, models, _
from odoo.tools import float_round
from xmlrpc.client import dumps, loads
import xmlrpc.client
import ssl

import logging

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    active = fields.Boolean('Active', default=True)
    erp_id = fields.Integer(string='ERP Company ID')

    def _sync_res_company(self):
        url = "https://erp.scigroup.com.vn"
        db = 'sci_erp'
        username = 'toannh@scigroup.com.vn'
        password = '123@123'

        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url), verbose=False, use_datetime=True, context=ssl._create_unverified_context())

        # Login
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url), verbose=False, use_datetime=True, context=ssl._create_unverified_context())

        res_companies = models.execute_kw(db, uid, password,
                                      'res.company', 'search_read',
                                      [[['active', '=', True]]],
                                      {'fields': ['id', 'name', 'code', 'active']})

        companies, company_names, company_codes = self.get_companies()

        for company in res_companies:
            if company['code'] in company_codes:
                record = company_codes[company['code']]
                print(record)
                record.sudo().write({
                    'id': company['id'],
                    'name': company['name'],
                    'active': company['active'],
                    'erp_id': company['id'],
                })
            else:
                if company['name'] in company_names:
                    record = company_names[company['name']]
                    record.sudo().write({
                        'id': company['id'],
                        'code': company['code'],
                        'active': company['active'],
                        'erp_id': company['id'],
                    })
                else:
                    # Thêm mới
                    rec = self.env['res.company'].create({
                        'code': company['code'],
                        'name': company['name'],
                        'active': company['active'],
                        'erp_id': company['id'],
                    })
                    _logger.info('Create company %s thành công.' % rec.name)
        # records = self.env['res.company'].search(['|', ('name', '=', company['name']), ('erp_id', '=', company['id'])])
        # if records:
        #     record = records[0]
        #     record.write({
        #         'code': company['code'],
        #         'name': company['name'],
        #         'active': company['active'],
        #         'erp_id': company['id'],
        #     })
        #     _logger.info('Update company %s thành công.' % company['name'])
        # else:


        # for company in res_companies:
        #     if company['id'] in companies:
        #         record = companies[company['id']]
        #         record.sudo().write({
        #             'code': company['code'],
        #             'name': company['name'],
        #             'active': company['active'],
        #         })
        #     else:
        #         if company['code'] in company_codes:
        #             print('update code')
        #             record = company_codes[company['code']]
        #             record.sudo().write({
        #                 'id': company['id'],
        #                 'name': company['name'],
        #                 'active': company['active'],
        #                 'erp_id': company['id'],
        #             })
        #         else:
        #             if company['name'] in company_names:
        #                 print('update name')
        #                 record = company_names[company['name']]
        #                 record.sudo().write({
        #                     'id': company['id'],
        #                     'code': company['code'],
        #                     'active': company['active'],
        #                     'erp_id': company['id'],
        #                 })
        #             else:
        #                 # Thêm mới
        #                 rec = self.env['res.company'].create({
        #                     'code': company['code'],
        #                     'name': company['name'],
        #                     'active': company['active'],
        #                     'erp_id': company['id'],
        #                 })
        #                 _logger.info('Create company %s thành công.' % rec.name)
        #     # records = self.env['res.company'].search(['|', ('name', '=', company['name']), ('erp_id', '=', company['id'])])
        #     # if records:
        #     #     record = records[0]
        #     #     record.write({
        #     #         'code': company['code'],
        #     #         'name': company['name'],
        #     #         'active': company['active'],
        #     #         'erp_id': company['id'],
        #     #     })
        #     #     _logger.info('Update company %s thành công.' % company['name'])
        #     # else:

        _logger.info('Sync company %s thành công.')

    def get_companies(self):
        companies = self.env['res.company'].search([])
        company_erp_ids = dict((company.erp_id, company) for company in companies)
        company_names = dict((company.name, company) for company in companies)
        company_codes = dict((company.code, company) for company in companies)
        return company_erp_ids, company_names, company_codes
