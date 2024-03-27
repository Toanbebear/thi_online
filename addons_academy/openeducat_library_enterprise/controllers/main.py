# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

import calendar
from datetime import date

from odoo import http
from odoo.http import request


class OpenEduCatLibraryController(http.Controller):

    @http.route('/openeducat_library_enterprise/get_library_dashboard_data',
                type='json', auth='user')
    def compute_library_dashboard_data(self):
        dbt = 0
        dbm = 0
        tpat = 0

        media = request.env['ir.model'].search(
            [('model', '=', 'op.media')])
        if media:
            last_day = date.today().replace(
                day=calendar.monthrange(date.today().year,
                                        date.today().month)[1])
            dbt = request.env['op.media.movement'].search_count(
                [('state', '=', 'issue'), ('return_date', '=', date.today())])
            dbm = request.env['op.media.movement'].search_count([
                ('state', '=', 'issue'),
                ('return_date', '>=', date.today().strftime('%Y-%m-01')),
                ('return_date', '<=', last_day)])
            movements_ids = request.env['op.media.movement'].search(
                [('state', '=', 'return'),
                 ('return_date', '>=', date.today().strftime('%Y-%m-01')),
                 ('return_date', '<=', last_day)])
            for movement in movements_ids:
                tpat += movement.penalty
        return {'dbt': dbt, 'dbm': dbm, 'tpat': tpat}
