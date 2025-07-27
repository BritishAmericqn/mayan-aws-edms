"""
PDF Report Models for Research Platform.
Task 3.6: Professional report tracking and management.
"""
import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from mayan.apps.databases.model_mixins import ExtraDataModelMixin
from mayan.apps.events.decorators import method_event
from mayan.apps.events.event_managers import EventManagerSave, EventManagerMethodAfter

from ..events import (
    event_compliance_report_generated, event_audit_trail_accessed,
    event_backup_completed
)


class ReportRequest(ExtraDataModelMixin, models.Model):
    """
    Model to track PDF report generation requests.
    Following Mayan patterns with comprehensive audit trail.
    """
    
    REPORT_TYPES = [
        ('compliance', _('Compliance Report')),
        ('research_summary', _('Research Summary')),
        ('audit_trail', _('Audit Trail Report')),
        ('project_overview', _('Project Overview')),
        ('security_analysis', _('Security Analysis'))
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('expired', _('Expired'))
    ]
    
    # Core report fields
    request_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text=_('Unique identifier for this report request'),
        verbose_name=_('Request ID')
    )
    
    report_type = models.CharField(
        max_length=50,
        choices=REPORT_TYPES,
        help_text=_('Type of report to generate'),
        verbose_name=_('Report Type')
    )
    
    title = models.CharField(
        max_length=255,
        help_text=_('Human-readable title for this report'),
        verbose_name=_('Report Title')
    )
    
    # Request metadata
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='report_requests',
        help_text=_('User who requested this report'),
        verbose_name=_('Requested By')
    )
    
    requested_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('When this report was requested'),
        verbose_name=_('Requested At')
    )
    
    # Processing tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text=_('Current status of the report generation'),
        verbose_name=_('Status')
    )
    
    started_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('When report generation started'),
        verbose_name=_('Started At')
    )
    
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('When report generation completed'),
        verbose_name=_('Completed At')
    )
    
    # Report configuration
    parameters = models.JSONField(
        default=dict,
        blank=True,
        help_text=_('JSON parameters for report generation'),
        verbose_name=_('Parameters')
    )
    
    # File storage
    report_file = models.FileField(
        upload_to='research_reports/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text=_('Generated PDF report file'),
        verbose_name=_('Report File')
    )
    
    file_size = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=_('Size of the generated report file in bytes'),
        verbose_name=_('File Size')
    )
    
    # Error handling
    error_message = models.TextField(
        blank=True,
        help_text=_('Error message if report generation failed'),
        verbose_name=_('Error Message')
    )
    
    # Access tracking
    download_count = models.PositiveIntegerField(
        default=0,
        help_text=_('Number of times this report has been downloaded'),
        verbose_name=_('Download Count')
    )
    
    last_downloaded_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('When this report was last downloaded'),
        verbose_name=_('Last Downloaded At')
    )
    
    # Cleanup
    expires_at = models.DateTimeField(
        help_text=_('When this report will be automatically deleted'),
        verbose_name=_('Expires At')
    )

    class Meta:
        verbose_name = _('Report Request')
        verbose_name_plural = _('Report Requests')
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['request_id']),
            models.Index(fields=['status']),
            models.Index(fields=['requested_by', 'requested_at']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f'{self.get_report_type_display()} - {self.title}'

    def save(self, *args, **kwargs):
        # Set expiration if not provided (30 days default)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=30)
        
        super().save(*args, **kwargs)

    @method_event(
        event_manager_class=EventManagerSave,
        created={
            'event': event_compliance_report_generated,
            'target': 'self'
        }
    )
    def mark_completed(self, file_path, file_size):
        """Mark report as completed with file details."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.report_file = file_path
        self.file_size = file_size
        self.save(update_fields=['status', 'completed_at', 'report_file', 'file_size'])

    @method_event(
        event_manager_class=EventManagerMethodAfter,
        event=event_audit_trail_accessed,
        target='self'
    )
    def record_download(self, user=None):
        """Record a download of this report."""
        self._event_actor = user
        
        self.download_count += 1
        self.last_downloaded_at = timezone.now()
        self.save(update_fields=['download_count', 'last_downloaded_at'])

    def mark_failed(self, error_message):
        """Mark report generation as failed."""
        self.status = 'failed'
        self.error_message = error_message
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'error_message', 'completed_at'])

    def mark_processing(self):
        """Mark report as being processed."""
        self.status = 'processing'
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at'])

    def is_expired(self):
        """Check if this report has expired."""
        return timezone.now() > self.expires_at

    def get_download_filename(self):
        """Get appropriate filename for download."""
        timestamp = self.completed_at or self.requested_at
        safe_title = "".join(c for c in self.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        return f"{safe_title}_{timestamp.strftime('%Y%m%d_%H%M')}.pdf"

    def cleanup_expired(self):
        """Clean up expired report files."""
        if self.is_expired() and self.report_file:
            try:
                self.report_file.delete(save=False)
                self.delete()
                return True
            except Exception:
                return False
        return False

    @property
    def processing_duration(self):
        """Get the duration of report processing."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None

    @property
    def is_downloadable(self):
        """Check if report is ready for download."""
        return self.status == 'completed' and self.report_file and not self.is_expired()


class ReportTemplate(ExtraDataModelMixin, models.Model):
    """
    Model for reusable report templates.
    Allows users to save report configurations for repeated use.
    """
    
    name = models.CharField(
        max_length=255,
        help_text=_('Name of the report template'),
        verbose_name=_('Template Name')
    )
    
    report_type = models.CharField(
        max_length=50,
        choices=ReportRequest.REPORT_TYPES,
        help_text=_('Type of report this template generates'),
        verbose_name=_('Report Type')
    )
    
    description = models.TextField(
        blank=True,
        help_text=_('Description of what this template generates'),
        verbose_name=_('Description')
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='report_templates',
        help_text=_('User who created this template'),
        verbose_name=_('Created By')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('When this template was created'),
        verbose_name=_('Created At')
    )
    
    # Template configuration
    default_parameters = models.JSONField(
        default=dict,
        help_text=_('Default parameters for this report template'),
        verbose_name=_('Default Parameters')
    )
    
    is_public = models.BooleanField(
        default=False,
        help_text=_('Whether this template is available to all users'),
        verbose_name=_('Is Public')
    )
    
    usage_count = models.PositiveIntegerField(
        default=0,
        help_text=_('Number of times this template has been used'),
        verbose_name=_('Usage Count')
    )

    class Meta:
        verbose_name = _('Report Template')
        verbose_name_plural = _('Report Templates')
        ordering = ['name']
        unique_together = [['name', 'created_by']]

    def __str__(self):
        return f'{self.name} ({self.get_report_type_display()})'

    def use_template(self, user, additional_params=None):
        """Create a report request using this template."""
        parameters = self.default_parameters.copy()
        if additional_params:
            parameters.update(additional_params)
        
        request = ReportRequest.objects.create(
            report_type=self.report_type,
            title=f"{self.name} - {timezone.now().strftime('%Y-%m-%d %H:%M')}",
            requested_by=user,
            parameters=parameters
        )
        
        # Update usage count
        self.usage_count += 1
        self.save(update_fields=['usage_count'])
        
        return request 