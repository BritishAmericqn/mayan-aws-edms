import os
import time

from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver

from django.conf import settings
from django.db.models import Q
from django.urls import reverse


class ContentTypeCheckTestCaseMixin:
    expected_content_types = ('text/html', 'text/html; charset=utf-8')

    def _pre_setup(self):
        super()._pre_setup()
        test_instance = self

        class CustomClient(self.client_class):
            def request(self, *args, **kwargs):
                response = super().request(*args, **kwargs)

                content_type = response.headers.get('content-type', '')
                if test_instance.expected_content_types:
                    test_instance.assertTrue(
                        content_type in test_instance.expected_content_types,
                        msg='Unexpected response content type: {}, expected: {}.'.format(
                            content_type, ' or '.join(
                                test_instance.expected_content_types
                            )
                        )
                    )

                return response

        self.client = CustomClient()


class DelayTestCaseMixin:
    def _test_delay(self, seconds=0.1):
        time.sleep(seconds)


class EnvironmentTestCaseMixin:
    def setUp(self):
        super().setUp()
        self._test_environment_variable_list = []

    def tearDown(self):
        for name in self._test_environment_variable_list:
            os.environ.pop(name)

        super().tearDown()

    def _set_environment_variable(self, name, value):
        self._test_environment_variable_list.append(name)
        os.environ[name] = value


class SeleniumTestMixin:
    SKIP_VARIABLE_NAME = 'TESTS_SELENIUM_SKIP'

    @staticmethod
    def _get_skip_variable_value():
        return os.environ.get(
            SeleniumTestMixin._get_skip_variable_environment_name(),
            getattr(settings, SeleniumTestMixin.SKIP_VARIABLE_NAME, False)
        )

    @staticmethod
    def _get_skip_variable_environment_name():
        return 'MAYAN_{}'.format(SeleniumTestMixin.SKIP_VARIABLE_NAME)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.webdriver = None
        if not SeleniumTestMixin._get_skip_variable_value():
            options = Options()
            options.add_argument('--headless')
            cls.webdriver = WebDriver(
                firefox_options=options, log_path='/dev/null'
            )

    @classmethod
    def tearDownClass(cls):
        if cls.webdriver:
            cls.webdriver.quit()
        super().tearDownClass()

    def setUp(self):
        if SeleniumTestMixin._get_skip_variable_value():
            self.skipTest(reason='Skipping selenium test')
        super().setUp()

    def _open_url(self, fragment=None, path=None, viewname=None):
        url = '{}{}{}'.format(
            self.live_server_url, path or reverse(viewname=viewname),
            fragment or ''
        )

        self.webdriver.get(url=url)


class TestMixinObjectCreationTrack:
    _test_object_list_name = None
    _test_object_model = None
    _test_object_name = None

    def _test_object_get_object_list_name(self, test_object_list_name=None):
        test_object_list_name = test_object_list_name or self._test_object_list_name or '{}_list'.format(
            self._test_object_name
        )

        return test_object_list_name

    def _test_object_list_set(self, test_object_list_name=None):
        self._test_object_list_name = self._test_object_get_object_list_name(
            test_object_list_name=test_object_list_name
        )

        _test_object_list = self._test_object_model.objects.filter(
            ~Q(pk__in=self._test_object_pk_list)
        )

        setattr(
            self, self._test_object_list_name, _test_object_list
        )

    def _test_object_set(self, test_object_name=None):
        test_object_name = test_object_name or self._test_object_name

        try:
            _test_object = self._test_object_model.objects.get(
                ~Q(pk__in=self._test_object_pk_list)
            )
        except self._test_object_model.DoesNotExist:
            _test_object = None

        setattr(self, test_object_name, _test_object)

    def _test_object_track(self):
        self._test_object_pk_list = list(
            self._test_object_model.objects.values_list('pk', flat=True)
        )
