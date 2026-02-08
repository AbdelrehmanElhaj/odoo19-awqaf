# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class WaqfPolicyDatasetRow(models.Model):
    _name = 'waqf.policy.dataset.row'
    _description = 'صف بيانات السياسة'
    _order = 'dataset_id, study_level, city_mode'
    
    dataset_id = fields.Many2one(
        'waqf.policy.dataset',
        string='مجموعة البيانات',
        required=True,
        ondelete='cascade',
        index=True
    )
    
    study_level = fields.Selection([
        ('diploma', 'دبلوم'),
        ('bachelor_theory', 'بكالوريوس نظري'),
        ('bachelor_science', 'بكالوريوس علمي'),
        ('master_theory', 'ماجستير نظري'),
        ('master_science', 'ماجستير علمي'),
    ], string='المستوى الدراسي', required=True, index=True)
    
    city_mode = fields.Selection([
        ('inside_city', 'داخل المدينة'),
        ('outside_city', 'خارج المدينة'),
    ], string='وضع السكن', required=True, index=True)
    
    cap_education_fee = fields.Float(
        string='الحد الأعلى للرسوم الدراسية',
        digits=(16, 2),
        required=True
    )
    
    cap_monthly_stipend = fields.Float(
        string='الحد الأعلى للمكافأة الشهرية',
        digits=(16, 2),
        required=True
    )
    
    notes = fields.Text(string='ملاحظات')
    
    active = fields.Boolean(default=True)
    
    company_id = fields.Many2one(
        related='dataset_id.company_id',
        store=True,
        index=True
    )
    
    _sql_constraints = [
        ('unique_policy_row', 
         'UNIQUE(dataset_id, study_level, city_mode)', 
         'يوجد صف مماثل بنفس المعايير في نفس المجموعة!'),
    ]
    
    @api.constrains('cap_education_fee', 'cap_monthly_stipend')
    def _check_caps(self):
        for rec in self:
            if rec.cap_education_fee < 0:
                raise ValidationError(_('الحد الأعلى للرسوم لا يمكن أن يكون سالباً'))
            if rec.cap_monthly_stipend < 0:
                raise ValidationError(_('الحد الأعلى للمكافأة لا يمكن أن يكون سالباً'))
    
    def name_get(self):
        result = []
        for rec in self:
            name = f"{dict(rec._fields['study_level'].selection).get(rec.study_level)} - {dict(rec._fields['city_mode'].selection).get(rec.city_mode)}"
            result.append((rec.id, name))
        return result