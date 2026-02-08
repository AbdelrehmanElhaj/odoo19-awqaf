# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class WaqfApplicationApproval(models.Model):
    _name = 'waqf.application.approval'
    _description = 'موافقة على طلب الدعم'
    _order = 'create_date desc'
    
    application_id = fields.Many2one(
        'waqf.support.application',
        string='الطلب',
        required=True,
        ondelete='cascade',
        index=True
    )
    
    decision = fields.Selection([
        ('approved', 'موافقة'),
        ('rejected', 'رفض'),
        ('pending', 'قيد المراجعة'),
    ], string='القرار', required=True, default='pending')
    
    approved_by = fields.Many2one(
        'res.users',
        string='تمت الموافقة بواسطة',
        required=True,
        default=lambda self: self.env.user
    )
    
    approval_date = fields.Datetime(
        string='تاريخ القرار',
        default=fields.Datetime.now,
        required=True
    )
    
    notes = fields.Text(string='ملاحظات')
    
    company_id = fields.Many2one(
        related='application_id.company_id',
        store=True,
        index=True
    )