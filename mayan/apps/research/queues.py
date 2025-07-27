"""
Research task queues and worker configuration.
Enhanced for Task 2.2 with optimized task processing.
Task 3.6: Added PDF report generation tasks (temporarily disabled pending ReportLab installation).
"""
from django.utils.translation import gettext_lazy as _

from mayan.apps.task_manager.classes import CeleryQueue
from mayan.apps.task_manager.workers import worker_c, worker_d

queue_research = CeleryQueue(
    label=_('Research Analysis'), name='research_analysis', 
    worker=worker_c  # Medium latency for data processing
)

# Task 2.1 and 2.2: Enhanced dataset analysis
queue_research.add_task_type(
    dotted_path='mayan.apps.research.tasks.task_analyze_dataset',
    label=_('Analyze dataset'), name='task_analyze_dataset'
)

# Document processing
queue_research.add_task_type(
    dotted_path='mayan.apps.research.tasks.task_process_dataset_documents',
    label=_('Process dataset documents'), name='task_process_dataset_documents'
)

# Task 3.6: PDF Report Generation Tasks
# Note: Requires ReportLab installation in production environment
# ReportLab is optional - tasks will handle gracefully if not installed

queue_research.add_task_type(
    dotted_path='mayan.apps.research.reports.tasks.task_generate_pdf_report',
    label=_('Generate PDF report'), name='task_generate_pdf_report'
)

queue_research.add_task_type(
    dotted_path='mayan.apps.research.reports.tasks.task_cleanup_expired_reports',
    label=_('Cleanup expired reports'), name='task_cleanup_expired_reports'
)
queue_research.add_task_type(
    dotted_path='mayan.apps.research.reports.tasks.task_generate_scheduled_reports',
    label=_('Generate scheduled reports'), name='task_generate_scheduled_reports'
) 