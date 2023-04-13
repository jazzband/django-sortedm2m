.PHONY: quality requirements

CHECK_DIRS?=example sortedm2m sortedm2m_tests test_project *.py

quality: ## Run isort, pycodestyle, and Pylint
	isort --check-only $(CHECK_DIRS)
	pycodestyle $(CHECK_DIRS)
	DJANGO_SETTINGS_MODULE=test_project.settings pylint --errors-only --load-plugins pylint_django $(CHECK_DIRS)

requirements: ## Install requirements for development
	pip install -r requirements.txt
