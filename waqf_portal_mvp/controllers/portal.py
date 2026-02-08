# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError


class WaqfPortal(CustomerPortal):
    
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        
        if 'beneficiary_count' in counters:
            values['beneficiary_count'] = request.env['waqf.beneficiary'].search_count([
                ('create_uid', '=', request.env.user.id)
            ]) if request.env['waqf.beneficiary'].check_access_rights('read', raise_exception=False) else 0
        
        if 'application_count' in counters:
            values['application_count'] = request.env['waqf.support.application'].search_count([
                ('create_uid', '=', request.env.user.id)
            ]) if request.env['waqf.support.application'].check_access_rights('read', raise_exception=False) else 0
        
        return values
    
    # Beneficiary routes
    @http.route(['/my/beneficiaries', '/my/beneficiaries/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_beneficiaries(self, page=1, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        
        Beneficiary = request.env['waqf.beneficiary']
        
        domain = [('create_uid', '=', request.env.user.id)]
        
        searchbar_sortings = {
            'date': {'label': _('التاريخ'), 'order': 'create_date desc'},
            'name': {'label': _('الاسم'), 'order': 'name'},
        }
        
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        
        beneficiary_count = Beneficiary.search_count(domain)
        
        pager = portal_pager(
            url="/my/beneficiaries",
            total=beneficiary_count,
            page=page,
            step=self._items_per_page,
            url_args={'sortby': sortby},
        )
        
        beneficiaries = Beneficiary.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager['offset']
        )
        
        values.update({
            'beneficiaries': beneficiaries,
            'page_name': 'beneficiary',
            'pager': pager,
            'default_url': '/my/beneficiaries',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        
        return request.render("waqf_portal_mvp.portal_my_beneficiaries", values)
    
    @http.route(['/my/beneficiary/new'], type='http', auth="user", website=True)
    def portal_beneficiary_new(self, **kw):
        values = {
            'page_name': 'beneficiary_new',
        }
        return request.render("waqf_portal_mvp.portal_beneficiary_form", values)
    
    @http.route(['/my/beneficiary/create'], type='http', auth="user", methods=['POST'], website=True)
    def portal_beneficiary_create(self, **post):
        Beneficiary = request.env['waqf.beneficiary']
        
        vals = {
            'name': post.get('name'),
            'national_id': post.get('national_id'),
            'category': post.get('category', 'public'),
            'phone': post.get('phone'),
            'email': post.get('email'),
            'residence_city': post.get('residence_city'),
            'social_status': post.get('social_status'),
            'dependents_count': int(post.get('dependents_count', 0)),
            'bank_name': post.get('bank_name'),
            'iban': post.get('iban'),
            'account_no': post.get('account_no'),
            'account_holder': post.get('account_holder'),
            'pledge_accepted': bool(post.get('pledge_accepted')),
        }
        
        beneficiary = Beneficiary.create(vals)
        
        return request.redirect('/my/beneficiary/%s' % beneficiary.id)
    
    @http.route(['/my/beneficiary/<int:beneficiary_id>'], type='http', auth="user", website=True)
    def portal_my_beneficiary(self, beneficiary_id, **kw):
        try:
            beneficiary_sudo = self._document_check_access('waqf.beneficiary', beneficiary_id)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        values = {
            'beneficiary': beneficiary_sudo,
            'page_name': 'beneficiary',
        }
        
        return request.render("waqf_portal_mvp.portal_beneficiary_detail", values)
    
    @http.route(['/my/beneficiary/<int:beneficiary_id>/upload'], type='http', auth="user", methods=['POST'], website=True)
    def portal_beneficiary_upload_document(self, beneficiary_id, **post):
        try:
            beneficiary_sudo = self._document_check_access('waqf.beneficiary', beneficiary_id)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        if post.get('document'):
            attachment = request.env['ir.attachment'].create({
                'name': post.get('document').filename,
                'datas': post.get('document').read(),
                'res_model': 'waqf.beneficiary.document',
                'res_id': 0,
            })
            
            request.env['waqf.beneficiary.document'].create({
                'name': post.get('document_name') or post.get('document').filename,
                'beneficiary_id': beneficiary_id,
                'document_type': post.get('document_type'),
                'attachment_id': attachment.id,
                'notes': post.get('notes'),
            })
        
        return request.redirect('/my/beneficiary/%s' % beneficiary_id)
    
    # Application routes
    @http.route(['/my/applications', '/my/applications/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_applications(self, page=1, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        
        Application = request.env['waqf.support.application']
        
        domain = [('create_uid', '=', request.env.user.id)]
        
        searchbar_sortings = {
            'date': {'label': _('التاريخ'), 'order': 'create_date desc'},
            'name': {'label': _('رقم الطلب'), 'order': 'name'},
        }
        
        searchbar_filters = {
            'all': {'label': _('الكل'), 'domain': []},
            'draft': {'label': _('مسودة'), 'domain': [('state', '=', 'draft')]},
            'submitted': {'label': _('مقدم'), 'domain': [('state', '=', 'submitted')]},
            'approved': {'label': _('موافق عليه'), 'domain': [('state', '=', 'approved')]},
            'rejected': {'label': _('مرفوض'), 'domain': [('state', '=', 'rejected')]},
        }
        
        if not sortby:
            sortby = 'date'
        if not filterby:
            filterby = 'all'
        
        order = searchbar_sortings[sortby]['order']
        domain += searchbar_filters[filterby]['domain']
        
        application_count = Application.search_count(domain)
        
        pager = portal_pager(
            url="/my/applications",
            total=application_count,
            page=page,
            step=self._items_per_page,
            url_args={'sortby': sortby, 'filterby': filterby},
        )
        
        applications = Application.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager['offset']
        )
        
        values.update({
            'applications': applications,
            'page_name': 'application',
            'pager': pager,
            'default_url': '/my/applications',
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': searchbar_filters,
            'sortby': sortby,
            'filterby': filterby,
        })
        
        return request.render("waqf_portal_mvp.portal_my_applications", values)
    
    @http.route(['/my/application/new'], type='http', auth="user", website=True)
    def portal_application_new(self, **kw):
        # Get user's beneficiaries
        beneficiaries = request.env['waqf.beneficiary'].search([
            ('create_uid', '=', request.env.user.id),
            ('state', 'in', ['verified', 'active'])
        ])
        
        values = {
            'page_name': 'application_new',
            'beneficiaries': beneficiaries,
        }
        return request.render("waqf_portal_mvp.portal_application_form", values)
    
    @http.route(['/my/application/create'], type='http', auth="user", methods=['POST'], website=True)
    def portal_application_create(self, **post):
        Application = request.env['waqf.support.application']
        
        vals = {
            'beneficiary_id': int(post.get('beneficiary_id')),
            'support_type': 'education',
        }
        
        application = Application.create(vals)
        
        # Create lines
        line_count = int(post.get('line_count', 0))
        for i in range(line_count):
            if post.get(f'line_type_{i}'):
                request.env['waqf.application.line'].create({
                    'application_id': application.id,
                    'line_type': post.get(f'line_type_{i}'),
                    'study_level': post.get(f'study_level_{i}'),
                    'city_mode': post.get(f'city_mode_{i}'),
                    'requested_amount': float(post.get(f'requested_amount_{i}', 0)),
                })
        
        return request.redirect('/my/application/%s' % application.id)
    
    @http.route(['/my/application/<int:application_id>'], type='http', auth="user", website=True)
    def portal_my_application(self, application_id, **kw):
        try:
            application_sudo = self._document_check_access('waqf.support.application', application_id)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        values = {
            'application': application_sudo,
            'page_name': 'application',
        }
        
        return request.render("waqf_portal_mvp.portal_application_detail", values)
    
    @http.route(['/my/application/<int:application_id>/submit'], type='http', auth="user", website=True)
    def portal_application_submit(self, application_id, **kw):
        try:
            application_sudo = self._document_check_access('waqf.support.application', application_id)
            application_sudo.action_submit()
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        return request.redirect('/my/application/%s' % application_id)