from django.utils.translation import gettext_lazy as _

from mayan.apps.navigation.links import Link

from .icons import (
    icon_project_list, icon_project_create, icon_project_detail,
    icon_project_edit, icon_project_delete,
    icon_study_list, icon_study_create, icon_study_detail,
    icon_study_edit, icon_study_delete,
    icon_dataset_list, icon_dataset_create, icon_dataset_detail,
    icon_dataset_edit, icon_dataset_delete, icon_dataset_analysis
)
from .permissions import (
    permission_project_view, permission_project_create, permission_project_edit,
    permission_project_delete, permission_study_view, permission_study_create,
    permission_study_edit, permission_study_delete, permission_dataset_view,
    permission_dataset_create, permission_dataset_edit, permission_dataset_delete,
    permission_dataset_analyze
)

# Project links
link_project_list = Link(
    icon=icon_project_list, text=_('Projects'),
    view='research:project_list', permission=permission_project_view
)

link_project_create = Link(
    icon=icon_project_create, text=_('Create project'),
    view='research:project_create', permission=permission_project_create
)

link_project_detail = Link(
    args=('resolved_object.pk',), icon=icon_project_detail,
    text=_('Details'), view='research:project_detail',
    permission=permission_project_view
)

link_project_edit = Link(
    args=('resolved_object.pk',), icon=icon_project_edit,
    text=_('Edit'), view='research:project_edit',
    permission=permission_project_edit
)

link_project_delete = Link(
    args=('resolved_object.pk',), icon=icon_project_delete,
    text=_('Delete'), view='research:project_delete',
    permission=permission_project_delete, tags='dangerous'
)

# Study links
link_study_list = Link(
    args=('resolved_object.pk',), icon=icon_study_list,
    text=_('Studies'), view='research:study_list',
    permission=permission_study_view
)

link_study_create = Link(
    args=('resolved_object.pk',), icon=icon_study_create,
    text=_('Create study'), view='research:study_create',
    permission=permission_study_create
)

link_study_detail = Link(
    args=('resolved_object.pk',), icon=icon_study_detail,
    text=_('Details'), view='research:study_detail',
    permission=permission_study_view
)

link_study_edit = Link(
    args=('resolved_object.pk',), icon=icon_study_edit,
    text=_('Edit'), view='research:study_edit',
    permission=permission_study_edit
)

link_study_delete = Link(
    args=('resolved_object.pk',), icon=icon_study_delete,
    text=_('Delete'), view='research:study_delete',
    permission=permission_study_delete, tags='dangerous'
)

# Dataset links
link_dataset_list = Link(
    args=('resolved_object.pk',), icon=icon_dataset_list,
    text=_('Datasets'), view='research:dataset_list',
    permission=permission_dataset_view
)

link_dataset_create = Link(
    args=('resolved_object.pk',), icon=icon_dataset_create,
    text=_('Create dataset'), view='research:dataset_create',
    permission=permission_dataset_create
)

link_dataset_detail = Link(
    args=('resolved_object.pk',), icon=icon_dataset_detail,
    text=_('Details'), view='research:dataset_detail',
    permission=permission_dataset_view
)

link_dataset_edit = Link(
    args=('resolved_object.pk',), icon=icon_dataset_edit,
    text=_('Edit'), view='research:dataset_edit',
    permission=permission_dataset_edit
)

link_dataset_delete = Link(
    args=('resolved_object.pk',), icon=icon_dataset_delete,
    text=_('Delete'), view='research:dataset_delete',
    permission=permission_dataset_delete, tags='dangerous'
)

link_dataset_analysis = Link(
    args=('resolved_object.pk',), icon=icon_dataset_analysis,
    text=_('Analysis'), view='research:dataset_analysis',
    permission=permission_dataset_analyze
)

link_dataset_documents = Link(
    args=('resolved_object.pk',), icon=icon_dataset_list,
    text=_('Documents'), view='research:dataset_document_list',
    permission=permission_dataset_view
) 