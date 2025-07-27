"""
Background tasks for PDF report generation.
Task 3.6: Asynchronous report processing following Mayan patterns.
"""
import logging
import tempfile
import os
from datetime import datetime

from celery import current_app
from django.core.files.base import ContentFile
from django.apps import apps
from django.utils import timezone

from mayan.apps.lock_manager.backends.base import LockingBackend
from mayan.apps.lock_manager.exceptions import LockError

from .generators import (
    ComplianceReportGenerator, ResearchSummaryGenerator, 
    AuditTrailGenerator
)
from .models import ReportRequest
from ..events import event_compliance_report_generated, event_backup_completed

logger = logging.getLogger(__name__)


@current_app.task(bind=True, ignore_result=False, max_retries=3, retry_backoff=True)
def task_generate_pdf_report(self, request_id, user_id=None):
    """
    Generate a PDF report asynchronously.
    Task 3.6: Professional report generation with proper error handling.
    
    Args:
        request_id: ID of the ReportRequest to process
        user_id: ID of the user for audit trail (optional)
    """
    lock_id = f'report_generation_{request_id}'
    
    try:
        # Acquire lock to prevent duplicate processing
        with LockingBackend.get_backend_instance().acquire_lock(
            name=lock_id, timeout=3600  # 1 hour timeout
        ):
            logger.info(f'Starting PDF report generation for request {request_id}')
            
            # Get the report request
            try:
                report_request = ReportRequest.objects.get(pk=request_id)
            except ReportRequest.DoesNotExist:
                logger.error(f'Report request {request_id} not found')
                return {'status': 'error', 'message': f'Report request {request_id} not found'}
            
            # Mark as processing
            report_request.mark_processing()
            
            try:
                # Generate the appropriate report
                generator_class = _get_generator_class(report_request.report_type)
                if not generator_class:
                    raise ValueError(f'Unknown report type: {report_request.report_type}')
                
                # Initialize generator
                generator = generator_class(user=report_request.requested_by)
                
                # Generate report based on type and parameters
                report_buffer = _generate_report_content(
                    generator, 
                    report_request.report_type, 
                    report_request.parameters
                )
                
                # Save the generated report
                filename = report_request.get_download_filename()
                file_content = ContentFile(report_buffer.getvalue(), name=filename)
                
                # Create file path
                timestamp = timezone.now()
                file_path = f'research_reports/{timestamp.year}/{timestamp.month:02d}/{timestamp.day:02d}/{filename}'
                
                # Save to storage
                report_request.report_file.save(filename, file_content, save=False)
                report_request.mark_completed(
                    file_path=report_request.report_file.name,
                    file_size=len(report_buffer.getvalue())
                )
                
                # Fire completion event
                event_compliance_report_generated.commit(
                    actor=report_request.requested_by,
                    target=report_request,
                    action_object=None
                )
                
                logger.info(f'PDF report generation completed for request {request_id}')
                
                return {
                    'status': 'completed',
                    'request_id': request_id,
                    'file_size': len(report_buffer.getvalue()),
                    'filename': filename
                }
                
            except Exception as e:
                logger.error(f'Error generating PDF report for request {request_id}: {e}')
                
                # Mark as failed
                report_request.mark_failed(str(e))
                
                # Retry logic
                if self.request.retries < self.max_retries:
                    logger.info(f'Retrying PDF report generation for request {request_id} (attempt {self.request.retries + 1})')
                    raise self.retry(countdown=60 * (2 ** self.request.retries), exc=e)
                
                return {
                    'status': 'failed',
                    'request_id': request_id,
                    'error': str(e)
                }
                
    except LockError:
        logger.warning(f'Could not acquire lock for report generation {request_id}')
        return {'status': 'error', 'message': 'Report already being processed'}
    
    except Exception as e:
        logger.error(f'Unexpected error in PDF report generation for request {request_id}: {e}')
        return {'status': 'error', 'message': str(e)}


@current_app.task(bind=True, ignore_result=False)
def task_cleanup_expired_reports(self):
    """
    Clean up expired report files.
    Task 3.6: Maintenance task for report lifecycle management.
    """
    logger.info('Starting cleanup of expired reports')
    
    try:
        expired_reports = ReportRequest.objects.filter(
            expires_at__lt=timezone.now(),
            status='completed'
        )
        
        cleanup_count = 0
        total_size_freed = 0
        
        for report in expired_reports:
            if report.file_size:
                total_size_freed += report.file_size
            
            if report.cleanup_expired():
                cleanup_count += 1
        
        # Fire backup completion event (using as cleanup completion)
        event_backup_completed.commit(
            actor=None,  # System action
            target=None,
            action_object=None
        )
        
        logger.info(f'Cleanup completed: {cleanup_count} reports removed, {total_size_freed} bytes freed')
        
        return {
            'status': 'completed',
            'reports_cleaned': cleanup_count,
            'bytes_freed': total_size_freed
        }
        
    except Exception as e:
        logger.error(f'Error during report cleanup: {e}')
        return {'status': 'error', 'message': str(e)}


@current_app.task(bind=True, ignore_result=False)
def task_generate_scheduled_reports(self):
    """
    Generate scheduled reports automatically.
    Task 3.6: Automated report generation for regular compliance reports.
    """
    logger.info('Starting scheduled report generation')
    
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get system user or admin for automated reports
        system_user = User.objects.filter(is_superuser=True).first()
        if not system_user:
            logger.error('No admin user found for scheduled reports')
            return {'status': 'error', 'message': 'No admin user available'}
        
        # Generate weekly compliance report
        weekly_compliance = ReportRequest.objects.create(
            report_type='compliance',
            title=f'Weekly Compliance Report - {timezone.now().strftime("%Y-%m-%d")}',
            requested_by=system_user,
            parameters={'time_range_days': 7, 'automated': True}
        )
        
        # Queue the report generation
        task_generate_pdf_report.delay(weekly_compliance.id, system_user.id)
        
        logger.info(f'Scheduled compliance report queued: {weekly_compliance.id}')
        
        return {
            'status': 'completed',
            'reports_scheduled': 1,
            'report_ids': [weekly_compliance.id]
        }
        
    except Exception as e:
        logger.error(f'Error generating scheduled reports: {e}')
        return {'status': 'error', 'message': str(e)}


def _get_generator_class(report_type):
    """Get the appropriate generator class for the report type."""
    generator_map = {
        'compliance': ComplianceReportGenerator,
        'research_summary': ResearchSummaryGenerator,
        'audit_trail': AuditTrailGenerator,
        'project_overview': ResearchSummaryGenerator,  # Same as research summary
        'security_analysis': AuditTrailGenerator,  # Same as audit trail
    }
    
    return generator_map.get(report_type)


def _generate_report_content(generator, report_type, parameters):
    """Generate the actual report content based on type and parameters."""
    # Default parameters
    time_range_days = parameters.get('time_range_days', 30)
    project_id = parameters.get('project_id')
    event_types = parameters.get('event_types')
    
    if report_type == 'compliance':
        return generator.generate_report(time_range_days=time_range_days)
    
    elif report_type in ['research_summary', 'project_overview']:
        if not project_id:
            raise ValueError('Project ID required for research summary reports')
        return generator.generate_project_report(project_id=project_id)
    
    elif report_type in ['audit_trail', 'security_analysis']:
        return generator.generate_audit_report(
            time_range_days=time_range_days,
            event_types=event_types
        )
    
    else:
        raise ValueError(f'Unknown report type: {report_type}')


# Utility functions for report management

def queue_report_generation(report_type, user, title=None, parameters=None):
    """
    Utility function to queue a new report for generation.
    
    Args:
        report_type: Type of report to generate
        user: User requesting the report
        title: Optional custom title
        parameters: Optional report parameters
    
    Returns:
        ReportRequest instance
    """
    if not title:
        title = f'{report_type.replace("_", " ").title()} Report - {timezone.now().strftime("%Y-%m-%d %H:%M")}'
    
    report_request = ReportRequest.objects.create(
        report_type=report_type,
        title=title,
        requested_by=user,
        parameters=parameters or {}
    )
    
    # Queue the generation task
    task_generate_pdf_report.delay(report_request.id, user.id)
    
    logger.info(f'Queued {report_type} report generation for user {user.username}: {report_request.id}')
    
    return report_request


def get_user_reports(user, status=None, limit=None):
    """
    Get reports for a specific user with optional filtering.
    
    Args:
        user: User to get reports for
        status: Optional status filter
        limit: Optional limit on number of results
    
    Returns:
        QuerySet of ReportRequest objects
    """
    queryset = ReportRequest.objects.filter(requested_by=user)
    
    if status:
        queryset = queryset.filter(status=status)
    
    queryset = queryset.order_by('-requested_at')
    
    if limit:
        queryset = queryset[:limit]
    
    return queryset 