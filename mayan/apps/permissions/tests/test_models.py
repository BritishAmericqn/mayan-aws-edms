from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied

from mayan.apps.testing.tests.base import BaseTestCase
from mayan.apps.user_management.tests.mixins.group_mixins import (
    GroupTestMixin
)

from ..classes import Permission, PermissionNamespace
from ..models import StoredPermission

from .literals import (
    TEST_INVALID_PERMISSION_NAME, TEST_INVALID_PERMISSION_NAMESPACE_NAME,
    TEST_PERMISSION_LABEL, TEST_PERMISSION_NAME,
    TEST_PERMISSION_NAMESPACE_LABEL, TEST_PERMISSION_NAMESPACE_NAME
)
from .mixins import RoleTestMixin


class PermissionTestCase(GroupTestMixin, RoleTestMixin, BaseTestCase):
    def setUp(self):
        super().setUp()
        self._create_test_user()
        self._create_test_group()
        self._create_test_role()
        self._create_test_permission()

    def test_no_permission(self):
        with self.assertRaises(expected_exception=PermissionDenied):
            Permission.check_user_permission(
                permission=self._test_permission, user=self._test_user
            )

    def test_with_permissions(self):
        self._test_group.user_set.add(self._test_user)
        self._test_role.grant(permission=self._test_permission)
        self._test_role.groups.add(self._test_group)

        try:
            Permission.check_user_permission(
                permission=self._test_permission, user=self._test_user
            )
        except PermissionDenied:
            self.fail('PermissionDenied exception was not expected.')

    def test_anonymous_user_permissions(self):
        self.auto_login_user = False
        test_anonymous_user = AnonymousUser()

        with self.assertRaises(expected_exception=PermissionDenied):
            Permission.check_user_permission(
                permission=self._test_permission, user=test_anonymous_user
            )


class RoleModelTestCase(RoleTestMixin, BaseTestCase):
    def test_method_get_absolute_url(self):
        self._create_test_role()

        self.assertTrue(
            self._test_role.get_absolute_url()
        )


class StoredPermissionManagerTestCase(BaseTestCase):
    create_test_case_super_user = False
    create_test_case_user = False

    def test_purge_obsolete_with_invalid(self):
        StoredPermission.objects.create(
            namespace=TEST_INVALID_PERMISSION_NAMESPACE_NAME,
            name=TEST_INVALID_PERMISSION_NAME
        )

        permission_count = StoredPermission.objects.count()

        StoredPermission.objects.purge_obsolete()

        self.assertEqual(
            StoredPermission.objects.count(), permission_count - 1
        )

    def test_purge_obsolete_with_valid(self):
        test_permission_namespace = PermissionNamespace(
            label=TEST_PERMISSION_NAMESPACE_LABEL,
            name=TEST_PERMISSION_NAMESPACE_NAME
        )
        test_permission = test_permission_namespace.add_permission(
            label=TEST_PERMISSION_LABEL, name=TEST_PERMISSION_NAME
        )
        test_permission.stored_permission

        permission_count = StoredPermission.objects.count()

        StoredPermission.objects.purge_obsolete()

        self.assertEqual(
            StoredPermission.objects.count(), permission_count
        )
