.PHONY: quality requirements test-postgres

quality: ## Run isort, pycodestyle, and Pylint
	isort --check-only --recursive sortedm2m/
	pycodestyle sortedm2m *.py
	# pylint --rcfile=pylintrc sortedm2m *.py

requirements: ## Install requirements for development
	pip install -r requirements/test.txt

test-postgres:
	vagrant up
	vagrant ssh -c "cd /vagrant ; DJANGO_SETTINGS_MODULE=test_project.postgres_settings python runtests.py"
