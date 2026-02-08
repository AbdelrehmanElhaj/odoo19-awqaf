# -*- coding: utf-8 -*-
{
    'name': 'Waqf Portal (MVP)',
    'version': '19.0.1.0.0',
    'category': 'Waqf Management',
    'summary': 'بوابة المستفيدين',
    'description': """
        بوابة المستفيدين من الوقف
        ==========================
        * تسجيل المستفيدين
        * رفع المرفقات
        * تقديم طلبات الدعم
        * متابعة حالة الطلبات
    """,
    'author': 'Waqf Development Team',
    'website': 'https://www.waqf.local',
    'license': 'OEEL-1',
    'depends': ['portal', 'waqf_support_mvp'],
    'data': [
        'security/ir.model.access.csv',
        'views/portal_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'waqf_portal_mvp/static/src/scss/portal.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}