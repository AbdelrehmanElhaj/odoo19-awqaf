# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class WaqfPolicyDataset(models.Model):
    _name = 'waqf.policy.dataset'
    _description = 'مجموعة بيانات السياسة'
    _order = 'name'
    
    name = fields.Char(string='اسم المجموعة', required=True, index=True)
    code = fields.Char(string='الرمز', required=True, index=True)
    description = fields.Text(string='الوصف')
    
    policy_type = fields.Selection([
        ('education', 'سياسة الدعم التعليمي'),
        ('medical', 'سياسة الدعم الطبي'),
        ('housing', 'سياسة الدعم السكني'),
    ], string='نوع السياسة', required=True, default='education')
    
    row_ids = fields.One2many(
        'waqf.policy.dataset.row',
        'dataset_id',
        string='صفوف البيانات'
    )
    
    row_count = fields.Integer(
        string='عدد الصفوف',
        compute='_compute_row_count'
    )
    
    active = fields.Boolean(default=True)
    is_default = fields.Boolean(string='افتراضي', default=False)
    
    company_id = fields.Many2one(
        'res.company',
        string='الشركة',
        default=lambda self: self.env.company
    )
    
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code, company_id)', 
         'رمز المجموعة يجب أن يكون فريداً!'),
    ]
    
    @api.depends('row_ids')
    def _compute_row_count(self):
        for rec in self:
            rec.row_count = len(rec.row_ids)
    
    def get_policy_row(self, study_level, city_mode, marital_status=None):
        """Get matching policy row based on criteria"""
        self.ensure_one()
        
        domain = [
            ('dataset_id', '=', self.id),
            ('study_level', '=', study_level),
            ('city_mode', '=', city_mode),
        ]
        
        row = self.env['waqf.policy.dataset.row'].search(domain, limit=1)
        return row