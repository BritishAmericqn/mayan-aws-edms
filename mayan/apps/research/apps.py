from django.utils.translation import gettext_lazy as _

from mayan.apps.acls.classes import ModelPermission
from mayan.apps.acls.permissions import (
    permission_acl_edit, permission_acl_view
)
from mayan.apps.app_manager.apps import MayanAppConfig
from mayan.apps.events.classes import EventModelRegistry, ModelEventType
from mayan.apps.navigation.menus import Menu

from .events import (
    event_project_created, event_project_edited, event_project_deleted,
    event_study_created, event_study_edited, event_study_deleted,
    event_dataset_created, event_dataset_edited, event_dataset_deleted,
    event_dataset_document_added, event_dataset_document_removed,
    event_dataset_analysis_completed, event_dataset_processed,
    event_dataset_status_changed, event_study_status_changed
)
from .permissions import (
    # Project permissions
    permission_project_view, permission_project_create, 
    permission_project_edit, permission_project_delete,
    # Study permissions
    permission_study_view, permission_study_create,
    permission_study_edit, permission_study_delete,
    # Dataset permissions  
    permission_dataset_view, permission_dataset_create,
    permission_dataset_edit, permission_dataset_delete,
    # Document-dataset relationship permissions
    permission_dataset_document_add, permission_dataset_document_remove,
    # Analysis permissions
    permission_dataset_analyze, permission_dataset_process,
    permission_dataset_export, permission_dataset_preview,
    # Sharing permissions
    permission_project_share, permission_dataset_share,
    permission_project_statistics
)


class ResearchApp(MayanAppConfig):
    app_namespace = 'research'
    app_url = 'research'
    has_rest_api = True
    has_tests = True
    name = 'mayan.apps.research'
    verbose_name = _('Research')

    def ready(self):
        super().ready()
        
        # Import models here to avoid circular imports
        Project = self.get_model('Project')
        Study = self.get_model('Study') 
        Dataset = self.get_model('Dataset')
        DatasetDocument = self.get_model('DatasetDocument')
        
        # Import links here to avoid circular imports
        from .links import (
            link_project_list, link_project_create, link_project_detail,
            link_project_edit, link_project_delete, link_study_list,
            link_study_create, link_study_detail, link_study_edit,
            link_study_delete, link_dataset_list, link_dataset_create,
            link_dataset_detail, link_dataset_edit, link_dataset_delete,
            link_dataset_analysis, link_dataset_documents
        )
        
        # Import menus here
        from mayan.apps.navigation.menus import Menu, menu_main, menu_object, menu_secondary
        
        # Register models for events
        EventModelRegistry.register(model=Project)
        EventModelRegistry.register(model=Study)
        EventModelRegistry.register(model=Dataset)
        EventModelRegistry.register(model=DatasetDocument)
        
        # Register event types for models
        ModelEventType.register(
            model=Project, event_types=(
                event_project_created, event_project_edited, 
                event_project_deleted
            )
        )
        
        ModelEventType.register(
            model=Study, event_types=(
                event_study_created, event_study_edited,
                event_study_deleted, event_study_status_changed
            )
        )
        
        ModelEventType.register(
            model=Dataset, event_types=(
                event_dataset_created, event_dataset_edited,
                event_dataset_deleted, event_dataset_status_changed,
                event_dataset_analysis_completed, event_dataset_processed
            )
        )
        
        ModelEventType.register(
            model=DatasetDocument, event_types=(
                event_dataset_document_added, event_dataset_document_removed
            )
        )
        
        # Register permissions for models
        ModelPermission.register(
            model=Project, permissions=(
                permission_acl_edit, permission_acl_view,
                permission_project_view, permission_project_create,
                permission_project_edit, permission_project_delete,
                permission_project_share, permission_project_statistics
            )
        )
        
        ModelPermission.register(
            model=Study, permissions=(
                permission_acl_edit, permission_acl_view,
                permission_study_view, permission_study_create,
                permission_study_edit, permission_study_delete
            )
        )
        
        ModelPermission.register(
            model=Dataset, permissions=(
                permission_acl_edit, permission_acl_view,
                permission_dataset_view, permission_dataset_create,
                permission_dataset_edit, permission_dataset_delete,
                permission_dataset_analyze, permission_dataset_process,
                permission_dataset_export, permission_dataset_preview,
                permission_dataset_share, permission_dataset_document_add,
                permission_dataset_document_remove
            )
        )
        
        # Set up permission inheritance
        # Studies inherit permissions from their parent project
        ModelPermission.register_inheritance(
            model=Study, related='project'
        )
        
        # Datasets inherit permissions from their parent study's project
        ModelPermission.register_inheritance(
            model=Dataset, related='study__project'
        )
        
        # DatasetDocument inherits from dataset
        ModelPermission.register_inheritance(
            model=DatasetDocument, related='dataset'
        )
        
        # Create research menu and bind to main menu
        menu_research = Menu(name='research', label=_('Research'))
        
        # Bind research menu to main navigation
        menu_main.bind_links(
            links=(menu_research,), position=25
        )
        
        # Bind main research links to research menu
        menu_research.bind_links(
            links=(link_project_list, link_project_create)
        )
        
        # Bind object-specific links
        menu_object.bind_links(
            links=(
                link_project_detail, link_project_edit, link_project_delete,
                link_study_list
            ), sources=(Project,)
        )
        
        menu_object.bind_links(
            links=(
                link_study_detail, link_study_edit, link_study_delete,
                link_dataset_list
            ), sources=(Study,)
        )
        
        menu_object.bind_links(
            links=(
                link_dataset_detail, link_dataset_edit, link_dataset_delete,
                link_dataset_analysis, link_dataset_documents
            ), sources=(Dataset,)
        )
        
        # Bind secondary action links for list views
        menu_secondary.bind_links(
            links=(link_project_create,),
            sources=('research:project_list',)
        )
        
        menu_secondary.bind_links(
            links=(link_study_create,),
            sources=('research:study_list',)
        )
        
        menu_secondary.bind_links(
            links=(link_dataset_create,),
            sources=('research:dataset_list',)
        ) 