.PHONY: quality requirements qunit

quality: ## Run isort, pycodestyle, and Pylint
	isort --check-only --recursive .
	pycodestyle example sortedm2m sortedm2m_tests test_project *.py
	pylint --rcfile=pylintrc example sortedm2m sortedm2m_tests test_project *.py

requirements: ## Install requirements for development
	pip install -r requirements.txt

qunit:
	timeout 20 xvfb-run python test_project/qunit-runner.py
