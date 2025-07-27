"""
PDF Report Management Views for Research Platform.
Task 3.6: Professional report generation and download views.
"""
import logging
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, FormView, DetailView

from mayan.apps.views.view_mixins import ExternalObjectViewMixin
from mayan.apps.storage.views.mixins import ViewMixinDownload

from ..permissions import permission_compliance_report_create
from ..models import Project
from ..reports.models import ReportRequest, ReportTemplate
from ..reports.tasks import queue_report_generation, get_user_reports
from ..forms import ReportRequestForm, ReportTemplateForm
from ..reports.generators import (
    ComplianceReportGenerator, ResearchSummaryGenerator, 
    AuditTrailGenerator, REPORTLAB_AVAILABLE
)

logger = logging.getLogger(__name__)


class ReportDashboardView(LoginRequiredMixin, TemplateView):
    """
    Main dashboard for PDF report management.
    Task 3.6: Central hub for all report activities.
    """
    template_name = 'research/reports/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get user reports with error handling for missing tables
        try:
            user_reports = get_user_reports(self.request.user)
            total_reports = user_reports.count()
            recent_reports = user_reports[:5]
        except Exception:
            # Handle missing database tables gracefully
            total_reports = 0
            recent_reports = []
        
        context.update({
            'page_title': _('Report Dashboard'),
            'total_reports': total_reports,
            'recent_reports': recent_reports,
            'report_types': [
                {'value': 'compliance', 'label': _('Compliance Report')},
                {'value': 'research_summary', 'label': _('Research Summary')},
                {'value': 'audit_trail', 'label': _('Audit Trail')},
                {'value': 'security_analysis', 'label': _('Security Analysis')},
            ],
            'demo_note': _('PDF generation requires additional setup. Database migrations pending for full functionality.')
        })
        
        return context


class ReportRequestView(LoginRequiredMixin, FormView):
    """
    View for requesting new PDF reports.
    Task 3.6: Professional report request interface.
    """
    template_name = 'research/reports/request_report.html'
    form_class = ReportRequestForm
    success_url = reverse_lazy('research:report_dashboard')
    
    def dispatch(self, request, *args, **kwargs):
        # Check if PDF generation is available
        if not REPORTLAB_AVAILABLE:
            messages.error(
                request, 
                _('PDF report generation is not available. ReportLab library is required.')
            )
            return redirect('research:report_dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        try:
            # Create the report request
            report_request = queue_report_generation(
                report_type=form.cleaned_data['report_type'],
                user=self.request.user,
                title=form.cleaned_data.get('title'),
                parameters=form.get_parameters()
            )
            
            messages.success(
                self.request,
                _('Report "{}" has been queued for generation. You will be notified when it\'s ready.').format(
                    report_request.title
                )
            )
            
            logger.info(f'Report requested by {self.request.user.username}: {report_request.id}')
            
        except Exception as e:
            logger.error(f'Error creating report request: {e}')
            messages.error(
                self.request,
                _('Failed to create report request. Please try again.')
            )
        
        return super().form_valid(form)


class ReportListView(LoginRequiredMixin, TemplateView):
    """
    List view for user's PDF reports.
    Task 3.6: Professional report management interface.
    """
    template_name = 'research/reports/report_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filtering parameters
        status_filter = self.request.GET.get('status')
        report_type_filter = self.request.GET.get('report_type')
        
        # Build queryset
        reports = ReportRequest.objects.filter(requested_by=self.request.user)
        
        if status_filter:
            reports = reports.filter(status=status_filter)
        
        if report_type_filter:
            reports = reports.filter(report_type=report_type_filter)
        
        reports = reports.order_by('-requested_at')
        
        context.update({
            'page_title': _('My Reports'),
            'reports': reports,
            'status_filter': status_filter,
            'report_type_filter': report_type_filter,
            'status_choices': ReportRequest.STATUS_CHOICES,
            'report_type_choices': ReportRequest.REPORT_TYPES
        })
        
        return context


class ReportDetailView(LoginRequiredMixin, DetailView):
    """
    Detailed view for individual PDF reports.
    Task 3.6: Report details and download interface.
    """
    model = ReportRequest
    template_name = 'research/reports/report_detail.html'
    context_object_name = 'report'
    pk_url_kwarg = 'report_id'
    
    def get_queryset(self):
        # Users can only view their own reports
        return ReportRequest.objects.filter(requested_by=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Report Details')
        return context


class ReportDownloadView(LoginRequiredMixin, ViewMixinDownload, DetailView):
    """
    Download view for completed PDF reports.
    Task 3.6: Secure report download with access tracking.
    """
    model = ReportRequest
    pk_url_kwarg = 'report_id'
    
    def get_queryset(self):
        # Users can only download their own reports
        return ReportRequest.objects.filter(
            requested_by=self.request.user,
            status='completed'
        )
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        
        # Check if report is downloadable
        if not obj.is_downloadable:
            if obj.is_expired():
                raise Http404(_('This report has expired and is no longer available'))
            else:
                raise Http404(_('This report is not ready for download'))
        
        return obj
    
    def get_download_file_object(self):
        report = self.get_object()
        
        # Record the download
        report.record_download(user=self.request.user)
        
        # Return the file object
        return report.report_file.open('rb')
    
    def get_download_filename(self):
        return self.get_object().get_download_filename()


class ReportDeleteView(LoginRequiredMixin, DetailView):
    """
    Delete view for user's PDF reports.
    Task 3.6: Allow users to manually delete their reports.
    """
    model = ReportRequest
    pk_url_kwarg = 'report_id'
    
    def get_queryset(self):
        return ReportRequest.objects.filter(requested_by=self.request.user)
    
    def post(self, request, *args, **kwargs):
        report = self.get_object()
        
        try:
            # Clean up the file if it exists
            if report.report_file:
                report.report_file.delete(save=False)
            
            # Delete the report record
            report_title = report.title
            report.delete()
            
            messages.success(
                request,
                _('Report "{}" has been deleted successfully.').format(report_title)
            )
            
            logger.info(f'Report deleted by {request.user.username}: {report_title}')
            
        except Exception as e:
            logger.error(f'Error deleting report {report.id}: {e}')
            messages.error(
                request,
                _('Failed to delete report. Please try again.')
            )
        
        return redirect('research:report_list')


class QuickReportView(LoginRequiredMixin, TemplateView):
    """
    AJAX view for quick report generation.
    Task 3.6: Fast report creation with minimal UI interaction.
    """
    
    def post(self, request, *args, **kwargs):
        report_type = request.POST.get('report_type')
        project_id = request.POST.get('project_id')
        time_range = request.POST.get('time_range', '30')
        
        if not report_type:
            return JsonResponse({
                'status': 'error',
                'message': _('Report type is required')
            })
        
        try:
            # Prepare parameters
            parameters = {'time_range_days': int(time_range)}
            if project_id:
                parameters['project_id'] = int(project_id)
            
            # Generate title
            title_map = {
                'compliance': _('Quick Compliance Report'),
                'research_summary': _('Quick Research Summary'),
                'audit_trail': _('Quick Audit Trail'),
                'security_analysis': _('Quick Security Analysis')
            }
            title = title_map.get(report_type, _('Quick Report'))
            
            # Queue the report
            report_request = queue_report_generation(
                report_type=report_type,
                user=request.user,
                title=title,
                parameters=parameters
            )
            
            return JsonResponse({
                'status': 'success',
                'message': _('Report queued successfully'),
                'report_id': report_request.id,
                'title': report_request.title
            })
            
        except Exception as e:
            logger.error(f'Error in quick report generation: {e}')
            return JsonResponse({
                'status': 'error',
                'message': _('Failed to queue report. Please try again.')
            })


class ReportStatusAPIView(LoginRequiredMixin, DetailView):
    """
    API view for checking report generation status.
    Task 3.6: Real-time status updates for report generation.
    """
    model = ReportRequest
    pk_url_kwarg = 'report_id'
    
    def get_queryset(self):
        return ReportRequest.objects.filter(requested_by=self.request.user)
    
    def get(self, request, *args, **kwargs):
        report = self.get_object()
        
        response_data = {
            'status': report.status,
            'title': report.title,
            'requested_at': report.requested_at.isoformat(),
            'is_downloadable': report.is_downloadable,
        }
        
        if report.status == 'completed':
            response_data.update({
                'completed_at': report.completed_at.isoformat(),
                'file_size': report.file_size,
                'download_url': reverse_lazy('research:report_download', kwargs={'report_id': report.id})
            })
        elif report.status == 'failed':
            response_data['error_message'] = report.error_message
        elif report.status == 'processing':
            if report.started_at:
                response_data['started_at'] = report.started_at.isoformat()
        
        if report.processing_duration:
            response_data['processing_duration'] = str(report.processing_duration)
        
        return JsonResponse(response_data)


# Project-specific report views

class ProjectReportView(LoginRequiredMixin, ExternalObjectViewMixin, FormView):
    """
    Generate reports for specific projects.
    Task 3.6: Project-focused reporting interface.
    """
    template_name = 'research/reports/project_report.html'
    form_class = ReportRequestForm
    external_object_pk_url_kwarg = 'project_id'
    external_object_class = Project
    
    def get_external_object_permission(self):
        return permission_compliance_report_create
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['project'] = self.external_object
        return kwargs
    
    def form_valid(self, form):
        try:
            # Create project-specific report
            parameters = form.get_parameters()
            parameters['project_id'] = self.external_object.id
            
            report_request = queue_report_generation(
                report_type='research_summary',
                user=self.request.user,
                title=f'Project Report: {self.external_object.title}',
                parameters=parameters
            )
            
            messages.success(
                self.request,
                _('Project report for "{}" has been queued for generation.').format(
                    self.external_object.title
                )
            )
            
            return redirect('research:report_detail', report_id=report_request.id)
            
        except Exception as e:
            logger.error(f'Error creating project report: {e}')
            messages.error(
                self.request,
                _('Failed to create project report. Please try again.')
            )
            return self.form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': _('Generate Project Report'),
            'project': self.external_object
        })
        return context 