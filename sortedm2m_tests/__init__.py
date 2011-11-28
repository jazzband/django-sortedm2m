# Python
import os

# django-setuptest
import setuptest

TEST_APPS = ['sortedm2m_tests', 'sortedm2m_field', 'sortedm2m_form', 'south_support']

class TestSuite(setuptest.SetupTestSuite):
    
    def resolve_packages(self):
        packages = super(TestSuite, self).resolve_packages()
        for test_app in TEST_APPS:
            if test_app not in packages:
                packages.append(test_app)
        return packages
