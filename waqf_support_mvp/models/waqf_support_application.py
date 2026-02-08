# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class WaqfSupportApplication(models.Model):
    _name = 'waqf.support.application'
    _description = 'طلب دعم'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    
    name = fields.Char(
        string='رقم الطلب',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _('New')
    )
    
    beneficiary_id = fields.Many2one(
        'waqf.beneficiary',
        string='المستفيد',
        required=True,
        tracking=True,
        domain="[('state', 'in', ['verified', 'active'])]"
    )
    
    support_type = fields.Selection([
        ('education', 'دعم تعليمي'),
    ], string='نوع الدعم', required=True, default='education', tracking=True)
    
    state = fields.Selection([
        ('draft', 'مسودة'),
        ('submitted', 'مقدم'),
        ('verified', 'مراجع'),
        ('in_committee', 'في اللجنة'),
        ('approved', 'موافق عليه'),
        ('rejected', 'مرفوض'),
        ('disbursed', 'تم الصرف'),
        ('closed', 'مغلق'),
    ], string='الحالة', default='draft', required=True, tracking=True)
    
    line_ids = fields.One2many(
        'waqf.application.line',
        'application_id',
        string='بنود الطلب'
    )
    
    approval_ids = fields.One2many(
        'waqf.application.approval',
        'application_id',
        string='الموافقات'
    )
    
    disbursement_ids = fields.One2many(
        'waqf.disbursement',
        'application_id',
        string='عمليات الصرف'
    )
    
    total_requested = fields.Float(
        string='إجمالي المطلوب',
        compute='_compute_totals',
        store=True,
        digits=(16, 2)
    )
    
    total_eligible = fields.Float(
        string='إجمالي المستحق',
        compute='_compute_totals',
        store=True,
        digits=(16, 2)
    )
    
    rejection_reason = fields.Text(string='سبب الرفض', tracking=True)
    
    # Timestamps
    submitted_at = fields.Datetime(string='تاريخ التقديم', readonly=True)
    verified_at = fields.Datetime(string='تاريخ المراجعة', readonly=True)
    approved_at = fields.Datetime(string='تاريخ الموافقة', readonly=True)
    rejected_at = fields.Datetime(string='تاريخ الرفض', readonly=True)
    disbursed_at = fields.Datetime(string='تاريخ الصرف', readonly=True)
    closed_at = fields.Datetime(string='تاريخ الإغلاق', readonly=True)
    
    # User tracking
    submitted_by = fields.Many2one('res.users', string='قدم بواسطة', readonly=True)
    verified_by = fields.Many2one('res.users', string='راجع بواسطة', readonly=True)
    approved_by = fields.Many2one('res.users', string='وافق بواسطة', readonly=True)
    rejected_by = fields.Many2one('res.users', string='رفض بواسطة', readonly=True)
    
    # Policy
    policy_dataset_id = fields.Many2one(
        'waqf.policy.dataset',
        string='مجموعة السياسة المطبقة',
        readonly=True
    )
    
    policy_evaluated = fields.Boolean(string='تم تقييم السياسة', default=False)
    
    company_id = fields.Many2one(
        'res.company',
        string='الشركة',
        required=True,
        default=lambda self: self.env.company
    )
    
    line_count = fields.Integer(compute='_compute_line_count')
    disbursement_count = fields.Integer(compute='_compute_disbursement_count')
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'waqf.support.application'
            ) or _('New')
        return super(WaqfSupportApplication, self).create(vals)
    
    @api.depends('line_ids.requested_amount', 'line_ids.eligible_amount')
    def _compute_totals(self):
        for rec in self:
            rec.total_requested = sum(rec.line_ids.mapped('requested_amount'))
            rec.total_eligible = sum(rec.line_ids.mapped('eligible_amount'))
    
    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.line_ids)
    
    def _compute_disbursement_count(self):
        for rec in self:
            rec.disbursement_count = len(rec.disbursement_ids)
    
    def action_submit(self):
        self.ensure_one()
        
        if not self.line_ids:
            raise ValidationError(_('يجب إضافة بنود للطلب قبل التقديم'))
        
        self.write({
            'state': 'submitted',
            'submitted_by': self.env.user.id,
            'submitted_at': fields.Datetime.now()
        })
        
        self.message_post(
            body=_('تم تقديم الطلب للمراجعة'),
            subject=_('تقديم طلب دعم')
        )
    
    def action_verify(self):
        self.ensure_one()
        
        self.write({
            'state': 'verified',
            'verified_by': self.env.user.id,
            'verified_at': fields.Datetime.now()
        })
        
        self.message_post(body=_('تمت مراجعة الطلب والموافقة على صحته'))
    
    def action_send_to_committee(self):
        self.ensure_one()
        
        if not self.policy_evaluated:
            raise ValidationError(_('يجب تقييم السياسة قبل إرسال الطلب للجنة'))
        
        self.write({'state': 'in_committee'})
        self.message_post(body=_('تم إرسال الطلب إلى اللجنة'))
    
    def action_approve(self):
        self.ensure_one()
        
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id,
            'approved_at': fields.Datetime.now()
        })
        
        # Create approval record
        self.env['waqf.application.approval'].create({
            'application_id': self.id,
            'decision': 'approved',
            'approved_by': self.env.user.id,
            'notes': 'تمت الموافقة على الطلب'
        })
        
        self.message_post(body=_('تمت الموافقة على الطلب'))
    
    def action_reject(self):
        self.ensure_one()
        
        if not self.rejection_reason:
            raise ValidationError(_('يجب إدخال سبب الرفض'))
        
        self.write({
            'state': 'rejected',
            'rejected_by': self.env.user.id,
            'rejected_at': fields.Datetime.now()
        })
        
        # Create approval record
        self.env['waqf.application.approval'].create({
            'application_id': self.id,
            'decision': 'rejected',
            'approved_by': self.env.user.id,
            'notes': self.rejection_reason
        })
        
        self.message_post(body=_('تم رفض الطلب: %s') % self.rejection_reason)
    
    def action_disburse(self):
        self.ensure_one()
        
        if self.total_eligible <= 0:
            raise ValidationError(_('لا يوجد مبلغ مستحق للصرف'))
        
        # Create disbursement record
        disbursement = self.env['waqf.disbursement'].create({
            'application_id': self.id,
            'beneficiary_id': self.beneficiary_id.id,
            'amount': self.total_eligible,
            'disbursement_date': fields.Date.today(),
            'notes': f'صرف طلب {self.name}'
        })
        
        self.write({
            'state': 'disbursed',
            'disbursed_at': fields.Datetime.now()
        })
        
        self.message_post(
            body=_('تم إنشاء عملية صرف بمبلغ %s ريال') % self.total_eligible
        )
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('عملية الصرف'),
            'res_model': 'waqf.disbursement',
            'res_id': disbursement.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_close(self):
        self.ensure_one()
        
        self.write({
            'state': 'closed',
            'closed_at': fields.Datetime.now()
        })
        
        self.message_post(body=_('تم إغلاق الطلب'))
    
    def action_reset_to_draft(self):
        self.write({'state': 'draft'})
    
    def action_evaluate_policy(self):
        """Evaluate policy and update eligible amounts"""
        self.ensure_one()
        
        if not self.line_ids:
            raise ValidationError(_('لا توجد بنود لتقييمها'))
        
        # Get default policy dataset
        dataset = self.env['waqf.policy.dataset'].search([
            ('policy_type', '=', 'education'),
            ('is_default', '=', True),
            ('company_id', '=', self.company_id.id)
        ], limit=1)
        
        if not dataset:
            raise ValidationError(_('لم يتم العثور على مجموعة سياسة افتراضية'))
        
        for line in self.line_ids:
            if line.line_type in ['education_fee', 'monthly_stipend']:
                policy_row = dataset.get_policy_row(
                    line.study_level,
                    line.city_mode
                )
                
                if not policy_row:
                    raise ValidationError(
                        _('لم يتم العثور على سياسة مطابقة للمستوى الدراسي: %s ووضع السكن: %s') 
                        % (line.study_level, line.city_mode)
                    )
                
                if line.line_type == 'education_fee':
                    cap = policy_row.cap_education_fee
                elif line.line_type == 'monthly_stipend':
                    cap = policy_row.cap_monthly_stipend
                else:
                    cap = 0
                
                line.eligible_amount = min(line.requested_amount, cap)
        
        self.write({
            'policy_evaluated': True,
            'policy_dataset_id': dataset.id
        })
        
        self.message_post(
            body=_('تم تقييم السياسة. إجمالي المستحق: %s ريال') % self.total_eligible
        )
    
    def action_view_lines(self):
        self.ensure_one()
        return {
            'name': _('بنود الطلب'),
            'type': 'ir.actions.act_window',
            'res_model': 'waqf.application.line',
            'view_mode': 'tree,form',
            'domain': [('application_id', '=', self.id)],
            'context': {'default_application_id': self.id}
        }
    
    def action_view_disbursements(self):
        self.ensure_one()
        return {
            'name': _('عمليات الصرف'),
            'type': 'ir.actions.act_window',
            'res_model': 'waqf.disbursement',
            'view_mode': 'tree,form',
            'domain': [('application_id', '=', self.id)],
            'context': {'default_application_id': self.id}
        }