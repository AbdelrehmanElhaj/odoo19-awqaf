# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class WaqfApplicationLine(models.Model):
    _name = 'waqf.application.line'
    _description = 'بند طلب الدعم'
    _order = 'application_id, sequence, id'
    
    sequence = fields.Integer(string='التسلسل', default=10)
    
    application_id = fields.Many2one(
        'waqf.support.application',
        string='الطلب',
        required=True,
        ondelete='cascade',
        index=True
    )
    
    line_type = fields.Selection([
        ('education_fee', 'رسوم دراسية'),
        ('monthly_stipend', 'مكافأة شهرية'),
    ], string='نوع البند', required=True)
    
    requested_amount = fields.Float(
        string='المبلغ المطلوب',
        required=True,
        digits=(16, 2)
    )
    
    eligible_amount = fields.Float(
        string='المبلغ المستحق',
        digits=(16, 2),
        readonly=True,
        help='يتم حسابه تلقائياً بناءً على السياسة'
    )
    
    # Meta fields for policy matching
    study_level = fields.Selection([
        ('diploma', 'دبلوم'),
        ('bachelor_theory', 'بكالوريوس نظري'),
        ('bachelor_science', 'بكالوريوس علمي'),
        ('master_theory', 'ماجستير نظري'),
        ('master_science', 'ماجستير علمي'),
    ], string='المستوى الدراسي', required=True)
    
    city_mode = fields.Selection([
        ('inside_city', 'داخل المدينة'),
        ('outside_city', 'خارج المدينة'),
    ], string='وضع السكن', required=True)
    
    notes = fields.Text(string='ملاحظات')
    
    company_id = fields.Many2one(
        related='application_id.company_id',
        store=True,
        index=True
    )
    
    @api.constrains('requested_amount')
    def _check_requested_amount(self):
        for rec in self:
            if rec.requested_amount <= 0:
                raise ValidationError(_('المبلغ المطلوب يجب أن يكون أكبر من صفر'))
    
    def name_get(self):
        result = []
        for rec in self:
            name = f"{dict(rec._fields['line_type'].selection).get(rec.line_type)} - {rec.requested_amount}"
            result.append((rec.id, name))
        return result