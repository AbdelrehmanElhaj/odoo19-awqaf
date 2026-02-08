# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class WaqfDisbursement(models.Model):
    _name = 'waqf.disbursement'
    _description = 'عملية صرف'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'disbursement_date desc, id desc'
    
    name = fields.Char(
        string='رقم العملية',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _('New')
    )
    
    application_id = fields.Many2one(
        'waqf.support.application',
        string='الطلب',
        required=True,
        index=True,
        tracking=True
    )
    
    beneficiary_id = fields.Many2one(
        'waqf.beneficiary',
        string='المستفيد',
        required=True,
        index=True,
        tracking=True
    )
    
    amount = fields.Float(
        string='المبلغ',
        required=True,
        digits=(16, 2),
        tracking=True
    )
    
    disbursement_date = fields.Date(
        string='تاريخ الصرف',
        required=True,
        default=fields.Date.today,
        tracking=True
    )
    
    state = fields.Selection([
        ('draft', 'مسودة'),
        ('confirmed', 'مؤكد'),
        ('paid', 'مدفوع'),
        ('cancelled', 'ملغي'),
    ], string='الحالة', default='draft', tracking=True)
    
    payment_method = fields.Selection([
        ('bank_transfer', 'تحويل بنكي'),
        ('cash', 'نقدي'),
        ('check', 'شيك'),
    ], string='طريقة الدفع', tracking=True)
    
    reference = fields.Char(string='المرجع', tracking=True)
    
    notes = fields.Text(string='ملاحظات')
    
    company_id = fields.Many2one(
        'res.company',
        string='الشركة',
        required=True,
        default=lambda self: self.env.company
    )
    
    disbursed_by = fields.Many2one('res.users', string='صرف بواسطة', readonly=True)
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'waqf.disbursement'
            ) or _('New')
        
        if vals.get('state') == 'confirmed' and not vals.get('disbursed_by'):
            vals['disbursed_by'] = self.env.user.id
            
        return super(WaqfDisbursement, self).create(vals)
    
    @api.constrains('amount')
    def _check_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError(_('المبلغ يجب أن يكون أكبر من صفر'))
    
    def action_confirm(self):
        self.write({
            'state': 'confirmed',
            'disbursed_by': self.env.user.id
        })
        self.message_post(body=_('تم تأكيد عملية الصرف'))
    
    def action_mark_paid(self):
        self.write({'state': 'paid'})
        self.message_post(body=_('تم تحديد العملية كمدفوعة'))
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})
        self.message_post(body=_('تم إلغاء عملية الصرف'))