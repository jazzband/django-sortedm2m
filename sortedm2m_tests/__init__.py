import os
from setuptest.setuptest import SetupTestSuite as _SetupTestSuite


TEST_APPS = ['sortedm2m_tests', 'sortedm2m_field', 'sortedm2m_form',
    'south_support']


class SetupTestSuite(_SetupTestSuite):
    def __init__(self, *args, **kwargs):
        os.environ['DJANGO_SETTINGS_MODULE'] = 'test_settings'
        from south.management.commands import patch_for_test_db_setup
        patch_for_test_db_setup()
        super(SetupTestSuite, self).__init__(*args, **kwargs)

    def resolve_packages(self):
        packages = super(SetupTestSuite, self).resolve_packages()
        for test_app in TEST_APPS:
            if test_app not in packages:
                packages.append(test_app)
        return packages
