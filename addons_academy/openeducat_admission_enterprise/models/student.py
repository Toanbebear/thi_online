# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from datetime import datetime
from odoo import models, api


class OpStudentFeesDetails(models.Model):
    _inherit = "op.student.fees.details"

    def _cron_create_invoice(self):
        fees_ids = self.env['op.student.fees.details'].search(
            [('date', '<', datetime.today()), ('invoice_id', '=', False)])
        for fees in fees_ids:
            fees.get_invoice()
