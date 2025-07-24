from django.utils.translation import gettext_lazy as _

from mayan.apps.task_manager.classes import CeleryQueue
from mayan.apps.task_manager.workers import worker_c


queue_research_analysis = CeleryQueue(
    label=_('Research analysis'), name='research_analysis', worker=worker_c
)

queue_research_analysis.add_task_type(
    dotted_path='mayan.apps.research.tasks.task_dataset_analyze',
    label=_('Analyze dataset'), name='task_dataset_analyze'
)

queue_research_analysis.add_task_type(
    dotted_path='mayan.apps.research.tasks.task_dataset_process_file',
    label=_('Process dataset file'), name='task_dataset_process_file'
)

queue_research_analysis.add_task_type(
    dotted_path='mayan.apps.research.tasks.task_generate_dataset_preview',
    label=_('Generate dataset preview'), name='task_generate_dataset_preview'
)

queue_research_analysis.add_task_type(
    dotted_path='mayan.apps.research.tasks.task_export_dataset',
    label=_('Export dataset'), name='task_export_dataset'
)


queue_research_sharing = CeleryQueue(
    label=_('Research sharing'), name='research_sharing', worker=worker_c
)

queue_research_sharing.add_task_type(
    dotted_path='mayan.apps.research.tasks.task_generate_share_link',
    label=_('Generate share link'), name='task_generate_share_link'
)

queue_research_sharing.add_task_type(
    dotted_path='mayan.apps.research.tasks.task_cleanup_expired_shares',
    label=_('Cleanup expired shares'), name='task_cleanup_expired_shares'
) 