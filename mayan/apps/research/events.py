"""
Research app events for audit trail and tracking.
"""
from django.utils.translation import gettext_lazy as _

from mayan.apps.events.classes import EventTypeNamespace

namespace = EventTypeNamespace(
    label='Research Platform', name='research'
)

# Project events
event_project_created = namespace.add_event_type(
    label='Project created', name='project_created'
)
event_project_edited = namespace.add_event_type(
    label='Project edited', name='project_edited'
)
event_project_deleted = namespace.add_event_type(
    label='Project deleted', name='project_deleted'
)
event_project_viewed = namespace.add_event_type(
    label='Project viewed', name='project_viewed'
)
event_project_exported = namespace.add_event_type(
    label='Project exported', name='project_exported'
)

# Study events
event_study_created = namespace.add_event_type(
    label='Study created', name='study_created'
)
event_study_edited = namespace.add_event_type(
    label='Study edited', name='study_edited'
)
event_study_deleted = namespace.add_event_type(
    label='Study deleted', name='study_deleted'
)
event_study_viewed = namespace.add_event_type(
    label='Study viewed', name='study_viewed'
)

# Dataset events
event_dataset_created = namespace.add_event_type(
    label='Dataset created', name='dataset_created'
)
event_dataset_edited = namespace.add_event_type(
    label='Dataset edited', name='dataset_edited'
)
event_dataset_deleted = namespace.add_event_type(
    label='Dataset deleted', name='dataset_deleted'
)
event_dataset_viewed = namespace.add_event_type(
    label='Dataset viewed', name='dataset_viewed'
)
event_dataset_analyzed = namespace.add_event_type(
    label='Dataset analyzed', name='dataset_analyzed'
)

# Task and processing events
event_dataset_analysis_started = namespace.add_event_type(
    label='Dataset analysis started', name='dataset_analysis_started'
)
event_dataset_analysis_completed = namespace.add_event_type(
    label='Dataset analysis completed', name='dataset_analysis_completed'
)
event_dataset_analysis_failed = namespace.add_event_type(
    label='Dataset analysis failed', name='dataset_analysis_failed'
)
event_dataset_processed = namespace.add_event_type(
    label='Dataset processed', name='dataset_processed'
)

# Document relationship events
event_dataset_document_added = namespace.add_event_type(
    label='Document added to dataset', name='dataset_document_added'
)
event_dataset_document_removed = namespace.add_event_type(
    label='Document removed from dataset', name='dataset_document_removed'
)

# Export and sharing events
event_dataset_exported = namespace.add_event_type(
    label='Dataset exported', name='dataset_exported'
)
event_dataset_shared = namespace.add_event_type(
    label='Dataset shared', name='dataset_shared'
)
event_dataset_share_expired = namespace.add_event_type(
    label='Dataset share link expired', name='dataset_share_expired'
)

# Analysis and quality events
event_quality_check_performed = namespace.add_event_type(
    label='Data quality check performed', name='quality_check_performed'
)
event_statistical_analysis_completed = namespace.add_event_type(
    label='Statistical analysis completed', name='statistical_analysis_completed'
)

# Task 2.2 enhanced events
event_enhanced_analysis_completed = namespace.add_event_type(
    label='Enhanced analysis completed', name='enhanced_analysis_completed'
)
event_professional_charts_generated = namespace.add_event_type(
    label='Professional charts generated', name='professional_charts_generated'
)
event_quality_indicators_calculated = namespace.add_event_type(
    label='Quality indicators calculated', name='quality_indicators_calculated'
) 

# Sharing and collaboration events (Task 3.1)
event_shared_document_created = namespace.add_event_type(
    label=_('Shared document created'), name='shared_document_created'
)
event_shared_document_accessed = namespace.add_event_type(
    label=_('Shared document accessed'), name='shared_document_accessed'
)
event_shared_document_expired = namespace.add_event_type(
    label=_('Shared document expired'), name='shared_document_expired'
)
event_shared_document_deleted = namespace.add_event_type(
    label=_('Shared document deleted'), name='shared_document_deleted'
) 