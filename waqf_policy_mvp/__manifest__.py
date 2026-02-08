# -*- coding: utf-8 -*-
{
    'name': 'Waqf Policy Engine (MVP)',
    'version': '19.0.1.0.0',
    'category': 'Waqf Management',
    'summary': 'محرك السياسات للوقف',
    'description': """
        محرك السياسات للوقف
        ===================
        * إدارة مجموعات بيانات السياسات
        * تطبيق الحدود القصوى للرسوم والمكافآت
        * سياسات الدعم التعليمي
    """,
    'author': 'Waqf Development Team',
    'website': 'https://www.waqf.local',
    'license': 'OEEL-1',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/waqf_policy_dataset_views.xml',
        'views/waqf_policy_menu.xml',
        'data/demo_policy_data.xml',
    ],
    'demo': [
        'data/demo_policy_data.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}