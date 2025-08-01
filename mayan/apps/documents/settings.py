from django.utils.translation import gettext_lazy as _

from mayan.apps.smart_settings.settings import setting_cluster

from .literals import (
    DEFAULT_DOCUMENTS_DISPLAY_HEIGHT, DEFAULT_DOCUMENTS_DISPLAY_WIDTH,
    DEFAULT_DOCUMENTS_FAVORITE_COUNT,
    DEFAULT_DOCUMENTS_FILE_PAGE_IMAGE_CACHE_MAXIMUM_SIZE,
    DEFAULT_DOCUMENTS_FILE_PAGE_IMAGE_CACHE_STORAGE_BACKEND,
    DEFAULT_DOCUMENTS_FILE_PAGE_IMAGE_CACHE_STORAGE_BACKEND_ARGUMENTS,
    DEFAULT_DOCUMENTS_FILE_STORAGE_BACKEND,
    DEFAULT_DOCUMENTS_FILE_STORAGE_BACKEND_ARGUMENTS,
    DEFAULT_DOCUMENTS_HASH_BLOCK_SIZE, DEFAULT_DOCUMENTS_LIST_THUMBNAIL_WIDTH,
    DEFAULT_DOCUMENTS_PREVIEW_HEIGHT, DEFAULT_DOCUMENTS_PREVIEW_WIDTH,
    DEFAULT_DOCUMENTS_PRINT_HEIGHT, DEFAULT_DOCUMENTS_PRINT_WIDTH,
    DEFAULT_DOCUMENTS_RECENTLY_ACCESSED_COUNT,
    DEFAULT_DOCUMENTS_RECENTLY_CREATED_COUNT, DEFAULT_DOCUMENTS_ROTATION_STEP,
    DEFAULT_DOCUMENTS_STUBS_DELETE_TASK_INTERVAL,
    DEFAULT_DOCUMENTS_THUMBNAIL_HEIGHT, DEFAULT_DOCUMENTS_THUMBNAIL_WIDTH,
    DEFAULT_DOCUMENTS_TRASH_PERIOD_CHECK_TASK_INTERVAL,
    DEFAULT_DOCUMENTS_TRASHED_DELETE_PERIODS_CHECK_TASK_INTERVAL,
    DEFAULT_DOCUMENTS_VERSION_PAGE_IMAGE_CACHE_MAXIMUM_SIZE,
    DEFAULT_DOCUMENTS_VERSION_PAGE_IMAGE_CACHE_STORAGE_BACKEND,
    DEFAULT_DOCUMENTS_VERSION_PAGE_IMAGE_CACHE_STORAGE_BACKEND_ARGUMENTS,
    DEFAULT_DOCUMENTS_ZOOM_MAX_LEVEL, DEFAULT_DOCUMENTS_ZOOM_MIN_LEVEL,
    DEFAULT_DOCUMENTS_ZOOM_PERCENT_STEP, DEFAULT_LANGUAGE,
    DEFAULT_LANGUAGE_CODES
)
from .setting_callbacks import (
    callback_update_document_file_page_image_cache_size,
    callback_update_document_version_page_image_cache_size
)
from .setting_migrations import DocumentsSettingMigration

setting_namespace = setting_cluster.do_namespace_add(
    label=_(message='Documents'), migration_class=DocumentsSettingMigration,
    name='documents', version='0004'
)

setting_display_height = setting_namespace.do_setting_add(
    default=DEFAULT_DOCUMENTS_DISPLAY_HEIGHT,
    global_name='DOCUMENTS_DISPLAY_HEIGHT'
)
setting_display_width = setting_namespace.do_setting_add(
    default=DEFAULT_DOCUMENTS_DISPLAY_WIDTH,
    global_name='DOCUMENTS_DISPLAY_WIDTH'
)
setting_document_file_page_image_cache_maximum_size = setting_namespace.do_setting_add(
    default=DEFAULT_DOCUMENTS_FILE_PAGE_IMAGE_CACHE_MAXIMUM_SIZE,
    global_name='DOCUMENTS_FILE_PAGE_IMAGE_CACHE_MAXIMUM_SIZE',
    help_text=_(
        message='The threshold at which the DOCUMENTS_FILE_PAGE_IMAGE_CACHE_STORAGE_BACKEND will start '
        'deleting the oldest document file page image cache files. Specify '
        'the size in bytes.'
    ), post_edit_function=callback_update_document_file_page_image_cache_size
)
setting_document_file_storage_backend = setting_namespace.do_setting_add(
    default=DEFAULT_DOCUMENTS_FILE_STORAGE_BACKEND,
    global_name='DOCUMENTS_FILE_STORAGE_BACKEND', help_text=_(
        message='Path to the Storage subclass to use when storing document '
        'files.'
    )
)
setting_document_file_storage_backend_arguments = setting_namespace.do_setting_add(
    default=DEFAULT_DOCUMENTS_FILE_STORAGE_BACKEND_ARGUMENTS,
    global_name='DOCUMENTS_FILE_STORAGE_BACKEND_ARGUMENTS', help_text=_(
        message='Arguments to pass to the DOCUMENT_FILE_STORAGE_BACKEND.'
    )
)
setting_document_file_page_image_cache_storage_backend = setting_namespace.do_setting_add(
    default=DEFAULT_DOCUMENTS_FILE_PAGE_IMAGE_CACHE_STORAGE_BACKEND,
    global_name='DOCUMENTS_FILE_PAGE_IMAGE_CACHE_STORAGE_BACKEND', help_text=_(
        message='Path to the Storage subclass to use when storing the cached '
        'document file page image files.'
    )
)
setting_document_file_page_image_cache_storage_backend_arguments = setting_namespace.do_setting_add(
    default=DEFAULT_DOCUMENTS_FILE_PAGE_IMAGE_CACHE_STORAGE_BACKEND_ARGUMENTS,
    global_name='DOCUMENTS_FILE_PAGE_IMAGE_CACHE_STORAGE_BACKEND_ARGUMENTS',
    help_text=_(
        message='Arguments to pass to the DOCUMENTS_FILE_PAGE_IMAGE_CACHE_STORAGE_BACKEND.'
    ),
)
setting_favorite_count = setting_namespace.do_setting_add(
    default=DEFAULT_DOCUMENTS_FAVORITE_COUNT,
    global_name='DOCUMENTS_FAVORITE_COUNT', help_text=_(
        message='Maximum number of favorite documents to remember per user.'
    )
)
setting_hash_block_size = setting_namespace.do_setting_add(
    default=DEFAULT_DOCUMENTS_HASH_BLOCK_SIZE,
    global_name='DOCUMENTS_HASH_BLOCK_SIZE', help_text=_(
        message='Size of blocks to use when calculating the document file\'s '
        'checksum. A value of 0 disables the block calculation and the entire '
        'file will be loaded into memory.'
    )
)
setting_language = setting_namespace.do_setting_add(
    default=DEFAULT_LANGUAGE, global_name='DOCUMENTS_LANGUAGE',
    help_text=_(message='Default documents language (in ISO639-3 format).')
)
setting_language_codes = setting_namespace.do_setting_add(
    default=DEFAULT_LANGUAGE_CODES, global_name='DOCUMENTS_LANGUAGE_CODES',
    help_text=_(message='List of supported document languages. In ISO639-3 format.')
)
setting_document_version_page_image_cache_maximum_size = setting_namespace.do_setting_add(
    default=DEFAULT_DOCUMENTS_VERSION_PAGE_IMAGE_CACHE_MAXIMUM_SIZE,
    global_name='DOCUMENTS_VERSION_PAGE_IMAGE_CACHE_MAXIMUM_SIZE',
    help_text=_(
        message='The threshold at which the DOCUMENT_VERSION_PAGE_IMAGE_CACHE_STORAGE_BACKEND will start '
        'deleting the oldest document version page image cache versions. Specify '
        'the size in bytes.'
    ), post_edit_function=callback_update_document_version_page_image_cache_size
)
setting_document_version_page_image_cache_storage_backend = setting_namespace.do_setting_add(
    default=DEFAULT_DOCUMENTS_VERSION_PAGE_IMAGE_CACHE_STORAGE_BACKEND,
    global_name='DOCUMENTS_VERSION_PAGE_IMAGE_CACHE_STORAGE_BACKEND',
    help_text=_(
        message='Path to the Storage subclass to use when storing the cached '
        'document version page image versions.'
    )
)
setting_document_version_page_image_cache_storage_backend_arguments = setting_namespace.do_setting_add(
    default=DEFAULT_DOCUMENTS_VERSION_PAGE_IMAGE_CACHE_STORAGE_BACKEND_ARGUMENTS,
    global_name='DOCUMENTS_VERSION_PAGE_IMAGE_CACHE_STORAGE_BACKEND_ARGUMENTS',
    help_text=_(
        message='Arguments to pass to the DOCUMENTS_VERSION_PAGE_IMAGE_CACHE_STORAGE_BACKEND.'
    ),
)
setting_preview_height = setting_namespace.do_setting_add(
    default=DEFAULT_DOCUMENTS_PREVIEW_HEIGHT,
    global_name='DOCUMENTS_PREVIEW_HEIGHT'
)
setting_preview_width = setting_namespace.do_setting_add(
    default=DEFAULT_DOCUMENTS_PREVIEW_WIDTH,
    global_name='DOCUMENTS_PREVIEW_WIDTH'
)
setting_print_height = setting_namespace.do_setting_add(
    default=DEFAULT_DOCUMENTS_PRINT_HEIGHT,
    global_name='DOCUMENTS_PRINT_HEIGHT'
)
setting_print_width = setting_namespace.do_setting_add(
    default=DEFAULT_DOCUMENTS_PRINT_WIDTH,
    global_name='DOCUMENTS_PRINT_WIDTH'
)
setting_recently_accessed_document_count = setting_namespace.do_setting_add(
    default=DEFAULT_DOCUMENTS_RECENTLY_ACCESSED_COUNT,
    global_name='DOCUMENTS_RECENTLY_ACCESSED_COUNT', help_text=_(
        message='Maximum number of recently accessed documents (created, edited, '
        'viewed) to remember per user.'
    )
)
setting_recently_created_document_count = setting_namespace.do_setting_add(
    default=DEFAULT_DOCUMENTS_RECENTLY_CREATED_COUNT,
    global_name='DOCUMENTS_RECENTLY_CREATED_COUNT', help_text=_(
        message='Maximum number of recently created documents to show.'
    )
)
setting_rotation_step = setting_namespace.do_setting_add(
    default=DEFAULT_DOCUMENTS_ROTATION_STEP,
    global_name='DOCUMENTS_ROTATION_STEP', help_text=_(
        message='Amount in degrees to rotate a document page per user interaction.'
    )
)
setting_task_document_type_document_trash_periods_check_interval = setting_namespace.do_setting_add(
    default=DEFAULT_DOCUMENTS_TRASH_PERIOD_CHECK_TASK_INTERVAL,
    global_name='DOCUMENTS_TRASH_PERIOD_CHECK_TASK_INTERVAL',
    help_text=_(
        'Time interval in seconds, at which the document trashing task will '
        'execute.'
    )
)
setting_task_document_type_document_stubs_delete_interval = setting_namespace.do_setting_add(
    default=DEFAULT_DOCUMENTS_STUBS_DELETE_TASK_INTERVAL,
    global_name='DOCUMENTS_STUBS_DELETE_TASK_INTERVAL',
    help_text=_(
        'Time interval in seconds, at which the document stub prune task '
        'will execute.'
    )
)
setting_task_trashed_document_delete_periods_check_interval = setting_namespace.do_setting_add(
    default=DEFAULT_DOCUMENTS_TRASHED_DELETE_PERIODS_CHECK_TASK_INTERVAL,
    global_name='DOCUMENTS_TRASHED_DOCUMENT_DELETE_PERIODS_CHECK_TASK_INTERVAL',
    help_text=_(
        'Time interval in seconds, at which the trashed document deletion '
        'task will execute.'
    )
)
setting_thumbnail_height = setting_namespace.do_setting_add(
    default=DEFAULT_DOCUMENTS_THUMBNAIL_HEIGHT,
    global_name='DOCUMENTS_THUMBNAIL_HEIGHT', help_text=_(
        message='Height in pixels of the document thumbnail image.'
    )
)
setting_thumbnail_width = setting_namespace.do_setting_add(
    default=DEFAULT_DOCUMENTS_THUMBNAIL_WIDTH,
    global_name='DOCUMENTS_THUMBNAIL_WIDTH', help_text=(
        'Width in pixels of the document thumbnail image.'
    )
)
setting_thumbnail_list_width = setting_namespace.do_setting_add(
    default=DEFAULT_DOCUMENTS_LIST_THUMBNAIL_WIDTH,
    global_name='DOCUMENTS_LIST_THUMBNAIL_WIDTH', help_text=(
        'Width in pixels of the document thumbnail image when shown in list '
        'view mode.'
    )
)
setting_zoom_max_level = setting_namespace.do_setting_add(
    default=DEFAULT_DOCUMENTS_ZOOM_MAX_LEVEL,
    global_name='DOCUMENTS_ZOOM_MAX_LEVEL', help_text=_(
        message='Maximum amount in percent (%) to allow user to zoom in a document '
        'page interactively.'
    )
)
setting_zoom_min_level = setting_namespace.do_setting_add(
    default=DEFAULT_DOCUMENTS_ZOOM_MIN_LEVEL,
    global_name='DOCUMENTS_ZOOM_MIN_LEVEL', help_text=_(
        message='Minimum amount in percent (%) to allow user to zoom out a document '
        'page interactively.'
    )
)
setting_zoom_percent_step = setting_namespace.do_setting_add(
    default=DEFAULT_DOCUMENTS_ZOOM_PERCENT_STEP,
    global_name='DOCUMENTS_ZOOM_PERCENT_STEP', help_text=_(
        message='Amount in percent zoom in or out a document page per user '
        'interaction.'
    )
)
