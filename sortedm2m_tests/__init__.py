import os
import setuptest


TEST_APPS = ['sortedm2m_tests', 'sortedm2m_field', 'sortedm2m_form', 'south_support']


class TestSuite(setuptest.SetupTestSuite):
    def __init__(self, *args, **kwargs):
        os.environ['DJANGO_SETTINGS_MODULE'] = 'test_settings'
        from south.management.commands import patch_for_test_db_setup
        patch_for_test_db_setup()
        super(TestSuite, self).__init__(*args, **kwargs)

    def resolve_packages(self):
        packages = super(TestSuite, self).resolve_packages()
        for test_app in TEST_APPS:
            if test_app not in packages:
                packages.append(test_app)
        return packages
