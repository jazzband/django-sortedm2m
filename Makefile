test-postgres:
	vagrant up
	vagrant ssh -c "cd /vagrant ; DJANGO_SETTINGS_MODULE=test_project.postgres_settings python runtests.py"

isort_check:
	isort -rc -c -df sortedm2m sortedm2m_tests

isort:
	isort -rc sortedm2m sortedm2m_tests
