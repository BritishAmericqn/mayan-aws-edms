from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db import models

from mayan.apps.events.classes import EventModelRegistry
from mayan.apps.testing.tests.base import BaseTestCase

from ..classes import ModelPermission
from ..models import AccessControlList

from .mixins import ACLTestMixin


class PermissionTestCase(ACLTestMixin, BaseTestCase):
    auto_create_acl_test_object = False

    def test_check_access_without_permission(self):
        self._create_acl_test_object()

        with self.assertRaises(expected_exception=PermissionDenied):
            AccessControlList.objects.check_access(
                obj=self._test_object,
                permission=self._test_permission,
                user=self._test_case_user,
            )

    def test_filtering_without_permission(self):
        self._create_acl_test_object()

        queryset = self._test_object._meta.model._default_manager.all()

        self.assertEqual(
            AccessControlList.objects.restrict_queryset(
                permission=self._test_permission, queryset=queryset,
                user=self._test_case_user
            ).count(), 0
        )

    def test_check_access_with_acl(self):
        self._create_acl_test_object()

        self.grant_access(
            obj=self._test_object, permission=self._test_permission
        )

        try:
            AccessControlList.objects.check_access(
                obj=self._test_object, permission=self._test_permission,
                user=self._test_case_user,
            )
        except PermissionDenied:
            self.fail('PermissionDenied exception was not expected.')

    def test_filtering_with_permission(self):
        self._create_acl_test_object()

        self.grant_access(
            obj=self._test_object, permission=self._test_permission
        )

        queryset = self._test_object._meta.model._default_manager.all()

        self.assertTrue(
            self._test_object in AccessControlList.objects.restrict_queryset(
                permission=self._test_permission, queryset=queryset,
                user=self._test_case_user
            )
        )

    def _setup_child_parent_test_objects(self):
        self._create_test_permission()
        self._create_test_model(model_name='TestModelParent')
        self._create_test_model(
            fields={
                'parent': models.ForeignKey(
                    on_delete=models.CASCADE, related_name='children',
                    to='TestModelParent'
                )
            }, model_name='TestModelChild'
        )

        ModelPermission.register(
            model=self._test_model_dict['TestModelParent'], permissions=(
                self._test_permission,
            )
        )
        ModelPermission.register(
            model=self._test_model_dict['TestModelChild'], permissions=(
                self._test_permission,
            )
        )
        ModelPermission.register_inheritance(
            model=self._test_model_dict['TestModelChild'], related='parent'
        )

        self._test_object_parent = self._test_model_dict['TestModelParent'].objects.create()
        self._test_object_child = self._test_model_dict['TestModelChild'].objects.create(
            parent=self._test_object_parent
        )

    def test_check_access_with_inherited_acl(self):
        self._setup_child_parent_test_objects()

        self.grant_access(
            obj=self._test_object_parent, permission=self._test_permission
        )

        try:
            AccessControlList.objects.check_access(
                obj=self._test_object_child,
                permission=self._test_permission, user=self._test_case_user
            )
        except PermissionDenied:
            self.fail('PermissionDenied exception was not expected.')

    def test_check_access_with_inherited_acl_and_local_acl(self):
        self._setup_child_parent_test_objects()

        self.grant_access(
            obj=self._test_object_parent, permission=self._test_permission
        )
        self.grant_access(
            obj=self._test_object_child, permission=self._test_permission
        )

        try:
            AccessControlList.objects.check_access(
                obj=self._test_object_child,
                permission=self._test_permission, user=self._test_case_user
            )
        except PermissionDenied:
            self.fail('PermissionDenied exception was not expected.')

    def test_filtering_with_inherited_permissions(self):
        self._setup_child_parent_test_objects()

        self.grant_access(
            obj=self._test_object_parent, permission=self._test_permission
        )

        result = AccessControlList.objects.restrict_queryset(
            permission=self._test_permission,
            queryset=self._test_object_child._meta.model._default_manager.all(),
            user=self._test_case_user
        )
        self.assertTrue(self._test_object_child in result)

    def test_filtering_with_inherited_permissions_and_local_acl(self):
        self._setup_child_parent_test_objects()

        self.grant_permission(permission=self._test_permission)
        self.grant_access(
            obj=self._test_object_parent, permission=self._test_permission
        )
        self.grant_access(
            obj=self._test_object_child, permission=self._test_permission
        )

        result = AccessControlList.objects.restrict_queryset(
            permission=self._test_permission,
            queryset=self._test_object_child._meta.model._default_manager.all(),
            user=self._test_case_user,
        )
        self.assertTrue(self._test_object_child in result)

    def test_method_get_absolute_url(self):
        self._create_acl_test_object()
        self._create_test_acl()

        self.assertTrue(
            self._test_acl.get_absolute_url()
        )


class InheritedPermissionTestCase(ACLTestMixin, BaseTestCase):
    def test_retrieve_inherited_role_permission_not_model_applicable(self):
        self._create_test_model()
        EventModelRegistry.register(model=self._test_model_dict['_TestModel_0'])
        self._test_object = self._test_model_dict['_TestModel_0'].objects.create()
        self._create_test_acl()
        self._create_test_permission()

        self._test_role.grant(permission=self._test_permission)

        queryset = AccessControlList.objects.get_inherited_permissions(
            obj=self._test_object, role=self._test_role
        )
        self.assertTrue(
            self._test_permission.stored_permission not in queryset
        )

    def test_retrieve_inherited_role_permission_model_applicable(self):
        self._create_test_model()
        EventModelRegistry.register(model=self._test_model_dict['_TestModel_0'])
        self._test_object = self._test_model_dict['_TestModel_0'].objects.create()
        self._create_test_acl()
        self._create_test_permission()

        ModelPermission.register(
            model=self._test_object._meta.model, permissions=(
                self._test_permission,
            )
        )
        self._test_role.grant(permission=self._test_permission)

        queryset = AccessControlList.objects.get_inherited_permissions(
            obj=self._test_object, role=self._test_role
        )
        self.assertTrue(self._test_permission.stored_permission in queryset)

    def test_retrieve_inherited_related_parent_child_permission(self):
        self._create_test_permission()

        self._create_test_model(model_name='TestModelParent')
        self._create_test_model(
            fields={
                'parent': models.ForeignKey(
                    on_delete=models.CASCADE, related_name='children',
                    to='TestModelParent'
                )
            }, model_name='TestModelChild'
        )

        ModelPermission.register(
            model=self._test_model_dict['TestModelParent'], permissions=(
                self._test_permission,
            )
        )
        ModelPermission.register(
            model=self._test_model_dict['TestModelChild'], permissions=(
                self._test_permission,
            )
        )
        ModelPermission.register_inheritance(
            model=self._test_model_dict['TestModelChild'], related='parent'
        )

        parent = self._test_model_dict['TestModelParent'].objects.create()
        child = self._test_model_dict['TestModelChild'].objects.create(parent=parent)

        AccessControlList.objects.grant(
            obj=parent, permission=self._test_permission,
            role=self._test_role
        )
        queryset = AccessControlList.objects.get_inherited_permissions(
            obj=child, role=self._test_role
        )

        self.assertTrue(self._test_permission.stored_permission in queryset)

    def test_retrieve_inherited_related_grandparent_parent_child_permission(
        self
    ):
        self._create_test_permission()

        self._create_test_model(model_name='TestModelGrandParent')
        self._create_test_model(
            fields={
                'parent': models.ForeignKey(
                    on_delete=models.CASCADE, related_name='children',
                    to='TestModelGrandParent'
                )
            }, model_name='TestModelParent'
        )
        self._create_test_model(
            fields={
                'parent': models.ForeignKey(
                    on_delete=models.CASCADE, related_name='children',
                    to='TestModelParent'
                )
            }, model_name='TestModelChild'
        )

        ModelPermission.register(
            model=self._test_model_dict['TestModelGrandParent'], permissions=(
                self._test_permission,
            )
        )
        ModelPermission.register(
            model=self._test_model_dict['TestModelParent'], permissions=(
                self._test_permission,
            )
        )
        ModelPermission.register(
            model=self._test_model_dict['TestModelChild'], permissions=(
                self._test_permission,
            )
        )
        ModelPermission.register_inheritance(
            model=self._test_model_dict['TestModelChild'], related='parent'
        )
        ModelPermission.register_inheritance(
            model=self._test_model_dict['TestModelParent'], related='parent'
        )

        grandparent = self._test_model_dict['TestModelGrandParent'].objects.create()
        parent = self._test_model_dict['TestModelParent'].objects.create(parent=grandparent)
        child = self._test_model_dict['TestModelChild'].objects.create(parent=parent)

        AccessControlList.objects.grant(
            obj=grandparent, permission=self._test_permission,
            role=self._test_role
        )

        queryset = AccessControlList.objects.get_inherited_permissions(
            obj=child, role=self._test_role
        )

        self.assertTrue(self._test_permission.stored_permission in queryset)

    def test_sub_model_with_multiple_inheritance_parent_with_common_super_parent_paths(self):
        self._create_test_permission()

        self._create_test_model(model_name='TestModelLevel1')
        self._create_test_model(
            fields={
                'level_1': models.ForeignKey(
                    on_delete=models.CASCADE, to='TestModelLevel1'
                )
            }, model_name='TestModelLevel2'
        )
        self._create_test_model(
            fields={
                'level_2': models.ForeignKey(
                    on_delete=models.CASCADE, to='TestModelLevel2'
                )
            }, model_name='TestModelLevel3'
        )
        self._create_test_model(
            fields={
                'level_3': models.ForeignKey(
                    on_delete=models.CASCADE, to='TestModelLevel3'
                )
            }, model_name='TestModelLevel4'
        )

        ModelPermission.register(
            model=self._test_model_dict['TestModelLevel2'], permissions=(
                self._test_permission,
            )
        )

        ModelPermission.register_inheritance(
            model=self._test_model_dict['TestModelLevel2'],
            related='level_1'
        )
        ModelPermission.register_inheritance(
            model=self._test_model_dict['TestModelLevel3'],
            related='level_2__level_1'
        )
        ModelPermission.register_inheritance(
            model=self._test_model_dict['TestModelLevel3'],
            related='level_2'
        )
        ModelPermission.register_inheritance(
            model=self._test_model_dict['TestModelLevel4'],
            related='level_3'
        )

        level_1 = self._test_model_dict['TestModelLevel1'].objects.create()
        level_2 = self._test_model_dict['TestModelLevel2'].objects.create(level_1=level_1)
        level_3 = self._test_model_dict['TestModelLevel3'].objects.create(level_2=level_2)
        level_4 = self._test_model_dict['TestModelLevel4'].objects.create(level_3=level_3)

        self.grant_access(
            obj=level_2, permission=self._test_permission
        )

        queryset = AccessControlList.objects.restrict_queryset(
            permission=self._test_permission,
            queryset=self._test_model_dict['TestModelLevel4'].objects.all(),
            user=self._test_case_user
        )

        self.assertTrue(level_4 in queryset)


class GenericForeignKeyFieldModelTestCase(ACLTestMixin, BaseTestCase):
    auto_create_acl_test_object = False

    def test_generic_foreign_key_model_with_alternate_ct_and_fk(self):
        self._create_test_permission()

        self._create_test_model(model_name='TestModelExternal')
        self._create_test_model(
            fields={
                'content_type_1': models.ForeignKey(
                    on_delete=models.CASCADE,
                    related_name='object_content_type',
                    to=ContentType
                ),
                'object_id_1': models.PositiveIntegerField(),
                'content_object_1': GenericForeignKey(
                    ct_field='content_type_1', fk_field='object_id_1'
                )
            }, model_name='TestModelChild'
        )

        ModelPermission.register(
            model=self._test_model_dict['TestModelExternal'], permissions=(
                self._test_permission,
            )
        )
        ModelPermission.register(
            model=self._test_model_dict['TestModelChild'], permissions=(
                self._test_permission,
            )
        )

        ModelPermission.register_inheritance(
            model=self._test_model_dict['TestModelChild'],
            related='content_object_1'
        )

        test_external_object = self._test_model_dict['TestModelExternal'].objects.create()
        test_object = self._test_model_dict['TestModelChild'].objects.create(
            content_object_1=test_external_object
        )

        self.grant_access(
            obj=test_external_object, permission=self._test_permission
        )

        queryset = AccessControlList.objects.restrict_queryset(
            queryset=self._test_model_dict['TestModelChild'].objects.all(),
            permission=self._test_permission, user=self._test_case_user
        )

        self.assertTrue(test_object in queryset)

    def test_generic_foreign_key_model_with_multiple_alternate_ct_and_fk(self):
        self._create_test_permission()

        self._create_test_model(model_name='TestModelExternal')
        self._create_test_model(
            fields={
                'content_type_1': models.ForeignKey(
                    on_delete=models.CASCADE,
                    related_name='object_content_type', to=ContentType
                ),
                'object_id_1': models.PositiveIntegerField(),
                'content_object_1': GenericForeignKey(
                    ct_field='content_type_1', fk_field='object_id_1'
                ),
                'content_type_2': models.ForeignKey(
                    blank=True, null=True, on_delete=models.CASCADE,
                    related_name='object_content_type',
                    to=ContentType
                ),
                'object_id_2': models.PositiveIntegerField(
                    blank=True, null=True
                ),
                'content_object_2': GenericForeignKey(
                    ct_field='content_type_2', fk_field='object_id_2'
                )
            }, model_name='TestModelChild'
        )

        ModelPermission.register(
            model=self._test_model_dict['TestModelExternal'], permissions=(
                self._test_permission,
            )
        )
        ModelPermission.register(
            model=self._test_model_dict['TestModelChild'], permissions=(
                self._test_permission,
            )
        )

        ModelPermission.register_inheritance(
            model=self._test_model_dict['TestModelChild'],
            related='content_object_1'
        )
        ModelPermission.register_inheritance(
            model=self._test_model_dict['TestModelChild'],
            related='content_object_2'
        )

        test_external_object = self._test_model_dict['TestModelExternal'].objects.create()
        test_object = self._test_model_dict['TestModelChild'].objects.create(
            content_object_1=test_external_object
        )

        self.grant_access(
            obj=test_external_object, permission=self._test_permission
        )

        queryset = AccessControlList.objects.restrict_queryset(
            queryset=self._test_model_dict['TestModelChild'].objects.all(),
            permission=self._test_permission, user=self._test_case_user
        )

        self.assertTrue(test_object in queryset)

    def test_generic_foreign_key_model_with_typecasting(self):
        self._create_test_permission()

        self._create_test_model(model_name='TestModelExternal')
        self._create_test_model(
            fields={
                'content_type': models.ForeignKey(
                    on_delete=models.CASCADE,
                    related_name='object_content_type',
                    to=ContentType
                ),
                'object_id': models.CharField(max_length=255),
                'content_object': GenericForeignKey(
                    ct_field='content_type', fk_field='object_id'
                )
            }, model_name='TestModelChild'
        )

        ModelPermission.register(
            model=self._test_model_dict['TestModelExternal'], permissions=(
                self._test_permission,
            )
        )
        ModelPermission.register(
            model=self._test_model_dict['TestModelChild'], permissions=(
                self._test_permission,
            )
        )

        ModelPermission.register_inheritance(
            model=self._test_model_dict['TestModelChild'],
            related='content_object', fk_field_cast=models.CharField
        )

        test_external_object = self._test_model_dict['TestModelExternal'].objects.create()
        test_object = self._test_model_dict['TestModelChild'].objects.create(
            content_object=test_external_object
        )

        self.grant_access(
            obj=test_external_object, permission=self._test_permission
        )

        queryset = AccessControlList.objects.restrict_queryset(
            queryset=self._test_model_dict['TestModelChild'].objects.all(),
            permission=self._test_permission, user=self._test_case_user
        )

        self.assertTrue(test_object in queryset)


class ProxyModelPermissionTestCase(ACLTestMixin, BaseTestCase):
    def test_proxy_model_filtering_no_permission(self):
        self._create_acl_test_object_base()
        self._create_acl_test_object_proxy()

        proxy_object = self._test_model_dict['TestModelProxy'].objects.get(
            pk=self._test_object.pk
        )

        self.assertFalse(
            proxy_object in AccessControlList.objects.restrict_queryset(
                permission=self._test_permission,
                queryset=self._test_model_dict['TestModelProxy'].objects.all(),
                user=self._test_case_user
            )
        )

    def test_proxy_model_filtering_with_access(self):
        self._create_acl_test_object_base()
        self._create_acl_test_object_proxy()

        self.grant_access(
            obj=self._test_object, permission=self._test_permission
        )

        proxy_object = self._test_model_dict['TestModelProxy'].objects.get(pk=self._test_object.pk)

        self.assertTrue(
            proxy_object in AccessControlList.objects.restrict_queryset(
                permission=self._test_permission,
                queryset=self._test_model_dict['TestModelProxy'].objects.all(),
                user=self._test_case_user
            )
        )

    def test_proxy_model_inheritance_with_access(self):
        self._create_test_permission()

        self._create_test_model(model_name='TestModelParent')
        self._create_test_model(
            fields={
                'parent': models.ForeignKey(
                    on_delete=models.CASCADE, related_name='children',
                    to='TestModelParent'
                )
            }, model_name='TestModelChild'
        )
        self._create_test_model(
            base_class=self._test_model_dict['TestModelChild'],
            model_name='TestModelProxy',
            options={'proxy': True}
        )

        ModelPermission.register(
            model=self._test_model_dict['TestModelParent'], permissions=(
                self._test_permission,
            )
        )
        ModelPermission.register_inheritance(
            model=self._test_model_dict['TestModelChild'], related='parent'
        )

        parent = self._test_model_dict['TestModelParent'].objects.create()
        child = self._test_model_dict['TestModelChild'].objects.create(parent=parent)

        self.grant_access(obj=parent, permission=self._test_permission)

        proxy_object = self._test_model_dict['TestModelProxy'].objects.get(pk=child.pk)

        self.assertTrue(
            proxy_object in AccessControlList.objects.restrict_queryset(
                permission=self._test_permission,
                queryset=self._test_model_dict['TestModelProxy'].objects.all(),
                user=self._test_case_user
            )
        )
