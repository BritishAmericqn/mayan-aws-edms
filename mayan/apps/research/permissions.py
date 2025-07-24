from django.utils.translation import gettext_lazy as _

from mayan.apps.permissions.classes import PermissionNamespace

namespace = PermissionNamespace(
    label=_('Research'), name='research'
)

# Project permissions
permission_project_view = namespace.add_permission(
    label=_('View projects'), name='project_view'
)
permission_project_create = namespace.add_permission(
    label=_('Create projects'), name='project_create'
)
permission_project_edit = namespace.add_permission(
    label=_('Edit projects'), name='project_edit'
)
permission_project_delete = namespace.add_permission(
    label=_('Delete projects'), name='project_delete'
)

# Study permissions  
permission_study_view = namespace.add_permission(
    label=_('View studies'), name='study_view'
)
permission_study_create = namespace.add_permission(
    label=_('Create studies'), name='study_create'
)
permission_study_edit = namespace.add_permission(
    label=_('Edit studies'), name='study_edit'
)
permission_study_delete = namespace.add_permission(
    label=_('Delete studies'), name='study_delete'
)

# Dataset permissions
permission_dataset_view = namespace.add_permission(
    label=_('View datasets'), name='dataset_view'
)
permission_dataset_create = namespace.add_permission(
    label=_('Create datasets'), name='dataset_create'
)
permission_dataset_edit = namespace.add_permission(
    label=_('Edit datasets'), name='dataset_edit'
)
permission_dataset_delete = namespace.add_permission(
    label=_('Delete datasets'), name='dataset_delete'
)

# Document-dataset relationship permissions
permission_dataset_document_add = namespace.add_permission(
    label=_('Add documents to datasets'), name='dataset_document_add'
)
permission_dataset_document_remove = namespace.add_permission(
    label=_('Remove documents from datasets'), name='dataset_document_remove'
)

# Analysis and processing permissions
permission_dataset_analyze = namespace.add_permission(
    label=_('Analyze datasets'), name='dataset_analyze'
)
permission_dataset_process = namespace.add_permission(
    label=_('Process datasets'), name='dataset_process'
)
permission_dataset_export = namespace.add_permission(
    label=_('Export dataset results'), name='dataset_export'
)

# Sharing and collaboration permissions
permission_project_share = namespace.add_permission(
    label=_('Share projects'), name='project_share'
)
permission_dataset_share = namespace.add_permission(
    label=_('Share dataset results'), name='dataset_share'
)

# Advanced permissions for demo features
permission_project_statistics = namespace.add_permission(
    label=_('View project statistics'), name='project_statistics'
)
permission_dataset_preview = namespace.add_permission(
    label=_('Generate dataset previews'), name='dataset_preview'
) 