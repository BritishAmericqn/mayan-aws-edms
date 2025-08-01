from mayan.apps.file_caching.events import event_cache_partition_purged
from mayan.apps.file_caching.models import CachePartitionFile
from mayan.apps.file_caching.permissions import (
    permission_cache_partition_purge
)
from mayan.apps.file_caching.tests.mixins import CachePartitionViewTestMixin

from ..document_file_actions import (
    DocumentFileActionAppendNewPages, DocumentFileActionNothing
)
from ..events import (
    event_document_version_deleted, event_document_version_edited,
    event_document_version_page_created, event_document_version_page_deleted,
    event_document_viewed
)
from ..models.document_version_models import DocumentVersion
from ..permissions import (
    permission_document_version_delete, permission_document_version_edit,
    permission_document_version_print, permission_document_version_view
)

from .base import GenericDocumentViewTestCase
from .mixins.document_file_mixins import DocumentFileTestMixin
from .mixins.document_version_mixins import (
    DocumentVersionModificationViewTestMixin, DocumentVersionTestMixin,
    DocumentVersionViewTestMixin
)


class DocumentVersionListViewTestCase(
    DocumentVersionTestMixin, DocumentVersionViewTestMixin,
    GenericDocumentViewTestCase
):
    def setUp(self):
        super().setUp()

        def get_label(self):
            return 'dv-{}'.format(self.pk)

        self._document_version_get_label = DocumentVersion.get_label

        DocumentVersion.get_label = get_label

    def tearDown(self):
        DocumentVersion.get_label = self._document_version_get_label

        super().tearDown()

    def test_document_version_list_view_no_permission(self):
        self._create_test_document_version()

        self._clear_events()

        response = self._request_test_document_version_list_view()
        self.assertNotContains(
            response=response, status_code=200, text=str(
                self._test_document_version_list[0]
            )
        )
        self.assertNotContains(
            response=response, status_code=200, text=str(
                self._test_document_version_list[1]
            )
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_list_view_with_document_access(self):
        self._create_test_document_version()

        self.grant_access(
            obj=self._test_document,
            permission=permission_document_version_view
        )

        self._clear_events()

        response = self._request_test_document_version_list_view()
        self.assertContains(
            response=response, status_code=200, text=str(
                self._test_document_version_list[0]
            )
        )
        self.assertContains(
            response=response, status_code=200, text=str(
                self._test_document_version_list[1]
            )
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_trashed_document_version_list_view_with_document_access(self):
        self._create_test_document_version()

        self.grant_access(
            obj=self._test_document,
            permission=permission_document_version_view
        )

        self._test_document.delete()
        self._clear_events()

        response = self._request_test_document_version_list_view()
        self.assertEqual(response.status_code, 404)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_list_view_with_document_version_access(self):
        self._create_test_document_version()

        self.grant_access(
            obj=self._test_document_version_list[0],
            permission=permission_document_version_view
        )

        self._clear_events()

        response = self._request_test_document_version_list_view()
        self.assertContains(
            response=response, status_code=200, text=str(
                self._test_document_version_list[0]
            )
        )
        self.assertNotContains(
            response=response, status_code=200, text=str(
                self._test_document_version_list[1]
            )
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)


class DocumentVersionViewTestCase(
    DocumentVersionTestMixin, DocumentVersionViewTestMixin,
    GenericDocumentViewTestCase
):
    def test_document_version_active_view_no_permission(self):
        self._create_test_document_version()

        self._test_document.versions.first().active_set()

        self._clear_events()

        response = self._request_test_document_version_active_view()
        self.assertEqual(response.status_code, 404)

        self._test_document_version.refresh_from_db()
        self.assertFalse(self._test_document_version.active)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_active_view_with_access(self):
        self._create_test_document_version()

        self._test_document.versions.first().active_set()

        self.grant_access(
            obj=self._test_document_version,
            permission=permission_document_version_edit
        )

        self._clear_events()

        response = self._request_test_document_version_active_view()
        self.assertEqual(response.status_code, 302)

        self._test_document_version.refresh_from_db()
        self.assertTrue(self._test_document_version.active)

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, self._test_document)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_document_version)
        self.assertEqual(events[0].verb, event_document_version_edited.id)

    def test_trashed_document_version_active_view_with_access(self):
        self._create_test_document_version()

        self._test_document.versions.first().active_set()

        self.grant_access(
            obj=self._test_document_version,
            permission=permission_document_version_edit
        )

        self._test_document.delete()
        self._clear_events()

        response = self._request_test_document_version_active_view()
        self.assertEqual(response.status_code, 404)

        self._test_document_version.refresh_from_db()
        self.assertFalse(self._test_document_version.active)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_single_delete_view_no_permission(self):
        self._create_test_document_version()

        document_version_count = self._test_document.versions.count()

        self._clear_events()

        response = self._request_test_document_version_single_delete_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            self._test_document.versions.count(), document_version_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_single_delete_view_with_access(self):
        self._create_test_document_version()
        self.grant_access(
            obj=self._test_document_version,
            permission=permission_document_version_delete
        )

        document_version_count = self._test_document.versions.count()

        self._clear_events()

        response = self._request_test_document_version_single_delete_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            self._test_document.versions.count(), document_version_count - 1
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_document)
        self.assertEqual(events[0].verb, event_document_version_deleted.id)

    def test_document_version_multiple_delete_view_no_permission(self):
        self._create_test_document_version()

        document_version_count = self._test_document.versions.count()

        self._clear_events()

        response = self._request_test_document_version_multiple_delete_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            self._test_document.versions.count(), document_version_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_multiple_delete_view_with_access(self):
        self._create_test_document_version()

        document_version_count = self._test_document.versions.count()

        self.grant_access(
            obj=self._test_document_version,
            permission=permission_document_version_delete
        )

        self._clear_events()

        response = self._request_test_document_version_multiple_delete_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            self._test_document.versions.count(), document_version_count - 1
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_document)
        self.assertEqual(events[0].verb, event_document_version_deleted.id)

    def test_document_version_edit_view_no_permission(self):
        document_version_comment = self._test_document_version.comment

        self._clear_events()

        response = self._request_test_document_version_edit_view()
        self.assertEqual(response.status_code, 404)

        self._test_document_version.refresh_from_db()
        self.assertEqual(
            self._test_document_version.comment,
            document_version_comment
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_edit_view_with_access(self):
        self.grant_access(
            obj=self._test_document_version,
            permission=permission_document_version_edit
        )

        document_version_comment = self._test_document_version.comment

        self._clear_events()

        response = self._request_test_document_version_edit_view()
        self.assertEqual(response.status_code, 302)

        self._test_document_version.refresh_from_db()
        self.assertNotEqual(
            self._test_document_version.comment,
            document_version_comment
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, self._test_document)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_document_version)
        self.assertEqual(events[0].verb, event_document_version_edited.id)

    def test_trashed_document_version_edit_view_with_access(self):
        self.grant_access(
            obj=self._test_document_version,
            permission=permission_document_version_edit
        )

        document_version_comment = self._test_document_version.comment

        self._test_document.delete()
        self._clear_events()

        response = self._request_test_document_version_edit_view()
        self.assertEqual(response.status_code, 404)

        self._test_document_version.refresh_from_db()
        self.assertEqual(
            self._test_document_version.comment,
            document_version_comment
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_preview_view_no_permission(self):
        self._clear_events()

        response = self._request_test_document_version_preview_view()
        self.assertEqual(response.status_code, 404)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_preview_view_with_access(self):
        self.grant_access(
            obj=self._test_document_version,
            permission=permission_document_version_view
        )

        self._clear_events()

        response = self._request_test_document_version_preview_view()
        self.assertContains(
            response=response, status_code=200,
            text=str(self._test_document_version)
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, self._test_document_version)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_document)
        self.assertEqual(events[0].verb, event_document_viewed.id)

    def test_trashed_document_version_preview_view_with_access(self):
        self.grant_access(
            obj=self._test_document_version,
            permission=permission_document_version_view
        )

        self._test_document.delete()
        self._clear_events()

        response = self._request_test_document_version_preview_view()
        self.assertEqual(response.status_code, 404)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_print_form_view_no_permission(self):
        self._clear_events()

        response = self._request_test_document_version_print_form_view()
        self.assertEqual(response.status_code, 404)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_print_form_view_with_access(self):
        self.grant_access(
            obj=self._test_document_version,
            permission=permission_document_version_print
        )

        self._clear_events()

        response = self._request_test_document_version_print_form_view()
        self.assertEqual(response.status_code, 200)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_trashed_document_version_print_form_view_with_access(self):
        self.grant_access(
            obj=self._test_document_version,
            permission=permission_document_version_print
        )

        self._test_document.delete()
        self._clear_events()

        response = self._request_test_document_version_print_form_view()
        self.assertEqual(response.status_code, 404)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_print_view_no_permission(self):
        self._clear_events()

        response = self._request_test_document_version_print_view()
        self.assertEqual(response.status_code, 404)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_print_view_with_access(self):
        self.grant_access(
            obj=self._test_document_version,
            permission=permission_document_version_print
        )

        self._clear_events()

        response = self._request_test_document_version_print_view()
        self.assertEqual(response.status_code, 200)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_trashed_document_version_print_view_with_access(self):
        self.grant_access(
            obj=self._test_document_version,
            permission=permission_document_version_print
        )

        self._test_document.delete()
        self._clear_events()

        response = self._request_test_document_version_print_view()
        self.assertEqual(response.status_code, 404)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)


class DocumentVersionCachePurgeViewTestCase(
    CachePartitionViewTestMixin, GenericDocumentViewTestCase
):
    def test_document_version_cache_purge_no_permission(self):
        self._test_object = self._test_document_version
        self._inject_test_object_content_type()

        self._test_document_version.version_pages.first().generate_image()

        test_document_version_cache_partitions = self._test_document_version.get_cache_partitions()

        cache_partition_version_count = CachePartitionFile.objects.filter(
            partition__in=test_document_version_cache_partitions
        ).count()

        self._clear_events()

        response = self._request_test_object_file_cache_partition_purge_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            CachePartitionFile.objects.filter(
                partition__in=test_document_version_cache_partitions
            ).count(), cache_partition_version_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_cache_purge_with_access(self):
        self._test_object = self._test_document_version
        self._inject_test_object_content_type()

        self.grant_access(
            obj=self._test_document_version,
            permission=permission_cache_partition_purge
        )

        self._test_document_version.version_pages.first().generate_image()

        test_document_version_cache_partitions = self._test_document_version.get_cache_partitions()

        cache_partition_version_count = CachePartitionFile.objects.filter(
            partition__in=test_document_version_cache_partitions
        ).count()

        cache_partitions = self._test_document_version.get_cache_partitions()

        self._clear_events()

        response = self._request_test_object_file_cache_partition_purge_view()
        self.assertEqual(response.status_code, 302)

        self.assertNotEqual(
            CachePartitionFile.objects.filter(
                partition__in=test_document_version_cache_partitions
            ).count(), cache_partition_version_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 2)

        self.assertEqual(events[0].action_object, self._test_document_version)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, cache_partitions[0])
        self.assertEqual(events[0].verb, event_cache_partition_purged.id)

        self.assertEqual(events[1].action_object, self._test_document_version)
        self.assertEqual(events[1].actor, self._test_case_user)
        self.assertEqual(events[1].target, cache_partitions[1])
        self.assertEqual(events[1].verb, event_cache_partition_purged.id)


class DocumentVersionModificationViewTestCase(
    DocumentFileTestMixin, DocumentVersionModificationViewTestMixin,
    DocumentVersionTestMixin, GenericDocumentViewTestCase
):
    def test_document_version_action_page_append_view_no_permission(self):
        self._upload_test_document_file(
            action_name=DocumentFileActionNothing.backend_id
        )

        self._clear_events()

        response = self._request_test_document_version_action_page_append_view()
        self.assertEqual(response.status_code, 404)

        self._test_document_version.refresh_from_db()

        self.assertEqual(
            self._test_document_version.pages.count(),
            self._test_document_file_list[0].pages.count()
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_action_page_append_view_with_access(self):
        self._upload_test_document_file(
            action_name=DocumentFileActionNothing.backend_id
        )

        self.grant_access(
            obj=self._test_document_version,
            permission=permission_document_version_edit
        )

        self._clear_events()

        response = self._request_test_document_version_action_page_append_view()
        self.assertEqual(response.status_code, 302)

        self._test_document_version.refresh_from_db()

        self.assertEqual(
            self._test_document_version.pages.count(),
            self._test_document_file_list[0].pages.count() + self._test_document_file_list[1].pages.count()
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 4)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_document_version)
        self.assertEqual(
            events[0].verb, event_document_version_page_deleted.id
        )

        self.assertEqual(events[1].action_object, self._test_document_version)
        self.assertEqual(events[1].actor, self._test_case_user)
        self.assertEqual(
            events[1].target, self._test_document_version.pages[0]
        )
        self.assertEqual(
            events[1].verb, event_document_version_page_created.id
        )

        self.assertEqual(events[2].action_object, self._test_document_version)
        self.assertEqual(events[2].actor, self._test_case_user)
        self.assertEqual(
            events[2].target, self._test_document_version.pages[1]
        )
        self.assertEqual(
            events[2].verb, event_document_version_page_created.id
        )

        self.assertEqual(events[3].action_object, self._test_document)
        self.assertEqual(events[3].actor, self._test_case_user)
        self.assertEqual(events[3].target, self._test_document_version)
        self.assertEqual(events[3].verb, event_document_version_edited.id)

    def test_trashed_document_version_action_page_append_view_with_access(self):
        self._upload_test_document_file(
            action_name=DocumentFileActionNothing.backend_id
        )

        self.grant_access(
            obj=self._test_document_version,
            permission=permission_document_version_edit
        )

        self._test_document.delete()

        self._clear_events()

        response = self._request_test_document_version_action_page_append_view()
        self.assertEqual(response.status_code, 404)

        self._test_document_version.refresh_from_db()

        self.assertEqual(
            self._test_document_version.pages.count(),
            self._test_document_file_list[0].pages.count()
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_action_page_reset_view_no_permission(self):
        self._upload_test_document_file(
            action_name=DocumentFileActionAppendNewPages.backend_id
        )

        self._clear_events()

        response = self._request_test_document_version_action_page_reset_view()
        self.assertEqual(response.status_code, 404)

        self._test_document_version.refresh_from_db()

        self.assertEqual(
            self._test_document_version.pages.count(),
            self._test_document_file_list[0].pages.count() + self._test_document_file_list[1].pages.count()
        )

        self.assertEqual(
            self._test_document_version.pages.all()[0].content_object,
            self._test_document_file_page_list[0]
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_version_action_page_reset_view_with_access(self):
        self._upload_test_document_file(
            action_name=DocumentFileActionAppendNewPages.backend_id
        )

        self.grant_access(
            obj=self._test_document_version,
            permission=permission_document_version_edit
        )

        self._clear_events()

        response = self._request_test_document_version_action_page_reset_view()
        self.assertEqual(response.status_code, 302)

        self._test_document_version.refresh_from_db()

        self.assertEqual(
            self._test_document_version.pages.count(),
            self._test_document_file_list[0].pages.count()
        )

        self.assertEqual(
            self._test_document_version.pages.all()[0].content_object,
            self._test_document_file_page_list[1]
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 4)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_document_version)
        self.assertEqual(
            events[0].verb, event_document_version_page_deleted.id
        )

        self.assertEqual(events[1].action_object, None)
        self.assertEqual(events[1].actor, self._test_case_user)
        self.assertEqual(events[1].target, self._test_document_version)
        self.assertEqual(
            events[1].verb, event_document_version_page_deleted.id
        )

        self.assertEqual(events[2].action_object, self._test_document_version)
        self.assertEqual(events[2].actor, self._test_case_user)
        self.assertEqual(
            events[2].target, self._test_document_version.pages[0]
        )
        self.assertEqual(
            events[2].verb, event_document_version_page_created.id
        )

        self.assertEqual(events[3].action_object, self._test_document)
        self.assertEqual(events[3].actor, self._test_case_user)
        self.assertEqual(events[3].target, self._test_document_version)
        self.assertEqual(events[3].verb, event_document_version_edited.id)

    def test_trashed_document_version_action_page_reset_view_with_access(self):
        self._upload_test_document_file(
            action_name=DocumentFileActionAppendNewPages.backend_id
        )

        self.grant_access(
            obj=self._test_document_version,
            permission=permission_document_version_edit
        )

        self._test_document.delete()

        self._clear_events()

        response = self._request_test_document_version_action_page_reset_view()
        self.assertEqual(response.status_code, 404)

        self._test_document_version.refresh_from_db()

        self.assertEqual(
            self._test_document_version.pages.count(),
            self._test_document_file_list[0].pages.count() + self._test_document_file_list[1].pages.count()
        )

        self.assertEqual(
            self._test_document_version.pages.all()[0].content_object,
            self._test_document_file_page_list[0]
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)
