# # -*- coding: utf-8 -*-
# # Depreciated
# # Part of Odoo. See LICENSE file for full copyright and licensing details.
#
# #
# # Order Point Method:
# #    - Order if the virtual stock of today is below the min of the defined order point
# #
#
# from odoo import api, models, tools
#
# import logging
# import threading
#
# _logger = logging.getLogger(__name__)
#
#
# class SCIStockSchedulerCompute(models.TransientModel):
#     _inherit = 'stock.scheduler.compute'
#
#     def _procure_calculation_orderpoint(self):
#         with api.Environment.manage():
#             # As this function is in a new thread, I need to open a new cursor, because the old one may be closed
#             new_cr = self.pool.cursor()
#             self = self.with_env(self.env(cr=new_cr))
#             scheduler_cron = self.sudo().env.ref('stock.ir_cron_scheduler_action')
#             # Avoid to run the scheduler multiple times in the same time
#             try:
#                 with tools.mute_logger('odoo.sql_db'):
#                     self._cr.execute("SELECT id FROM ir_cron WHERE id = %s FOR UPDATE NOWAIT", (scheduler_cron.id,))
#             except Exception:
#                 _logger.info('Attempt to run procurement scheduler aborted, as already running')
#                 self._cr.rollback()
#                 self._cr.close()
#                 return {}
#
#             for company in self.env.user.company_ids:
#                 self.env['procurement.group'].with_context(compute_child=False, exact_location=True, separate_pick=True, do_not_confirm=True).run_scheduler(
#                     use_new_cursor=self._cr.dbname,
#                     company_id=company.id)
#             new_cr.close()
#             return {}
#
