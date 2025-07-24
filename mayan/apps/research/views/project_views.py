from django.template import RequestContext
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from mayan.apps.views.generics import (
    SingleObjectCreateView, SingleObjectDeleteView, SingleObjectDetailView,
    SingleObjectEditView, SingleObjectListView
)

from ..forms import ProjectForm
from ..icons import (
    icon_project_create, icon_project_delete, icon_project_detail,
    icon_project_edit, icon_project_list
)
from ..links import link_project_create, link_study_create
from ..models import Project
from ..permissions import (
    permission_project_create, permission_project_delete,
    permission_project_edit, permission_project_view
)


class ProjectListView(SingleObjectListView):
    model = Project
    object_permission = permission_project_view
    view_icon = icon_project_list

    def get_extra_context(self):
        return {
            'hide_link': True,
            'hide_object': True,
            'no_results_icon': icon_project_list,
            'no_results_main_link': link_project_create.resolve(
                context=RequestContext(request=self.request)
            ),
            'no_results_text': _(
                'Research projects organize studies and datasets. '
                'Create projects to group related research activities, '
                'manage collaborators, and track progress. '
                'Each project can contain multiple studies with their own datasets.'
            ),
            'no_results_title': _('No research projects available'),
            'title': _('Research Projects')
        }

    def get_source_queryset(self):
        return Project.objects.all()


class ProjectDetailView(SingleObjectDetailView):
    model = Project
    object_permission = permission_project_view
    pk_url_kwarg = 'project_id'
    template_name = 'research/project_detail.html'
    view_icon = icon_project_detail

    def get_extra_context(self):
        return {
            'object': self.object,
            'project': self.object,
            'title': _('Project: %s') % self.object.title,
            'no_results_icon': icon_project_detail,
            'no_results_main_link': link_study_create.resolve(
                context=RequestContext(
                    dict_={'project': self.object},
                    request=self.request
                )
            ),
            'no_results_text': _(
                'Studies organize datasets within a research project. '
                'Create studies to group related datasets and documents. '
                'Each study can contain multiple datasets.'
            ),
            'no_results_title': _('This project has no studies yet')
        }


class ProjectCreateView(SingleObjectCreateView):
    form_class = ProjectForm
    model = Project
    post_action_redirect = reverse_lazy(viewname='research:project_list')
    view_icon = icon_project_create
    view_permission = permission_project_create

    def get_extra_context(self):
        return {
            'title': _('Create research project')
        }

    def get_instance_extra_data(self):
        return {'_event_actor': self.request.user}


class ProjectEditView(SingleObjectEditView):
    form_class = ProjectForm
    model = Project
    object_permission = permission_project_edit
    pk_url_kwarg = 'project_id'
    post_action_redirect = reverse_lazy(viewname='research:project_list')
    view_icon = icon_project_edit

    def get_extra_context(self):
        return {
            'object': self.object,
            'title': _('Edit project: %s') % self.object.title
        }

    def get_instance_extra_data(self):
        return {'_event_actor': self.request.user}


class ProjectDeleteView(SingleObjectDeleteView):
    model = Project
    object_permission = permission_project_delete
    pk_url_kwarg = 'project_id'
    post_action_redirect = reverse_lazy(viewname='research:project_list')
    view_icon = icon_project_delete

    def get_extra_context(self):
        return {
            'object': self.object,
            'title': _('Delete project: %s') % self.object.title
        } 