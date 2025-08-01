import logging

from django.apps import apps
from django.contrib.contenttypes.models import ContentType

from ..classes import ErrorLog

from .literals import TEST_ERROR_LOG_ENTRY_RESULT


class ErrorLogPartitionEntryAPIViewTestMixin:
    def _request_test_error_log_delete_api_view(self):
        content_type = ContentType.objects.get_for_model(
            model=self._test_object
        )

        return self.delete(
            viewname='rest_api:errorlogpartitionentry-detail', kwargs={
                'app_label': content_type.app_label,
                'model_name': content_type.model,
                'object_id': self._test_object.pk,
                'error_log_partition_entry_id': self._test_error_log_entry.pk
            }
        )

    def _request_test_error_log_detail_api_view(self):
        content_type = ContentType.objects.get_for_model(
            model=self._test_object
        )

        return self.get(
            viewname='rest_api:errorlogpartitionentry-detail', kwargs={
                'app_label': content_type.app_label,
                'model_name': content_type.model,
                'object_id': self._test_object.pk,
                'error_log_partition_entry_id': self._test_error_log_entry.pk
            }
        )

    def _request_test_error_log_list_api_view(self):
        content_type = ContentType.objects.get_for_model(
            model=self._test_object
        )

        return self.get(
            viewname='rest_api:errorlogpartitionentry-list', kwargs={
                'app_label': content_type.app_label,
                'model_name': content_type.model,
                'object_id': self._test_object.pk
            }
        )


class ErrorLogPartitionEntryTestMixin:
    def _create_test_error_log_object(self):
        app_config = apps.get_app_config(app_label='logging')
        self.error_log = ErrorLog(app_config=app_config)

        self._create_test_user()
        self._test_object = self._test_user

    def _create_test_error_log_entry(self):
        self._test_error_log_entry = self._test_object.error_log.create(
            text=TEST_ERROR_LOG_ENTRY_RESULT
        )


class ErrorLogViewTestMixin:
    def _request_object_error_log_list_view(self):
        content_type = ContentType.objects.get_for_model(
            model=self._test_object
        )

        return self.get(
            viewname='logging:object_error_log_entry_list', kwargs={
                'app_label': content_type.app_label,
                'model_name': content_type.model,
                'object_id': self._test_object.pk
            }
        )

    def _request_object_error_log_clear_view(self):
        content_type = ContentType.objects.get_for_model(
            model=self._test_object
        )

        return self.post(
            viewname='logging:object_error_log_entry_list_clear', kwargs={
                'app_label': content_type.app_label,
                'model_name': content_type.model,
                'object_id': self._test_object.pk
            }
        )

    def _request_object_error_log_entry_delete_view(self):
        content_type = ContentType.objects.get_for_model(
            model=self._test_object
        )

        return self.post(
            viewname='logging:object_error_log_entry_delete', kwargs={
                'app_label': content_type.app_label,
                'model_name': content_type.model,
                'object_id': self._test_object.pk,
                'error_log_partition_entry_id': self._test_error_log_entry.pk
            }
        )


class GlobalErrorLogViewTestMixin:
    def _request_global_error_log_partition_entry_list_view(self):
        return self.get(
            viewname='logging:global_error_log_partition_entry_list'
        )


class TestCaseMixinSilenceLogger:
    """
    Changes the log level of a specific logger for the duration of a test.
    The default level for silenced loggers is CRITICAL.
    Example: self._silence_logger(name='mayan.apps.converter.managers')
    """
    test_case_silenced_logger = None
    test_case_silenced_logger_new_level = logging.CRITICAL

    def tearDown(self):
        if self.test_case_silenced_logger:
            self.test_case_silenced_logger.setLevel(
                level=self.test_case_silenced_logger_level
            )

        super().tearDown()

    def _silence_logger(self, name):
        self.test_case_silenced_logger = logging.getLogger(name=name)
        self.test_case_silenced_logger_level = self.test_case_silenced_logger.level
        self.test_case_silenced_logger.setLevel(
            level=self.test_case_silenced_logger_new_level
        )
