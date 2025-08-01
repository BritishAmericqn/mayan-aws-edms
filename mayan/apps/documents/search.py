from django.utils.translation import gettext_lazy as _

from mayan.apps.dynamic_search.search_models import SearchModel
from mayan.apps.views.literals import LIST_MODE_CHOICE_ITEM

from .permissions import (
    permission_document_file_view, permission_document_type_view,
    permission_document_version_view, permission_document_view
)

# Document

search_model_document = SearchModel(
    app_label='documents', default=True, label=_(message='Document'),
    list_mode=LIST_MODE_CHOICE_ITEM, manager_name='valid',
    model_name='DocumentSearchResult', permission=permission_document_view,
    serializer_path='mayan.apps.documents.serializers.document_serializers.DocumentSerializer'
)
search_model_document.add_proxy_model(
    app_label='documents', model_name='Document'
)
search_model_document.add_proxy_model(
    app_label='documents', model_name='RecentlyAccessedDocumentProxy'
)
search_model_document.add_proxy_model(
    app_label='documents', model_name='RecentlyCreatedDocument'
)

search_model_document.add_model_field(
    field='document_type__id',
    help_text=_(message='The database ID of the document type.'),
    label=_(message='Document type ID')
)
search_model_document.add_model_field(
    field='document_type__label', label=_(message='Document type label')
)
search_model_document.add_model_field(field='datetime_created')
search_model_document.add_model_field(field='label')
search_model_document.add_model_field(field='description')
search_model_document.add_model_field(field='language')
search_model_document.add_model_field(field='uuid')
search_model_document.add_model_field(
    field='files__checksum', label=('Document file checksum')
)
search_model_document.add_model_field(
    field='files__filename', label=('Document file filename')
)
search_model_document.add_model_field(
    field='files__mimetype', label=('Document file MIME type')
)

# Document file

search_model_document_file = SearchModel(
    app_label='documents', label=_(message='Document file'),
    list_mode=LIST_MODE_CHOICE_ITEM, manager_name='valid',
    model_name='DocumentFileSearchResult',
    permission=permission_document_file_view,
    serializer_path='mayan.apps.documents.serializers.document_file_serializers.DocumentFileSerializer'
)
search_model_document_file.add_proxy_model(
    app_label='documents', model_name='DocumentFile'
)

search_model_document_file.add_model_field(
    field='document__document_type__label',
    label=_(message='Document type label')
)
search_model_document_file.add_model_field(
    field='document__description', label=_(message='Document description')
)
search_model_document_file.add_model_field(
    field='document__id',
    help_text=_(message='The database ID of the document.'),
    label=_(message='Document ID')
)
search_model_document_file.add_model_field(
    field='document__label', label=_(message='Document label')
)
search_model_document_file.add_model_field(
    field='document__uuid', label=_(message='Document UUID')
)
search_model_document_file.add_model_field(field='checksum')
search_model_document_file.add_model_field(field='comment')
search_model_document_file.add_model_field(field='filename')
search_model_document_file.add_model_field(field='mimetype')
search_model_document_file.add_model_field(field='size')

# Document file page

search_model_document_file_page = SearchModel(
    app_label='documents', label=_(message='Document file page'),
    list_mode=LIST_MODE_CHOICE_ITEM, manager_name='valid',
    model_name='DocumentFilePageSearchResult',
    permission=permission_document_file_view,
    serializer_path='mayan.apps.documents.serializers.document_file_serializers.DocumentFilePageSerializer'
)
search_model_document_file_page.add_proxy_model(
    app_label='documents', model_name='DocumentFilePage'
)

search_model_document_file_page.add_model_field(
    field='document_file__document__document_type__label',
    label=_(message='Document type label')
)
search_model_document_file_page.add_model_field(
    field='document_file__document__label', label=_(message='Document label')
)
search_model_document_file_page.add_model_field(
    field='document_file__checksum', label=_(message='Document file checksum')
)
search_model_document_file_page.add_model_field(
    field='document_file__document__uuid', label=_(message='Document UUID')
)

# Document type

search_model_document_type = SearchModel(
    app_label='documents', list_mode=LIST_MODE_CHOICE_ITEM,
    model_name='DocumentType', permission=permission_document_type_view,
    serializer_path='mayan.apps.documents.serializers.document_type_serializers.DocumentTypeSerializer'
)
search_model_document_type.add_model_field(field='id')
search_model_document_type.add_model_field(field='label')

# Document version

search_model_document_version = SearchModel(
    app_label='documents', label=_(message='Document version'),
    list_mode=LIST_MODE_CHOICE_ITEM, manager_name='valid',
    model_name='DocumentVersionSearchResult',
    permission=permission_document_version_view,
    serializer_path='mayan.apps.documents.serializers.document_version_serializers.DocumentVersionSerializer'
)
search_model_document_version.add_proxy_model(
    app_label='documents', model_name='DocumentVersion'
)

search_model_document_version.add_model_field(field='comment')
search_model_document_version.add_model_field(
    field='document__document_type__label',
    label=_(message='Document type label')
)
search_model_document_version.add_model_field(
    field='document__id',
    help_text=_(message='The database ID of the document.'),
    label=_(message='Document ID')
)
search_model_document_version.add_model_field(
    field='document__label', label=_(message='Document label')
)
search_model_document_version.add_model_field(
    field='document__description', label=_(message='Document description')
)
search_model_document_version.add_model_field(
    field='document__uuid', label=_(message='Document UUID')
)

# Document version page

search_model_document_version_page = SearchModel(
    app_label='documents', label=_(message='Document version page'),
    list_mode=LIST_MODE_CHOICE_ITEM, manager_name='valid',
    model_name='DocumentVersionPageSearchResult',
    permission=permission_document_version_view,
    serializer_path='mayan.apps.documents.serializers.document_version_serializers.DocumentVersionPageSerializer'
)
search_model_document_version_page.add_proxy_model(
    app_label='documents', model_name='DocumentVersionPage'
)

search_model_document_version_page.add_model_field(
    field='document_version__document__document_type__label',
    label=_(message='Document type label')
)
search_model_document_version_page.add_model_field(
    field='document_version__document__label',
    label=_(message='Document label')
)
search_model_document_version_page.add_model_field(
    field='document_version__document__uuid',
    label=_(message='Document UUID')
)
