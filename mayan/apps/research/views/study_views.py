from django.template import RequestContext
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from mayan.apps.views.generics import (
    SingleObjectCreateView, SingleObjectDeleteView, SingleObjectDetailView,
    SingleObjectEditView, SingleObjectListView
)
from mayan.apps.views.view_mixins import ExternalObjectViewMixin

from ..forms import StudyForm
from ..icons import (
    icon_study_create, icon_study_delete, icon_study_detail,
    icon_study_edit, icon_study_list
)
from ..links import link_dataset_create, link_study_create
from ..models import Project, Study
from ..permissions import (
    permission_study_create, permission_study_delete,
    permission_study_edit, permission_study_view, permission_project_view
)


class StudyListView(ExternalObjectViewMixin, SingleObjectListView):
    external_object_class = Project
    external_object_permission = permission_project_view
    external_object_pk_url_kwarg = 'project_id'
    object_permission = permission_study_view
    view_icon = icon_study_list

    def get_extra_context(self):
        return {
            'hide_link': True,
            'hide_object': True,
            'no_results_icon': icon_study_list,
            'no_results_main_link': link_study_create.resolve(
                context=RequestContext(
                    dict_={'project': self.external_object},
                    request=self.request
                )
            ),
            'no_results_text': _(
                'Studies organize datasets within a research project. '
                'Create studies to group related datasets and track '
                'specific research activities within the project.'
            ),
            'no_results_title': _('No studies available in this project'),
            'object': self.external_object,
            'title': _('Studies in project: %s') % self.external_object.title
        }

    def get_source_queryset(self):
        return self.external_object.studies.all()


class StudyDetailView(SingleObjectDetailView):
    model = Study
    object_permission = permission_study_view
    pk_url_kwarg = 'study_id'
    template_name = 'research/study_detail.html'
    view_icon = icon_study_detail

    def get_extra_context(self):
        return {
            'object': self.object,
            'study': self.object,
            'project': self.object.project,
            'title': _('Study: %s') % self.object.title,
            'no_results_icon': icon_study_detail,
            'no_results_main_link': link_dataset_create.resolve(
                context=RequestContext(
                    dict_={'study': self.object},
                    request=self.request
                )
            ),
            'no_results_text': _(
                'Datasets contain documents and data files for analysis. '
                'Create datasets to organize and analyze research data '
                'within this study.'
            ),
            'no_results_title': _('This study has no datasets yet')
        }


class StudyCreateView(ExternalObjectViewMixin, SingleObjectCreateView):
    external_object_class = Project
    external_object_permission = permission_project_view
    external_object_pk_url_kwarg = 'project_id'
    form_class = StudyForm
    model = Study
    view_icon = icon_study_create
    view_permission = permission_study_create

    def get_extra_context(self):
        return {
            'object': self.external_object,
            'title': _('Create study in project: %s') % self.external_object.title
        }

    def get_form_extra_kwargs(self):
        return {
            'project': self.external_object
        }

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
            'project': self.external_object
        }

    def get_post_action_redirect(self):
        return reverse_lazy(
            viewname='research:study_list',
            kwargs={'project_id': self.external_object.pk}
        )


class StudyEditView(SingleObjectEditView):
    form_class = StudyForm
    model = Study
    object_permission = permission_study_edit
    pk_url_kwarg = 'study_id'
    view_icon = icon_study_edit

    def get_extra_context(self):
        return {
            'object': self.object,
            'title': _('Edit study: %s') % self.object.title
        }

    def get_form_extra_kwargs(self):
        return {
            'project': self.object.project
        }

    def get_instance_extra_data(self):
        return {'_event_actor': self.request.user}

    def get_post_action_redirect(self):
        return reverse_lazy(
            viewname='research:study_list',
            kwargs={'project_id': self.object.project.pk}
        )


class StudyDeleteView(SingleObjectDeleteView):
    model = Study
    object_permission = permission_study_delete
    pk_url_kwarg = 'study_id'
    view_icon = icon_study_delete

    def get_extra_context(self):
        return {
            'object': self.object,
            'title': _('Delete study: %s') % self.object.title
        }

    def get_post_action_redirect(self):
        return reverse_lazy(
            viewname='research:study_list',
            kwargs={'project_id': self.object.project.pk}
        ) 