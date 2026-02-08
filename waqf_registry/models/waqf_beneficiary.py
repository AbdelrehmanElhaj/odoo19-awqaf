# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class WaqfBeneficiary(models.Model):
    _name = 'waqf.beneficiary'
    _description = 'مستفيد من الوقف'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='الاسم الكامل',
        required=True,
        tracking=True,
        translate=True
    )
    
    beneficiary_code = fields.Char(
        string='رقم المستفيد',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _('New')
    )
    
    national_id = fields.Char(
        string='رقم الهوية الوطنية',
        required=True,
        tracking=True,
        index=True
    )
    
    category = fields.Selection([
        ('dhurri', 'ذري'),
        ('public', 'عام')
    ], string='الفئة', required=True, default='public', tracking=True)
    
    phone = fields.Char(string='رقم الجوال', required=True, tracking=True)
    email = fields.Char(string='البريد الإلكتروني', tracking=True)
    
    social_status = fields.Selection([
        ('single', 'أعزب'),
        ('married', 'متزوج'),
        ('divorced', 'مطلق'),
        ('widowed', 'أرمل')
    ], string='الحالة الاجتماعية', tracking=True)
    
    dependents_count = fields.Integer(string='عدد المعالين', default=0, tracking=True)
    
    residence_city = fields.Char(string='مدينة الإقامة', tracking=True)
    
    # Bank Details
    bank_name = fields.Char(string='اسم البنك', tracking=True)
    iban = fields.Char(string='رقم الآيبان', tracking=True)
    account_no = fields.Char(string='رقم الحساب', tracking=True)
    account_holder = fields.Char(string='اسم صاحب الحساب', tracking=True)
    
    # Pledge
    pledge_accepted = fields.Boolean(
        string='قبول التعهد',
        required=True,
        default=False,
        tracking=True
    )
    pledge_date = fields.Datetime(
        string='تاريخ التعهد',
        readonly=True,
        tracking=True
    )
    
    # Documents
    document_ids = fields.One2many(
        'waqf.beneficiary.document',
        'beneficiary_id',
        string='المرفقات'
    )
    
    document_count = fields.Integer(
        string='عدد المرفقات',
        compute='_compute_document_count'
    )
    
    # Status
    state = fields.Selection([
        ('draft', 'مسودة'),
        ('submitted', 'مقدم'),
        ('verified', 'مراجع'),
        ('active', 'نشط'),
        ('inactive', 'غير نشط')
    ], string='الحالة', default='draft', tracking=True)
    
    # Multi-company
    company_id = fields.Many2one(
        'res.company',
        string='الشركة',
        required=True,
        default=lambda self: self.env.company
    )
    
    # User tracking
    submitted_by = fields.Many2one('res.users', string='قدم بواسطة', readonly=True)
    submitted_at = fields.Datetime(string='تاريخ التقديم', readonly=True)
    verified_by = fields.Many2one('res.users', string='راجع بواسطة', readonly=True)
    verified_at = fields.Datetime(string='تاريخ المراجعة', readonly=True)
    
    active = fields.Boolean(default=True)
    
    _sql_constraints = [
        ('national_id_unique', 'UNIQUE(national_id, company_id)', 
         'رقم الهوية الوطنية يجب أن يكون فريداً!'),
    ]
    
    @api.model
    def create(self, vals):
        if vals.get('beneficiary_code', _('New')) == _('New'):
            vals['beneficiary_code'] = self.env['ir.sequence'].next_by_code(
                'waqf.beneficiary'
            ) or _('New')
        
        if vals.get('pledge_accepted') and not vals.get('pledge_date'):
            vals['pledge_date'] = fields.Datetime.now()
        
        return super(WaqfBeneficiary, self).create(vals)
    
    def write(self, vals):
        if vals.get('pledge_accepted') and not self.pledge_date:
            vals['pledge_date'] = fields.Datetime.now()
        return super(WaqfBeneficiary, self).write(vals)
    
    @api.depends('document_ids')
    def _compute_document_count(self):
        for rec in self:
            rec.document_count = len(rec.document_ids)
    
    def action_submit(self):
        self.ensure_one()
        
        if not self.pledge_accepted:
            raise ValidationError(_('يجب قبول التعهد قبل التقديم'))
        
        required_docs = self._get_required_document_types()
        existing_docs = self.document_ids.mapped('document_type')
        
        missing_docs = set(required_docs) - set(existing_docs)
        if missing_docs:
            raise ValidationError(
                _('المرفقات المطلوبة ناقصة: %s') % ', '.join(missing_docs)
            )
        
        self.write({
            'state': 'submitted',
            'submitted_by': self.env.user.id,
            'submitted_at': fields.Datetime.now()
        })
        
        self.message_post(
            body=_('تم تقديم الطلب للمراجعة'),
            subject=_('تقديم طلب مستفيد')
        )
    
    def action_verify(self):
        self.ensure_one()
        self.write({
            'state': 'verified',
            'verified_by': self.env.user.id,
            'verified_at': fields.Datetime.now()
        })
        self.message_post(body=_('تمت مراجعة البيانات والموافقة عليها'))
    
    def action_activate(self):
        self.write({'state': 'active'})
        self.message_post(body=_('تم تفعيل المستفيد'))
    
    def action_deactivate(self):
        self.write({'state': 'inactive'})
        self.message_post(body=_('تم إلغاء تفعيل المستفيد'))
    
    def action_reset_to_draft(self):
        self.write({'state': 'draft'})
    
    def _get_required_document_types(self):
        return ['national_id_copy', 'bank_certificate']
    
    def action_view_documents(self):
        self.ensure_one()
        return {
            'name': _('مرفقات المستفيد'),
            'type': 'ir.actions.act_window',
            'res_model': 'waqf.beneficiary.document',
            'view_mode': 'tree,form',
            'domain': [('beneficiary_id', '=', self.id)],
            'context': {'default_beneficiary_id': self.id}
        }