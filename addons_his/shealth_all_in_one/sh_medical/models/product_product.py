##############################################################################
#    Copyright (C) 2016 sHealth (<http://scigroup.com.vn/>). All Rights Reserved
#    sHealth, Hospital Management Solutions
##############################################################################

from odoo import api, fields, models, _


class sHealthProduct(models.Model):
    _inherit = 'product.template'

    is_medicine = fields.Boolean(string='Medicine', help='Check if the product is a medicine')
    is_bed = fields.Boolean(string='Bed', help='Check if the product is a bed')
    is_vaccine = fields.Boolean(string='Vaccine', help='Check if the product is a vaccine')
    is_medical_supply = fields.Boolean(string='Medical Supply', help='Check if the product is a medical supply')
    is_insurance_plan = fields.Boolean(string='Insurance Plan', help='Check if the product is an insurance plan')

    _sql_constraints = [
        ('unique_product_default_code', 'unique (default_code)', 'Mã nội bộ phải là duy nhất!')
    ]
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
