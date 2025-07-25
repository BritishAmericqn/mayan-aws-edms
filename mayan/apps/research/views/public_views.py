import logging
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from stronghold.views import StrongholdPublicMixin

from mayan.apps.documents.models import Document

from ..sharing.models import SharedDocument
from ..events import event_shared_document_accessed

logger = logging.getLogger(__name__)


# Simple test view to verify StrongholdPublicMixin works
class TestPublicView(StrongholdPublicMixin, TemplateView):
    template_name = 'research/sharing/test_public.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = 'Public access working!'
        return context


@method_decorator(csrf_exempt, name='dispatch')
class SharedDocumentAccessView(StrongholdPublicMixin, TemplateView):
    """
    Public view for external document access - NO AUTHENTICATION REQUIRED.
    Task 3.3: External Access View with professional interface and download tracking.
    """
    template_name = 'research/sharing/public_access.html'

    def dispatch(self, request, *args, **kwargs):
        # Get the shared document by URL key
        url_key = kwargs.get('url_key')
        
        try:
            self.shared_document = get_object_or_404(
                SharedDocument.objects.select_related('document', 'created_by'),
                url_key=url_key
            )
        except (SharedDocument.DoesNotExist, ValueError):
            raise Http404(_('Shared document not found or invalid link'))
        
        # Validate access is allowed
        if not self.shared_document.is_access_allowed():
            if self.shared_document.is_expired():
                return render(request, 'research/sharing/access_expired.html', {
                    'shared_document': self.shared_document,
                    'error_type': 'expired'
                })
            elif not self.shared_document.is_active:
                return render(request, 'research/sharing/access_denied.html', {
                    'shared_document': self.shared_document,
                    'error_type': 'inactive'
                })
            else:
                return render(request, 'research/sharing/access_denied.html', {
                    'shared_document': self.shared_document,
                    'error_type': 'limit_exceeded'
                })
        
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Record the access for compliance tracking
        client_ip = self.get_client_ip()
        self.shared_document.record_access(ip_address=client_ip)
        
        # Add context for template
        context.update({
            'shared_document': self.shared_document,
            'document': self.shared_document.document,
            'page_title': _('Shared Document: %s') % self.shared_document.document.label,
            'access_info': {
                'expires_at': self.shared_document.expires_at,
                'access_count': self.shared_document.access_count,
                'shared_by': self.shared_document.created_by.get_full_name() or 
                           self.shared_document.created_by.username,
                'share_label': self.shared_document.label,
                'time_until_expiry': self.shared_document.expires_at - timezone.now(),
            },
            'demo_mode': True,  # For demo styling
        })
        
        return context

    def get_client_ip(self):
        """Get client IP address for access tracking."""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


@method_decorator(csrf_exempt, name='dispatch')
class SharedDocumentDownloadView(StrongholdPublicMixin, DetailView):
    """
    Direct download view for shared documents.
    Task 3.3: Download tracking for compliance with proper file handling.
    """
    model = SharedDocument
    slug_field = 'url_key'
    slug_url_kwarg = 'url_key'

    def get(self, request, *args, **kwargs):
        shared_document = self.get_object()
        
        # Validate access
        if not shared_document.is_access_allowed():
            raise PermissionDenied(_('Access to this shared document is no longer available'))
        
        # Record access for compliance
        client_ip = self.get_client_ip()
        shared_document.record_access(ip_address=client_ip)
        
        # Note: Event firing removed to avoid actstream registration issues in public views
        
        try:
            # Get the document file
            document = shared_document.document
            if not document.file_latest:
                raise Http404(_('Document file not found'))
            
            document_file = document.file_latest
            
            # Open and return the file
            with document_file.open() as file_object:
                response = HttpResponse(
                    file_object.read(),
                    content_type=document_file.mimetype or 'application/octet-stream'
                )
                
                # Set download headers
                filename = document_file.filename or f"{document.label}.{document_file.file_extension}"
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                response['Content-Length'] = document_file.size
                
                return response
                
        except Exception as e:
            logger.error(f"Download failed for shared document {shared_document.url_key}: {e}")
            raise Http404(_('Unable to download document'))

    def get_client_ip(self):
        """Get client IP address for access tracking."""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


@method_decorator(csrf_exempt, name='dispatch')
class SharedDocumentPreviewView(StrongholdPublicMixin, TemplateView):
    """
    Public preview view for shared documents without download.
    Task 3.3: Professional viewing interface for external users.
    """
    template_name = 'research/sharing/public_preview.html'

    def dispatch(self, request, *args, **kwargs):
        url_key = kwargs.get('url_key')
        
        try:
            self.shared_document = get_object_or_404(
                SharedDocument.objects.select_related('document', 'created_by'),
                url_key=url_key
            )
        except (SharedDocument.DoesNotExist, ValueError):
            raise Http404(_('Shared document not found'))
        
        # Validate access
        if not self.shared_document.is_access_allowed():
            raise PermissionDenied(_('Access to this shared document is no longer available'))
        
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Record preview access
        client_ip = self.get_client_ip()
        self.shared_document.record_access(ip_address=client_ip)
        
        # Note: Event firing removed to avoid actstream registration issues in public views
        
        document = self.shared_document.document
        
        context.update({
            'shared_document': self.shared_document,
            'document': document,
            'page_title': _('Preview: %s') % document.label,
            'can_download': True,  # Could be configurable per share
            'file_info': {
                'size': document.file_latest.size if document.file_latest else 0,
                'type': document.file_latest.mimetype if document.file_latest else 'unknown',
                'filename': document.file_latest.filename if document.file_latest else document.label,
            },
            'access_info': {
                'expires_at': self.shared_document.expires_at,
                'time_remaining': self.shared_document.expires_at - timezone.now(),
                'shared_by': self.shared_document.created_by.get_full_name() or 
                           self.shared_document.created_by.username,
            }
        })
        
        return context

    def get_client_ip(self):
        """Get client IP address for access tracking."""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip 