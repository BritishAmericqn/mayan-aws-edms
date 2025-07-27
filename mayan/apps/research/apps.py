"""
Research App Configuration.
Simplified version for reliable startup and analysis functionality.
"""
from mayan.apps.common.apps import MayanAppConfig


class ResearchApp(MayanAppConfig):
    app_namespace = 'research'
    app_url = 'research'
    has_rest_api = True
    has_static_media = True
    name = 'mayan.apps.research'
    verbose_name = 'Research Platform'

    def ready(self):
        super().ready()

        # Add shared URLs to public access (bypass authentication)
        from django.conf import settings
        if hasattr(settings, 'STRONGHOLD_PUBLIC_URLS'):
            settings.STRONGHOLD_PUBLIC_URLS += (
                r'^/test-public/$',
                r'^/shared/[0-9a-f-]+/$',
                r'^/shared/[0-9a-f-]+/download/$', 
                r'^/shared/[0-9a-f-]+/preview/$',
            )

        # Simple permission registration only - avoid complex event system
        try:
            from .models import Dataset, DatasetDocument, Project, Study
            from mayan.apps.acls.classes import ModelPermission
            from .permissions import (
                permission_project_create,
                permission_project_delete,
                permission_project_edit,
                permission_project_view,
                permission_study_create,
                permission_study_delete,
                permission_study_edit,
                permission_study_view,
                permission_dataset_create,
                permission_dataset_delete,
                permission_dataset_edit,
                permission_dataset_view,
                permission_dataset_analyze
            )

            # Register basic permissions for models
            ModelPermission.register(
                model=Project, permissions=(
                    permission_project_create,
                    permission_project_delete,
                    permission_project_edit,
                    permission_project_view,
                )
            )

            ModelPermission.register(
                model=Study, permissions=(
                    permission_study_create,
                    permission_study_delete,
                    permission_study_edit,
                    permission_study_view,
                ), related='project'
            )

            ModelPermission.register(
                model=Dataset, permissions=(
                    permission_dataset_create,
                    permission_dataset_delete,
                    permission_dataset_edit,
                    permission_dataset_view,
                    permission_dataset_analyze,
                ), related='study__project'
            )

        except Exception as e:
            # Log error but don't fail - allow app to start
            import logging
            logger = logging.getLogger(name=__name__)
            logger.warning(f"Research app permissions setup warning: {e}")
            pass

    # Removed custom configure_urls method - using parent MayanAppConfig implementation
    # which will automatically import from urls.py and register with namespace 