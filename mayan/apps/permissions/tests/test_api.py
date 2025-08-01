from rest_framework import status

from mayan.apps.rest_api.tests.base import BaseAPITestCase
from mayan.apps.user_management.permissions import (
    permission_group_edit, permission_group_view
)
from mayan.apps.user_management.tests.mixins.group_mixins import (
    GroupTestMixin
)

from ..classes import Permission
from ..events import event_role_created, event_role_edited
from ..models import Role
from ..permissions import (
    permission_role_create, permission_role_delete, permission_role_edit,
    permission_role_view
)

from .mixins import (
    PermissionAPIViewTestMixin, RoleAPIViewTestMixin,
    RoleGroupAPIViewTestMixin, RolePermissionAPIViewTestMixin
)


class PermissionAPIViewTestCase(PermissionAPIViewTestMixin, BaseAPITestCase):
    def setUp(self):
        super().setUp()
        Permission.invalidate_cache()

    def test_permissions_list_api_view(self):
        self._clear_events()

        response = self._request_permissions_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)


class RoleAPIViewTestCase(
    GroupTestMixin, RoleAPIViewTestMixin, BaseAPITestCase
):
    def test_role_create_api_view_no_permission(self):
        role_count = Role.objects.count()

        self._clear_events()

        response = self._request_test_role_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(Role.objects.count(), role_count)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_role_create_api_view_with_permission(self):
        self.grant_permission(permission=permission_role_create)

        role_count = Role.objects.count()

        self._clear_events()

        response = self._request_test_role_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(
            Role.objects.count(), role_count + 1
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_role)
        self.assertEqual(events[0].verb, event_role_created.id)

    def test_role_delete_api_view_no_permission(self):
        self._create_test_role()

        role_count = Role.objects.count()

        self._clear_events()

        response = self._request_test_role_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(
            Role.objects.count(), role_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_role_delete_api_view_with_access(self):
        self._create_test_role()

        self.grant_access(
            obj=self._test_role, permission=permission_role_delete
        )

        role_count = Role.objects.count()

        self._clear_events()

        response = self._request_test_role_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(Role.objects.count(), role_count - 1)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_role_edit_api_view_via_patch_no_permission(self):
        self._create_test_role()

        role_label = self._test_role.label

        self._clear_events()

        response = self._request_test_role_edit_api_view(
            request_type='patch'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self._test_role.refresh_from_db()
        self.assertEqual(self._test_role.label, role_label)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_role_edit_api_view_via_patch_with_access(self):
        self._create_test_role()
        self.grant_access(
            obj=self._test_role, permission=permission_role_edit
        )

        role_label = self._test_role.label

        self._clear_events()

        response = self._request_test_role_edit_api_view(
            request_type='patch'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self._test_role.refresh_from_db()
        self.assertNotEqual(self._test_role.label, role_label)

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_role)
        self.assertEqual(events[0].verb, event_role_edited.id)

    def test_role_edit_api_view_via_put_no_permission(self):
        self._create_test_role()

        self._clear_events()

        response = self._request_test_role_edit_api_view(request_type='put')

        role_label = self._test_role.label

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self._test_role.refresh_from_db()
        self.assertEqual(self._test_role.label, role_label)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_role_edit_api_view_via_put_with_access(self):
        self._create_test_role()
        self.grant_access(
            obj=self._test_role, permission=permission_role_edit
        )

        role_label = self._test_role.label

        self._clear_events()

        response = self._request_test_role_edit_api_view(request_type='put')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self._test_role.refresh_from_db()
        self.assertNotEqual(self._test_role.label, role_label)

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_role)
        self.assertEqual(events[0].verb, event_role_edited.id)

    def test_roles_list_api_view_no_permission(self):
        self._create_test_role()

        self._clear_events()

        response = self._request_test_role_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            response.data['count'], 0
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_roles_list_api_view_with_access(self):
        self._create_test_role()
        self.grant_access(
            obj=self._test_role, permission=permission_role_view
        )

        self._clear_events()

        response = self._request_test_role_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['count'], 1
        )
        self.assertEqual(
            response.data['results'][0]['label'], self._test_role.label
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)


class RoleGroupAPIViewTestCase(
    GroupTestMixin, RoleGroupAPIViewTestMixin, BaseAPITestCase
):
    auto_create_role_test_object = True

    def setUp(self):
        super().setUp()
        self._create_test_role()
        self._create_test_group()

    def test_role_group_add_api_view_no_group(self):
        self._clear_events()

        response = self._request_test_role_group_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertFalse(
            self._test_group in self._test_role.groups.all()
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_role_group_add_api_view_with_group_access(self):
        self.grant_access(
            obj=self._test_group, permission=permission_group_edit
        )

        self._clear_events()

        response = self._request_test_role_group_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertFalse(
            self._test_group in self._test_role.groups.all()
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_role_group_add_api_view_with_role_access(self):
        self.grant_access(
            obj=self._test_role, permission=permission_role_edit
        )

        self._clear_events()

        response = self._request_test_role_group_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertFalse(
            self._test_group in self._test_role.groups.all()
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_role_group_add_api_view_with_full_access(self):
        self.grant_access(
            obj=self._test_group, permission=permission_group_edit
        )
        self.grant_access(
            obj=self._test_role, permission=permission_role_edit
        )

        self._clear_events()

        response = self._request_test_role_group_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(
            self._test_group in self._test_role.groups.all()
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, self._test_group)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_role)
        self.assertEqual(events[0].verb, event_role_edited.id)

    def test_role_group_list_api_view_no_group(self):
        self._test_role.groups.add(self._test_group)

        self._clear_events()

        response = self._request_test_role_group_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_role_group_list_api_view_with_group_access(self):
        self._test_role.groups.add(self._test_group)

        self.grant_access(
            obj=self._test_group, permission=permission_group_view
        )

        self._clear_events()

        response = self._request_test_role_group_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_role_group_list_api_view_with_role_access(self):
        self._test_role.groups.add(self._test_group)

        self.grant_access(
            obj=self._test_role, permission=permission_role_view
        )

        self._clear_events()

        response = self._request_test_role_group_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['count'], 0
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_role_group_list_api_view_with_full_access(self):
        self._test_role.groups.add(self._test_group)

        self.grant_access(
            obj=self._test_group, permission=permission_group_view
        )
        self.grant_access(
            obj=self._test_role, permission=permission_role_view
        )

        self._clear_events()

        response = self._request_test_role_group_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['results'][0]['id'],
            self._test_group.pk
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_role_group_remove_api_view_no_group(self):
        self._test_role.groups.add(self._test_group)

        role_group_count = self._test_role.groups.count()

        self._clear_events()

        response = self._request_test_role_group_remove_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(
            self._test_role.groups.count(), role_group_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_role_group_remove_api_view_with_group_access(self):
        self._test_role.groups.add(self._test_group)

        self.grant_access(
            obj=self._test_group, permission=permission_group_edit
        )

        role_group_count = self._test_role.groups.count()

        self._clear_events()

        response = self._request_test_role_group_remove_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(
            self._test_role.groups.count(), role_group_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_role_group_remove_api_view_with_role_access(self):
        self._test_role.groups.add(self._test_group)

        self.grant_access(
            obj=self._test_role, permission=permission_role_edit
        )

        role_group_count = self._test_role.groups.count()

        self._clear_events()

        response = self._request_test_role_group_remove_api_view()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(
            self._test_role.groups.count(), role_group_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_role_group_remove_api_view_with_full_access(self):
        self._test_role.groups.add(self._test_group)

        self.grant_access(
            obj=self._test_group, permission=permission_group_edit
        )
        self.grant_access(
            obj=self._test_role, permission=permission_role_edit
        )

        role_group_count = self._test_role.groups.count()

        self._clear_events()

        response = self._request_test_role_group_remove_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            self._test_role.groups.count(), role_group_count - 1
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, self._test_group)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_role)
        self.assertEqual(events[0].verb, event_role_edited.id)


class RolePermissionAPIViewTestCase(
    RolePermissionAPIViewTestMixin, BaseAPITestCase
):
    auto_create_role_test_object = True

    def setUp(self):
        super().setUp()
        self._create_test_role()
        self._create_test_permission()

    def test_role_permission_add_api_view_no_permission(self):
        self._clear_events()

        response = self._request_test_role_permission_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertFalse(
            self._test_permission.stored_permission in self._test_role.permissions.all()
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_role_permission_add_api_view_with_access(self):
        self.grant_access(
            obj=self._test_role, permission=permission_role_edit
        )

        self._clear_events()

        response = self._request_test_role_permission_add_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(
            self._test_permission.stored_permission in self._test_role.permissions.all()
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(
            events[0].action_object, self._test_permission.stored_permission
        )
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_role)
        self.assertEqual(events[0].verb, event_role_edited.id)

    def test_role_permission_list_api_view_no_permission(self):
        self._test_role.permissions.add(
            self._test_permission.stored_permission
        )

        self._clear_events()

        response = self._request_test_role_permission_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_role_permission_list_api_view_with_access(self):
        self._test_role.permissions.add(
            self._test_permission.stored_permission
        )

        self.grant_access(
            obj=self._test_role, permission=permission_role_view
        )

        self._clear_events()

        response = self._request_test_role_permission_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['results'][0]['pk'],
            self._test_permission.pk
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_role_permission_remove_api_view_no_permission(self):
        self._test_role.permissions.add(
            self._test_permission.stored_permission
        )

        role_permission_count = self._test_role.permissions.count()

        self._clear_events()

        response = self._request_test_role_permission_remove_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(
            self._test_role.permissions.count(), role_permission_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_role_permission_remove_api_view_with_access(self):
        self._test_role.permissions.add(
            self._test_permission.stored_permission
        )

        self.grant_access(
            obj=self._test_role, permission=permission_role_edit
        )

        role_permission_count = self._test_role.permissions.count()

        self._clear_events()

        response = self._request_test_role_permission_remove_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            self._test_role.permissions.count(), role_permission_count - 1
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(
            events[0].action_object, self._test_permission.stored_permission
        )
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_role)
        self.assertEqual(events[0].verb, event_role_edited.id)
