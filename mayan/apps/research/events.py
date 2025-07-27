"""
Research app events for comprehensive audit trail and tracking.
Enhanced for Task 3.4: Advanced audit events beyond basic CRUD.
"""
from django.utils.translation import gettext_lazy as _

from mayan.apps.events.classes import EventTypeNamespace

namespace = EventTypeNamespace(
    label=_('Research Platform'), name='research'
)

# Basic Project events
event_project_created = namespace.add_event_type(
    label=_('Project created'), name='project_created'
)
event_project_edited = namespace.add_event_type(
    label=_('Project edited'), name='project_edited'
)
event_project_deleted = namespace.add_event_type(
    label=_('Project deleted'), name='project_deleted'
)
event_project_viewed = namespace.add_event_type(
    label=_('Project viewed'), name='project_viewed'
)
event_project_exported = namespace.add_event_type(
    label=_('Project exported'), name='project_exported'
)

# Basic Study events
event_study_created = namespace.add_event_type(
    label=_('Study created'), name='study_created'
)
event_study_edited = namespace.add_event_type(
    label=_('Study edited'), name='study_edited'
)
event_study_deleted = namespace.add_event_type(
    label=_('Study deleted'), name='study_deleted'
)
event_study_viewed = namespace.add_event_type(
    label=_('Study viewed'), name='study_viewed'
)

# Basic Dataset events
event_dataset_created = namespace.add_event_type(
    label=_('Dataset created'), name='dataset_created'
)
event_dataset_edited = namespace.add_event_type(
    label=_('Dataset edited'), name='dataset_edited'
)
event_dataset_deleted = namespace.add_event_type(
    label=_('Dataset deleted'), name='dataset_deleted'
)
event_dataset_viewed = namespace.add_event_type(
    label=_('Dataset viewed'), name='dataset_viewed'
)
event_dataset_analyzed = namespace.add_event_type(
    label=_('Dataset analyzed'), name='dataset_analyzed'
)

# Task and processing events
event_dataset_analysis_started = namespace.add_event_type(
    label=_('Dataset analysis started'), name='dataset_analysis_started'
)
event_dataset_analysis_completed = namespace.add_event_type(
    label=_('Dataset analysis completed'), name='dataset_analysis_completed'
)
event_dataset_analysis_failed = namespace.add_event_type(
    label=_('Dataset analysis failed'), name='dataset_analysis_failed'
)

# === TASK 3.4: ENHANCED AUDIT EVENTS ===

# Data Quality and Validation Events
event_data_quality_check_performed = namespace.add_event_type(
    label=_('Data quality check performed'), name='data_quality_check_performed'
)
event_data_validation_passed = namespace.add_event_type(
    label=_('Data validation passed'), name='data_validation_passed'
)
event_data_validation_failed = namespace.add_event_type(
    label=_('Data validation failed'), name='data_validation_failed'
)
event_data_integrity_verified = namespace.add_event_type(
    label=_('Data integrity verified'), name='data_integrity_verified'
)
event_statistical_analysis_completed = namespace.add_event_type(
    label=_('Statistical analysis completed'), name='statistical_analysis_completed'
)

# Compliance and Audit Events
event_compliance_report_generated = namespace.add_event_type(
    label=_('Compliance report generated'), name='compliance_report_generated'
)
event_audit_trail_accessed = namespace.add_event_type(
    label=_('Audit trail accessed'), name='audit_trail_accessed'
)
event_data_retention_policy_applied = namespace.add_event_type(
    label=_('Data retention policy applied'), name='data_retention_policy_applied'
)
event_security_scan_performed = namespace.add_event_type(
    label=_('Security scan performed'), name='security_scan_performed'
)
event_access_control_modified = namespace.add_event_type(
    label=_('Access control modified'), name='access_control_modified'
)

# Document Sharing and External Access Events
event_shared_document_created = namespace.add_event_type(
    label=_('Document shared externally'), name='shared_document_created'
)
event_shared_document_accessed = namespace.add_event_type(
    label=_('Shared document accessed'), name='shared_document_accessed'
)
event_shared_document_downloaded = namespace.add_event_type(
    label=_('Shared document downloaded'), name='shared_document_downloaded'
)
event_shared_document_expired = namespace.add_event_type(
    label=_('Shared document expired'), name='shared_document_expired'
)
event_shared_document_revoked = namespace.add_event_type(
    label=_('Shared document access revoked'), name='shared_document_revoked'
)

# Collaboration and Team Events
event_research_team_member_added = namespace.add_event_type(
    label=_('Research team member added'), name='research_team_member_added'
)
event_research_team_member_removed = namespace.add_event_type(
    label=_('Research team member removed'), name='research_team_member_removed'
)
event_permission_granted = namespace.add_event_type(
    label=_('Research permission granted'), name='permission_granted'
)
event_permission_revoked = namespace.add_event_type(
    label=_('Research permission revoked'), name='permission_revoked'
)

# Advanced Analytics and Processing Events
event_machine_learning_model_applied = namespace.add_event_type(
    label=_('Machine learning model applied'), name='machine_learning_model_applied'
)
event_pattern_analysis_completed = namespace.add_event_type(
    label=_('Pattern analysis completed'), name='pattern_analysis_completed'
)
event_predictive_analysis_performed = namespace.add_event_type(
    label=_('Predictive analysis performed'), name='predictive_analysis_performed'
)
event_data_visualization_generated = namespace.add_event_type(
    label=_('Data visualization generated'), name='data_visualization_generated'
)

# External Integration Events  
event_external_system_accessed = namespace.add_event_type(
    label=_('External system accessed'), name='external_system_accessed'
)
event_data_exported_external = namespace.add_event_type(
    label=_('Data exported to external system'), name='data_exported_external'
)
event_api_access_requested = namespace.add_event_type(
    label=_('API access requested'), name='api_access_requested'
)

# Performance and System Events
event_large_dataset_processed = namespace.add_event_type(
    label=_('Large dataset processed'), name='large_dataset_processed'
)
event_system_performance_measured = namespace.add_event_type(
    label=_('System performance measured'), name='system_performance_measured'
)
event_backup_completed = namespace.add_event_type(
    label=_('Research data backup completed'), name='backup_completed'
)

# Advanced Workflow Events
event_research_milestone_reached = namespace.add_event_type(
    label=_('Research milestone reached'), name='research_milestone_reached'
)
event_publication_prepared = namespace.add_event_type(
    label=_('Publication prepared'), name='publication_prepared'
)
event_peer_review_initiated = namespace.add_event_type(
    label=_('Peer review initiated'), name='peer_review_initiated'
)

# === MISSING EVENTS FOR EXISTING MODEL IMPORTS ===

# Document relationship events (needed by dataset_models.py)
event_dataset_document_added = namespace.add_event_type(
    label=_('Document added to dataset'), name='dataset_document_added'
)
event_dataset_document_removed = namespace.add_event_type(
    label=_('Document removed from dataset'), name='dataset_document_removed'
)

# Additional processing events (needed by other models)
event_dataset_processed = namespace.add_event_type(
    label=_('Dataset processed'), name='dataset_processed'
)
event_dataset_exported = namespace.add_event_type(
    label=_('Dataset exported'), name='dataset_exported'
)
event_dataset_shared = namespace.add_event_type(
    label=_('Dataset shared'), name='dataset_shared'
)
event_dataset_share_expired = namespace.add_event_type(
    label=_('Dataset share link expired'), name='dataset_share_expired'
)

# Quality and enhanced analysis events (needed by other models)
event_enhanced_analysis_completed = namespace.add_event_type(
    label=_('Enhanced analysis completed'), name='enhanced_analysis_completed'
)
event_professional_charts_generated = namespace.add_event_type(
    label=_('Professional charts generated'), name='professional_charts_generated'
)
event_quality_indicators_calculated = namespace.add_event_type(
    label=_('Quality indicators calculated'), name='quality_indicators_calculated'
)

# Legacy sharing events (needed by existing code)
event_shared_document_deleted = namespace.add_event_type(
    label=_('Shared document deleted'), name='shared_document_deleted'
) 