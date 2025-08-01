from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q

from mayan.apps.permissions.tests.mixins import (
    RoleTestCaseMixin, RoleTestMixin
)
from mayan.apps.user_management.tests.mixins.user_mixins import (
    UserTestCaseMixin
)

from ..classes import ModelPermission
from ..models import AccessControlList
from ..permissions import permission_acl_edit, permission_acl_view


class ACLAPIViewTestMixin:
    def _request_test_acl_create_api_view(self):
        pk_list = list(
            AccessControlList.objects.values_list('pk', flat=True)
        )

        response = self.post(
            viewname='rest_api:accesscontrollist-list',
            kwargs=self._test_object_view_kwargs, data={
                'role_id': self._test_role.pk
            }
        )

        try:
            self._test_acl = AccessControlList.objects.get(
                ~Q(pk__in=pk_list)
            )
        except AccessControlList.DoesNotExist:
            self._test_acl = None

        return response

    def _request_test_acl_delete_api_view(self):
        return self.delete(
            viewname='rest_api:accesscontrollist-detail', kwargs={
                'app_label': self._test_object_content_type.app_label,
                'model_name': self._test_object_content_type.model,
                'object_id': self._test_object.pk,
                'acl_id': self._test_acl.pk
            }
        )

    def _request_test_acl_detail_api_view(self):
        return self.get(
            viewname='rest_api:accesscontrollist-detail', kwargs={
                'app_label': self._test_object_content_type.app_label,
                'model_name': self._test_object_content_type.model,
                'object_id': self._test_object.pk,
                'acl_id': self._test_acl.pk
            }
        )

    def _request_test_acl_list_api_view(self):
        return self.get(
            viewname='rest_api:accesscontrollist-list', kwargs={
                'app_label': self._test_object_content_type.app_label,
                'model_name': self._test_object_content_type.model,
                'object_id': self._test_object.pk
            }
        )

    def _request_test_acl_permission_add_api_view(self):
        return self.post(
            viewname='rest_api:accesscontrollist-permission-add', kwargs={
                'app_label': self._test_object_content_type.app_label,
                'model_name': self._test_object_content_type.model,
                'object_id': self._test_object.pk,
                'acl_id': self._test_acl.pk
            }, data={'permission': self._test_permission.pk}
        )

    def _request_test_acl_permission_list_api_view(self):
        return self.get(
            viewname='rest_api:accesscontrollist-permission-list', kwargs={
                'app_label': self._test_object_content_type.app_label,
                'model_name': self._test_object_content_type.model,
                'object_id': self._test_object.pk,
                'acl_id': self._test_acl.pk
            }
        )

    def _request_test_acl_permission_remove_api_view(self):
        return self.post(
            viewname='rest_api:accesscontrollist-permission-remove', kwargs={
                'app_label': self._test_object_content_type.app_label,
                'model_name': self._test_object_content_type.model,
                'object_id': self._test_object.pk,
                'acl_id': self._test_acl.pk
            }, data={'permission': self._test_permission.pk}
        )

    def _request_test_class_permission_list_api_view(self):
        return self.get(
            viewname='rest_api:class-permission-list', kwargs={
                'app_label': self._test_object_content_type.app_label,
                'model_name': self._test_object_content_type.model
            }
        )


class ACLTestCaseMixin(RoleTestCaseMixin, UserTestCaseMixin):
    def setUp(self):
        super().setUp()
        if hasattr(self, '_test_case_user'):
            self._test_case_role.groups.add(self._test_case_group)

    def grant_access(self, obj, permission):
        if not hasattr(self, '_test_case_role'):
            raise ImproperlyConfigured(
                'Enable the creation of the test case user, group, and role '
                'in order to enable the usage of ACLs in tests.'
            )

        self._test_case_acl = AccessControlList.objects.grant(
            obj=obj, permission=permission, role=self._test_case_role
        )

    def revoke_access(self, obj, permission):
        self._test_case_acl = AccessControlList.objects.revoke(
            obj=obj, permission=permission, role=self._test_case_role
        )


class ACLTestMixin(RoleTestMixin):
    auto_create_test_role = True
    auto_create_acl_test_object = False

    def setUp(self):
        super().setUp()
        if self.auto_create_test_role:
            self._create_test_role()

        if self.auto_create_acl_test_object:
            self._create_acl_test_object()

    def _create_test_acl(self):
        self._test_acl = AccessControlList.objects.create(
            content_object=self._test_object, role=self._test_role
        )

    def _create_acl_test_object(
        self, model_name=None, create_test_permission=True,
        register_acl_permissions=True, register_test_permission=True
    ):
        self._create_test_model()

        if create_test_permission:
            self._create_test_permission()

        if register_acl_permissions or 1:
            ModelPermission.register(
                model=self._test_model_dict['_TestModel_0'], permissions=(
                    permission_acl_edit, permission_acl_view
                )
            )

        if register_test_permission or 1:
            ModelPermission.register(
                model=self._test_model_dict['_TestModel_0'], permissions=(
                    self._test_permission,
                )
            )

        self._create_test_object()

    def _create_acl_test_object_base(self):
        self._test_object_base = self._create_acl_test_object(
            model_name='TestModelBase'
        )

    def _create_acl_test_object_proxy(self):
        self._create_test_model(
            base_class=self._test_model_dict['_TestModel_0'],
            model_name='TestModelProxy', options={'proxy': True}
        )
        self._test_object_proxy = self._test_model_dict['TestModelProxy'].objects.create()


class AccessControlListViewTestMixin:
    def _request_test_acl_create_get_view(self):
        return self.get(
            viewname='acls:acl_create',
            kwargs=self._test_object_view_kwargs, data={
                'role': self._test_role.pk
            }
        )

    def _request_test_acl_create_post_view(self):
        pk_list = list(
            AccessControlList.objects.values_list('pk', flat=True)
        )

        response = self.post(
            viewname='acls:acl_create',
            kwargs=self._test_object_view_kwargs, data={
                'role': self._test_role.pk
            }
        )

        try:
            self._test_acl = AccessControlList.objects.get(
                ~Q(pk__in=pk_list)
            )
        except AccessControlList.DoesNotExist:
            self._test_acl = None

        return response

    def _request_test_acl_delete_view(self):
        return self.post(
            viewname='acls:acl_delete', kwargs={'acl_id': self._test_acl.pk}
        )

    def _request_test_acl_list_view(self):
        return self.get(
            viewname='acls:acl_list',
            kwargs=self._test_object_view_kwargs
        )

    def _request_test_acl_permission_list_get_view(self):
        return self.get(
            viewname='acls:acl_permissions', kwargs={
                'acl_id': self._test_acl.pk
            }

        )

    def _request_test_acl_permission_add_view(self):
        return self.post(
            viewname='acls:acl_permissions', kwargs={
                'acl_id': self._test_acl.pk
            }, data={
                'available-submit': 'true',
                'available-selection': self._test_permission.stored_permission.pk
            }
        )

    def _request_test_acl_permission_remove_view(self):
        return self.post(
            viewname='acls:acl_permissions', kwargs={
                'acl_id': self._test_acl.pk
            }, data={
                'added-submit': 'true',
                'added-selection': self._test_permission.stored_permission.pk
            }
        )

    def _request_test_global_acl_list_view(self):
        return self.get(
            viewname='acls:global_acl_list',
        )
