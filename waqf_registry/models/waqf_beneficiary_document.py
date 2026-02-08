# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class WaqfBeneficiaryDocument(models.Model):
    _name = 'waqf.beneficiary.document'
    _description = 'مرفقات المستفيد'
    _inherit = ['mail.thread']
    _order = 'create_date desc'
    
    name = fields.Char(string='اسم المرفق', required=True)
    
    beneficiary_id = fields.Many2one(
        'waqf.beneficiary',
        string='المستفيد',
        required=True,
        ondelete='cascade',
        index=True
    )
    
    document_type = fields.Selection([
        ('national_id_copy', 'صورة الهوية الوطنية'),
        ('bank_certificate', 'شهادة حساب بنكي'),
        ('family_record', 'صورة سجل الأسرة'),
        ('salary_certificate', 'تعريف راتب'),
        ('student_certificate', 'شهادة طالب'),
        ('medical_report', 'تقرير طبي'),
        ('other', 'أخرى')
    ], string='نوع المرفق', required=True, tracking=True)
    
    attachment_id = fields.Many2one(
        'ir.attachment',
        string='الملف',
        required=True,
        ondelete='cascade'
    )
    
    file_name = fields.Char(related='attachment_id.name', string='اسم الملف')
    file_size = fields.Integer(related='attachment_id.file_size', string='حجم الملف')
    mimetype = fields.Char(related='attachment_id.mimetype', string='نوع الملف')
    
    notes = fields.Text(string='ملاحظات')
    
    company_id = fields.Many2one(
        related='beneficiary_id.company_id',
        store=True,
        index=True
    )
    
    active = fields.Boolean(default=True)