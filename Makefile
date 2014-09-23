test-postgres:
	vagrant up
	vagrant ssh -c "cd /vagrant ; DJANGO_SETTINGS_MODULE=test_project.postgres_settings python runtests.py"
