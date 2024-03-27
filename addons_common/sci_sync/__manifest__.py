# -*- coding: utf-8 -*-
{
    'name': 'SCI SYNC',
    'version': '1.0',
    'category': 'SCI Đồng bộ',
    'sequence': 1,
    'description': """
    Đồng bộ dữ liệu từ ERP
    =====================================
    
  
    * Dữ liệu phòng ban
    * Dữ liệu vị trí công việc
    * Dữ liệu nhân viên
    * Dữ liệu người dùng
    
    """,
    'company': 'Tập đoàn SCI Group',
    'website': "scigroup.com.vn",
    'depends': ['hr', 'sci_hrms'],
    'data': [
        'data/ir_cron_data.xml',
    ],
    'demo': [],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}

