import logging
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.views.generic import FormView, DetailView, TemplateView, CreateView, ListView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from mayan.apps.documents.models import Document
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.views.view_mixins import ExternalObjectViewMixin

from ..sharing.forms import ShareDocumentForm, QuickShareForm
from ..sharing.models import SharedDocument
from ..sharing.generators import PreSignedURLGenerator
from ..permissions import permission_shared_document_create, permission_shared_document_view

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class DocumentShareView(ExternalObjectViewMixin, CreateView):
    """Main view for creating document shares with full form"""
    
    model = SharedDocument
    form_class = ShareDocumentForm
    template_name = 'research/sharing/document_share.html'
    external_object_class = Document
    external_object_permission = permission_shared_document_create
    success_url = reverse_lazy('research:share_success')
    
    def get_external_object(self):
        """Get the document to be shared"""
        return get_object_or_404(
            Document.objects.all(),
            pk=self.kwargs['document_id']
        )
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_initial(self):
        initial = super().get_initial()
        document = self.get_external_object()
        initial['document'] = document
        initial['label'] = f'Shared: {document.label}'
        return initial
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Store shared document ID in session for success page
        self.request.session['last_shared_document_id'] = self.object.id
        
        messages.success(
            self.request,
            _('Document shared successfully! Share link created.')
        )
        
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        document = self.get_external_object()
        
        context.update({
            'document': document,
            'existing_shares': SharedDocument.objects.filter(
                document=document,
                created_by=self.request.user,
                is_active=True
            ).order_by('-created_at')[:5],
            'page_title': _('Share Document: %s') % document.label,
        })
        
        return context


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class DocumentQuickShareView(ExternalObjectViewMixin, FormView):
    """AJAX view for quick sharing via modal"""
    
    form_class = QuickShareForm
    external_object_class = Document
    external_object_permission = permission_shared_document_create
    
    def get_external_object(self):
        """Get the document to be shared"""
        return get_object_or_404(
            Document.objects.all(),
            pk=self.kwargs['document_id']
        )
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['document'] = self.get_external_object()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        """Create share and return JSON response"""
        shared_doc = form.create_share()
        
        if shared_doc:
            # Generate the public URL
            public_url = shared_doc.get_public_url()
            
            return JsonResponse({
                'success': True,
                'message': _('Document shared successfully!'),
                'share_id': shared_doc.id,
                'share_url': public_url,
                'expires_at': shared_doc.expires_at.isoformat(),
                'label': shared_doc.label,
                'redirect_url': reverse('research:share_success') + f'?share_id={shared_doc.id}'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': _('Failed to create share'),
                'errors': form.errors
            })
    
    def form_invalid(self, form):
        """Return error JSON response"""
        return JsonResponse({
            'success': False,
            'message': _('Please correct the errors below'),
            'errors': form.errors
        })


@method_decorator(login_required, name='dispatch')
class DocumentShareSuccessView(DetailView):
    """Success page showing share details and copy-to-clipboard functionality"""
    
    model = SharedDocument
    template_name = 'research/sharing/share_success.html'
    context_object_name = 'shared_document'
    
    def get_object(self):
        """Get shared document from session or URL parameter"""
        share_id = self.request.GET.get('share_id') or self.request.session.get('last_shared_document_id')
        
        if not share_id:
            # Fallback to latest share by this user
            return SharedDocument.objects.filter(
                created_by=self.request.user
            ).order_by('-created_at').first()
        
        return get_object_or_404(
            SharedDocument.objects.filter(created_by=self.request.user),
            id=share_id
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shared_doc = self.get_object()
        
        if shared_doc:
            context.update({
                'share_url': shared_doc.get_public_url(),
                'download_url': shared_doc.get_download_url(),
                'preview_url': shared_doc.get_preview_url(),
                'page_title': _('Document Shared Successfully'),
            })
        
        return context


@method_decorator(login_required, name='dispatch')
class SharedDocumentListView(ListView):
    """List view for user's shared documents"""
    
    model = SharedDocument
    template_name = 'research/sharing/shared_document_list.html'
    context_object_name = 'shared_documents'
    paginate_by = 25
    
    def get_queryset(self):
        """Return shared documents for current user"""
        return SharedDocument.objects.filter(
            created_by=self.request.user
        ).select_related('document', 'created_by').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add summary statistics
        user_shares = self.get_queryset()
        context.update({
            'total_shares': user_shares.count(),
            'active_shares': user_shares.filter(is_active=True).count(),
            'expired_shares': user_shares.filter(is_active=False).count(),
            'page_title': _('My Shared Documents'),
        })
        
        return context 