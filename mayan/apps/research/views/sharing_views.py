import logging
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.views.generic import FormView, DetailView, TemplateView

from mayan.apps.documents.models import Document
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.views.view_mixins import ExternalObjectViewMixin

from ..sharing.forms import ShareDocumentForm, QuickShareForm
from ..sharing.models import SharedDocument
from ..sharing.generators import PreSignedURLGenerator
from ..permissions import permission_shared_document_create, permission_shared_document_view

logger = logging.getLogger(__name__)


class DocumentShareView(LoginRequiredMixin, ExternalObjectViewMixin, FormView):
    """
    Full document sharing view with comprehensive options.
    Task 3.2: Complete sharing workflow with form validation.
    """
    template_name = 'research/sharing/document_share.html'
    form_class = ShareDocumentForm
    external_object_permission = permission_document_view
    external_object_pk_url_kwarg = 'document_id'
    external_object_queryset = Document.valid

    def get_success_url(self):
        return reverse(
            'research:document_share_success',
            kwargs={'document_id': self.external_object.pk}
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['document'] = self.external_object
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['document'] = self.external_object
        context['page_title'] = _('Share Document: %s') % self.external_object.label
        
        # Add existing shares for this document
        context['existing_shares'] = SharedDocument.objects.filter(
            document=self.external_object,
            created_by=self.request.user
        ).order_by('-created_at')[:5]  # Last 5 shares
        
        return context

    def form_valid(self, form):
        try:
            # Create the shared document
            shared_document = form.save()
            
            # Generate the sharing URL
            generator = PreSignedURLGenerator()
            url_info = generator.generate_url(
                document=self.external_object,
                expiration_hours=int(form.cleaned_data['expiration_hours']),
                shared_document=shared_document
            )
            
            # Store URL info in session for success page
            self.request.session['share_url_info'] = url_info
            
            messages.success(
                self.request,
                _('Document shared successfully! Link expires: %s') % 
                shared_document.expires_at.strftime('%Y-%m-%d %H:%M')
            )
            
            return super().form_valid(form)
            
        except Exception as e:
            logger.error(f"Document sharing failed: {e}")
            messages.error(
                self.request,
                _('Failed to create sharing link. Please try again.')
            )
            return self.form_invalid(form)


class DocumentQuickShareView(LoginRequiredMixin, ExternalObjectViewMixin, FormView):
    """
    Quick share modal view for AJAX requests.
    Task 3.2: Modal integration with fast sharing workflow.
    """
    template_name = 'research/sharing/quick_share_modal.html'
    form_class = QuickShareForm
    external_object_permission = permission_document_view
    external_object_pk_url_kwarg = 'document_id'
    external_object_queryset = Document.valid

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['document'] = self.external_object
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        try:
            # Create share using form method
            share_info = form.create_share()
            
            if not share_info:
                return JsonResponse({
                    'success': False,
                    'error': _('Failed to create sharing link')
                })
            
            # Return JSON response for AJAX
            if self.request.headers.get('Accept') == 'application/json':
                return JsonResponse({
                    'success': True,
                    'share_url': share_info['url_info']['url'],
                    'expires_at': share_info['url_info']['expires_at'].isoformat(),
                    'share_key': str(share_info['shared_document'].url_key)[:8] + '...',
                    'demo_info': share_info['url_info'].get('demo_info', {}),
                    'message': _('Sharing link created successfully!')
                })
            
            # Regular form submission - redirect to success page
            self.request.session['quick_share_info'] = share_info
            return HttpResponseRedirect(
                reverse('research:document_share_success', 
                       kwargs={'document_id': self.external_object.pk})
            )
            
        except Exception as e:
            logger.error(f"Quick share failed: {e}")
            
            if self.request.headers.get('Accept') == 'application/json':
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                })
            
            messages.error(self.request, _('Quick share failed. Please try again.'))
            return self.form_invalid(form)

    def form_invalid(self, form):
        if self.request.headers.get('Accept') == 'application/json':
            return JsonResponse({
                'success': False,
                'errors': form.errors,
                'error': _('Form validation failed')
            })
        return super().form_invalid(form)


class DocumentShareSuccessView(LoginRequiredMixin, ExternalObjectViewMixin, TemplateView):
    """
    Success page showing sharing link with copy-to-clipboard functionality.
    Task 3.2: Copy-to-clipboard JavaScript integration.
    """
    template_name = 'research/sharing/share_success.html'
    external_object_permission = permission_document_view
    external_object_pk_url_kwarg = 'document_id'
    external_object_queryset = Document.valid

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['document'] = self.external_object
        
        # Get share info from session
        share_url_info = self.request.session.pop('share_url_info', None)
        quick_share_info = self.request.session.pop('quick_share_info', None)
        
        if share_url_info:
            context['share_url_info'] = share_url_info
        elif quick_share_info:
            context['share_url_info'] = quick_share_info['url_info']
            context['quick_share'] = True
        else:
            # Fallback - get most recent share for this document
            recent_share = SharedDocument.objects.filter(
                document=self.external_object,
                created_by=self.request.user
            ).order_by('-created_at').first()
            
            if recent_share:
                generator = PreSignedURLGenerator()
                context['share_url_info'] = generator._generate_mayan_sharing_url(
                    self.external_object, recent_share.expires_at, recent_share
                )
        
        return context


class SharedDocumentListView(LoginRequiredMixin, TemplateView):
    """
    List view of user's shared documents for management.
    Task 3.2: Management interface for existing shares.
    """
    template_name = 'research/sharing/shared_document_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get user's shared documents
        shared_documents = SharedDocument.objects.filter(
            created_by=self.request.user
        ).select_related('document').order_by('-created_at')
        
        context['shared_documents'] = shared_documents
        context['page_title'] = _('My Shared Documents')
        
        # Add statistics for demo
        context['total_shares'] = shared_documents.count()
        context['active_shares'] = shared_documents.filter(
            expires_at__gt=timezone.now(),
            is_active=True
        ).count()
        
        return context 