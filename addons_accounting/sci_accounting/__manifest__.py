# -*- coding: utf-8 -*-

{
    'name': 'SCI Accounting',
    'version': '13.0.1.0.0',
    'summary': """Customized accounting for HIS.""",
    'description': '',
    'category': 'Accounting',
    'author': 'Nomed',
    'company': 'SCI Group',
    'website': "https://scigroup.com.vn",
    'depends': ['stock_intercompany_transfer', 'account_standard_report', 'stock_account'],
    'data': ['views/stock_valuation_layer_views.xml',
             'views/account_move_line_view.xml'
    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'post_init_hook': 'post_init',
    'application': True,
}
