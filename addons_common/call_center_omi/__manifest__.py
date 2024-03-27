# -*- coding: utf-8 -*-

{
    "name": "Addon intergate call center OMI",
    "summary": "Tích hợp tổng đài OMI với CRM",
    "version": "13.0.0.1",
    "category": "CRM",
    "website": "https://omicall.com/",
	"description": """
		Tích hợp tổng đài OMI cho phép gọi điện cho khách hàng
    """,
	'images':[
        'images/screen.png'
	],
    "author": "thond",
    "license": "LGPL-3",
    "installable": True,
    'application': True,
    "depends": [
        'web',
    ],
    "data": [
        'views/assets.xml',
    ],
}

