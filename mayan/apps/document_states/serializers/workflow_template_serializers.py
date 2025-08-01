from django.utils.translation import gettext_lazy as _

from mayan.apps.documents.models.document_type_models import DocumentType
from mayan.apps.documents.permissions import permission_document_type_edit
from mayan.apps.rest_api import serializers
from mayan.apps.rest_api.relations import FilteredPrimaryKeyRelatedField

from ..models import Workflow


class WorkflowTemplateSerializer(serializers.HyperlinkedModelSerializer):
    document_types_add_url = serializers.HyperlinkedIdentityField(
        label=_(message='Document types add URL'),
        lookup_url_kwarg='workflow_template_id',
        view_name='rest_api:workflow-template-document-type-add'
    )
    document_types_remove_url = serializers.HyperlinkedIdentityField(
        label=_(message='Document types remove URL'),
        lookup_url_kwarg='workflow_template_id',
        view_name='rest_api:workflow-template-document-type-remove'
    )
    document_types_url = serializers.HyperlinkedIdentityField(
        label=_(message='Document types URL'),
        lookup_url_kwarg='workflow_template_id',
        view_name='rest_api:workflow-template-document-type-list'
    )
    documents_url = serializers.HyperlinkedIdentityField(
        label=_(message='Documents URL'),
        lookup_url_kwarg='workflow_template_id',
        view_name='rest_api:workflow-template-document-list'
    )
    image_url = serializers.HyperlinkedIdentityField(
        label=_(message='Image URL'), lookup_url_kwarg='workflow_template_id',
        view_name='rest_api:workflow-template-image'
    )
    states_url = serializers.HyperlinkedIdentityField(
        label=_(message='States URL'), lookup_url_kwarg='workflow_template_id',
        view_name='rest_api:workflow-template-state-list'
    )
    transitions_url = serializers.HyperlinkedIdentityField(
        label=_(message='Transitions URL'), lookup_url_kwarg='workflow_template_id',
        view_name='rest_api:workflow-template-transition-list'
    )

    class Meta:
        extra_kwargs = {
            'url': {
                'label': _(message='URL'),
                'lookup_url_kwarg': 'workflow_template_id',
                'view_name': 'rest_api:workflow-template-detail'
            }
        }
        fields = (
            'auto_launch', 'document_types_add_url',
            'document_types_remove_url', 'document_types_url',
            'documents_url', 'id', 'ignore_completed', 'image_url',
            'internal_name', 'label', 'states_url', 'transitions_url', 'url'
        )
        model = Workflow
        read_only_fields = (
            'document_types_add_url', 'document_types_remove_url',
            'document_types_url', 'documents_url', 'id', 'image_url',
            'states_url', 'transitions_url', 'url'
        )


class WorkflowTemplateDocumentTypeAddSerializer(serializers.Serializer):
    document_type_id = FilteredPrimaryKeyRelatedField(
        help_text=_(
            message='Primary key of the document type to add to the workflow.'
        ), label=_(message='Document type ID'), source_model=DocumentType,
        source_permission=permission_document_type_edit
    )


class WorkflowTemplateDocumentTypeRemoveSerializer(serializers.Serializer):
    document_type_id = FilteredPrimaryKeyRelatedField(
        help_text=_(
            message='Primary key of the document type to remove from the workflow.'
        ), label=_(message='Document type ID'), source_model=DocumentType,
        source_permission=permission_document_type_edit
    )
