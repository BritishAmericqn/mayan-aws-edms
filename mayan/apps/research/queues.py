"""
Research task queues and worker configuration.
Enhanced for Task 2.2 with optimized task processing.
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