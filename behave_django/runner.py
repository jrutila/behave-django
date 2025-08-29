from django.test.runner import DiscoverRunner

from behave_django.environment import BehaveHooksMixin
from behave_django.testcase import (
    BehaviorDrivenTestCase,
    DjangoSimpleTestCase,
    ExistingDatabaseTestCase,
)


class BehaviorDrivenTestRunner(DiscoverRunner, BehaveHooksMixin):
    """Test runner that uses the BehaviorDrivenTestCase."""

    testcase_class = BehaviorDrivenTestCase

    def teardown_databases(self, old_config, **kwargs):
        for connection, old_name, destroy in old_config:
            print("teardown_databases", connection.cursor, old_name, destroy)
            if destroy:
                query = f"""
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'test_{old_name}'
AND pid <> pg_backend_pid();
"""
                with connection.cursor() as cursor:
                    cursor.execute(query)
                connection.close()
        super().teardown_databases(old_config, **kwargs)

class ExistingDatabaseTestRunner(DiscoverRunner, BehaveHooksMixin):
    """Test runner that uses the ExistingDatabaseTestCase.

    This test runner nullifies Django's test database setup methods. Using this
    test runner would make your tests run with the default configured database
    in settings.py.
    """

    testcase_class = ExistingDatabaseTestCase

    def setup_databases(self, **kwargs):
        pass

    def teardown_databases(self, old_config, **kwargs):
        pass


class SimpleTestRunner(DiscoverRunner, BehaveHooksMixin):
    """Test runner that uses DjangoSimpleTestCase with atomic
    transaction management and no support of web browser automation.
    """

    testcase_class = DjangoSimpleTestCase
