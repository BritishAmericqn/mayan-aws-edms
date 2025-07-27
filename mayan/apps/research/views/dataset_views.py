from django.template import RequestContext
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from mayan.apps.views.generics import (
    SingleObjectCreateView, SingleObjectDeleteView, SingleObjectDetailView,
    SingleObjectEditView, SingleObjectListView
)
from mayan.apps.views.view_mixins import ExternalObjectViewMixin

from ..forms import DatasetForm
from ..icons import (
    icon_dataset_create, icon_dataset_delete, icon_dataset_detail,
    icon_dataset_edit, icon_dataset_list
)
from ..links import link_dataset_create
from ..models import Dataset, Study
from ..permissions import (
    permission_dataset_create, permission_dataset_delete,
    permission_dataset_edit, permission_dataset_view, permission_study_view
)


class DatasetListView(ExternalObjectViewMixin, SingleObjectListView):
    external_object_class = Study
    external_object_permission = permission_study_view
    external_object_pk_url_kwarg = 'study_id'
    object_permission = permission_dataset_view
    view_icon = icon_dataset_list

    def get_extra_context(self):
        return {
            'hide_link': True,
            'hide_object': True,
            'no_results_icon': icon_dataset_list,
            'no_results_main_link': link_dataset_create.resolve(
                context=RequestContext(
                    dict_={'study': self.external_object},
                    request=self.request
                )
            ),
            'no_results_text': _(
                'Datasets contain documents and data files for analysis. '
                'Upload CSV files, research papers, and other documents '
                'to organize and analyze your research data.'
            ),
            'no_results_title': _('No datasets available in this study'),
            'object': self.external_object,
            'study': self.external_object,
            'project': self.external_object.project,
            'title': _('Datasets in study: %s') % self.external_object.title
        }

    def get_source_queryset(self):
        return self.external_object.datasets.all()


class DatasetDetailView(SingleObjectDetailView):
    model = Dataset
    object_permission = permission_dataset_view
    pk_url_kwarg = 'dataset_id'
    template_name = 'research/dataset_detail.html'
    view_icon = icon_dataset_detail

    def get_extra_context(self):
        return {
            'object': self.object,
            'dataset': self.object,
            'study': self.object.study,
            'project': self.object.study.project,
            'title': _('Dataset: %s') % self.object.title,
            'hide_object': True,
            'list_as_items': True
        }


class DatasetCreateView(ExternalObjectViewMixin, SingleObjectCreateView):
    external_object_class = Study
    external_object_permission = permission_study_view
    external_object_pk_url_kwarg = 'study_id'
    form_class = DatasetForm
    model = Dataset
    view_icon = icon_dataset_create
    view_permission = permission_dataset_create

    def get_extra_context(self):
        return {
            'object': self.external_object,
            'title': _('Create dataset in study: %s') % self.external_object.title
        }

    def get_form_extra_kwargs(self):
        return {
            'study': self.external_object
        }

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
            'study': self.external_object
        }

    def get_post_action_redirect(self):
        return reverse_lazy(
            viewname='research:dataset_list',
            kwargs={'study_id': self.external_object.pk}
        )


class DatasetEditView(SingleObjectEditView):
    form_class = DatasetForm
    model = Dataset
    object_permission = permission_dataset_edit
    pk_url_kwarg = 'dataset_id'
    view_icon = icon_dataset_edit

    def get_extra_context(self):
        return {
            'object': self.object,
            'title': _('Edit dataset: %s') % self.object.name
        }

    def get_form_extra_kwargs(self):
        return {
            'study': self.object.study
        }

    def get_instance_extra_data(self):
        return {'_event_actor': self.request.user}

    def get_post_action_redirect(self):
        return reverse_lazy(
            viewname='research:dataset_list',
            kwargs={'study_id': self.object.study.pk}
        )


class DatasetDeleteView(SingleObjectDeleteView):
    model = Dataset
    object_permission = permission_dataset_delete
    pk_url_kwarg = 'dataset_id'
    view_icon = icon_dataset_delete

    def get_extra_context(self):
        return {
            'object': self.object,
            'title': _('Delete dataset: %s') % self.object.name
        }

    def get_post_action_redirect(self):
        return reverse_lazy(
            viewname='research:dataset_list',
            kwargs={'study_id': self.object.study.pk}
        ) 