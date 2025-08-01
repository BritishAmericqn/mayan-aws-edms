from django.contrib import messages
from django.utils.translation import gettext_lazy as _, ngettext

from mayan.apps.views.generics import (
    ConfirmView, MultipleObjectConfirmActionView, SingleObjectDetailView,
    SingleObjectListView
)
from mayan.apps.views.view_mixins import (
    ContentTypeViewMixin, ExternalObjectViewMixin
)

from .forms import CacheDetailForm, CachePartitionDetailForm
from .icons import (
    icon_cache_detail, icon_cache_list, icon_cache_partition_detail,
    icon_cache_partition_purge, icon_cache_purge_multiple
)
from .models import Cache, CachePartition
from .permissions import (
    permission_cache_partition_purge, permission_cache_purge,
    permission_cache_view
)

from .tasks import task_cache_partition_purge, task_cache_purge


class CacheDetailView(SingleObjectDetailView):
    form_class = CacheDetailForm
    model = Cache
    object_permission = permission_cache_view
    pk_url_kwarg = 'cache_id'
    view_icon = icon_cache_detail

    def get_extra_context(self):
        return {
            'object': self.object,
            'title': _(message='Details of cache: %s') % self.object
        }


class CacheListView(SingleObjectListView):
    model = Cache
    object_permission = permission_cache_view
    view_icon = icon_cache_list

    def get_extra_context(self):
        return {
            'hide_object': True,
            'title': _(message='File caches list')
        }


class CachePartitionDetailView(SingleObjectDetailView):
    form_class = CachePartitionDetailForm
    form_extra_kwargs = {
        'extra_fields': [
            {
                'field': 'get_total_size_display'
            }
        ]
    }
    model = CachePartition
    object_permission = permission_cache_view
    pk_url_kwarg = 'cache_partition_id'
    view_icon = icon_cache_partition_detail

    def get_extra_context(self):
        return {
            'object': self.object,
            'title': _(message='Details of cache partition: %s') % self.object
        }


class CachePartitionPurgeView(
    ContentTypeViewMixin, ExternalObjectViewMixin, ConfirmView
):
    external_object_permission = permission_cache_partition_purge
    external_object_pk_url_kwarg = 'object_id'
    view_icon = icon_cache_partition_purge

    def get_external_object_queryset(self):
        return self.get_content_type().get_all_objects_for_this_type()

    def get_extra_context(self):
        return {
            'object': self.external_object,
            'title': _(
                message='Purge cache partitions of "%s"?'
            ) % self.external_object
        }

    def view_action(self, form=None):
        for cache_partition in self.external_object.get_cache_partitions():
            task_cache_partition_purge.apply_async(
                kwargs={
                    'content_type_id': self.get_content_type().pk,
                    'cache_partition_id': cache_partition.pk,
                    'object_id': self.external_object.pk,
                    'user_id': self.request.user.pk
                }
            )

        messages.success(
            message=_(
                message='Object cache partitions submitted for purging.'
            ), request=self.request
        )


class CachePurgeView(MultipleObjectConfirmActionView):
    model = Cache
    object_permission = permission_cache_purge
    pk_url_kwarg = 'cache_id'
    success_message_plural = _(
        message='%(count)d caches submitted for purging.'
    )
    success_message_singular = _(
        message='%(count)d cache submitted for purging.'
    )
    view_icon = icon_cache_purge_multiple

    def get_extra_context(self):
        queryset = self.object_list

        result = {
            'title': ngettext(
                singular='Submit the selected cache for purging?',
                plural='Submit the selected caches for purging?',
                number=queryset.count()
            )
        }

        if queryset.count() == 1:
            result['object'] = queryset.first()

        return result

    def object_action(self, form, instance):
        task_cache_purge.apply_async(
            kwargs={'cache_id': instance.pk, 'user_id': self.request.user.pk}
        )
