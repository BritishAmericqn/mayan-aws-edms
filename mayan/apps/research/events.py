from django.utils.translation import gettext_lazy as _

from mayan.apps.events.classes import EventTypeNamespace

namespace = EventTypeNamespace(
    label=_('Research'), name='research'
)

# Project events
event_project_created = namespace.add_event_type(
    label=_('Project created'), name='project_created'
)
event_project_edited = namespace.add_event_type(
    label=_('Project edited'), name='project_edited'
)
event_project_deleted = namespace.add_event_type(
    label=_('Project deleted'), name='project_deleted'
)

# Study events
event_study_created = namespace.add_event_type(
    label=_('Study created'), name='study_created'
)
event_study_edited = namespace.add_event_type(
    label=_('Study edited'), name='study_edited'
)
event_study_deleted = namespace.add_event_type(
    label=_('Study deleted'), name='study_deleted'
)

# Dataset events
event_dataset_created = namespace.add_event_type(
    label=_('Dataset created'), name='dataset_created'
)
event_dataset_edited = namespace.add_event_type(
    label=_('Dataset edited'), name='dataset_edited'
)
event_dataset_deleted = namespace.add_event_type(
    label=_('Dataset deleted'), name='dataset_deleted'
)

# Document-dataset relationship events
event_dataset_document_added = namespace.add_event_type(
    label=_('Document added to dataset'), name='dataset_document_added'
)
event_dataset_document_removed = namespace.add_event_type(
    label=_('Document removed from dataset'), name='dataset_document_removed'
)

# Analysis and processing events
event_dataset_analysis_started = namespace.add_event_type(
    label=_('Dataset analysis started'), name='dataset_analysis_started'
)
event_dataset_analysis_completed = namespace.add_event_type(
    label=_('Dataset analysis completed'), name='dataset_analysis_completed'
)
event_dataset_analysis_failed = namespace.add_event_type(
    label=_('Dataset analysis failed'), name='dataset_analysis_failed'
)

# Data processing events
event_dataset_processed = namespace.add_event_type(
    label=_('Dataset processed'), name='dataset_processed'
)
event_dataset_validation_completed = namespace.add_event_type(
    label=_('Dataset validation completed'), name='dataset_validation_completed'
)

# Export and sharing events
event_dataset_exported = namespace.add_event_type(
    label=_('Dataset exported'), name='dataset_exported'
)
event_project_shared = namespace.add_event_type(
    label=_('Project shared'), name='project_shared'
)
event_dataset_shared = namespace.add_event_type(
    label=_('Dataset results shared'), name='dataset_shared'
)

# Status change events
event_dataset_status_changed = namespace.add_event_type(
    label=_('Dataset status changed'), name='dataset_status_changed'
)
event_study_status_changed = namespace.add_event_type(
    label=_('Study status changed'), name='study_status_changed'
)

# Preview generation events (for demo)
event_dataset_preview_generated = namespace.add_event_type(
    label=_('Dataset preview generated'), name='dataset_preview_generated'
) 