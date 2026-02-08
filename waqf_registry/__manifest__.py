# -*- coding: utf-8 -*-
{
    'name': 'Waqf Registry',
    'version': '19.0.1.0.0',
    'category': 'Waqf Management',
    'summary': 'إدارة سجل المستفيدين من الوقف',
    'description': """
        نظام إدارة سجل المستفيدين من الوقف
        =========================================
        * تسجيل المستفيدين الأفراد
        * إدارة المرفقات والوثائق
        * التعهدات والموافقات
        * دعم متعدد الشركات
    """,
    'author': 'Waqf Development Team',
    'website': 'https://www.waqf.local',
    'license': 'OEEL-1',
    'depends': ['base', 'mail'],
    'data': [
        'security/waqf_security.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/waqf_beneficiary_views.xml',
        'views/waqf_menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}