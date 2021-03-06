.PHONY: docs
init:
	pip install pipenv --upgrade
	pipenv install --dev
test:
	python setup.py test
ci:
	python setup.py test

test-readme:
	@pipenv run python setup.py check --restructuredtext --strict && ([ $$? -eq 0 ] && echo "README.rst and HISTORY.rst ok") || echo "Invalid markup in README.rst or HISTORY.rst!"

flake8:
	pipenv run flake8 --ignore=E501,F401,E128,E402,E731,F821 azure_runbook_util

coverage:
	pipenv run py.test --cov-config .coveragerc --verbose --cov-report term --cov-report xml --cov=requests tests

build:
	python setup.py sdist bdist_wheel

publish: build
	pip install 'twine>=1.5.0'
	python setup.py sdist bdist_wheel
	twine upload dist/*
	rm -fr build dist .egg azure_runbook_util.egg-info

docs:
	cd docs && make html
	@echo "\033[95m\n\nBuild successful! View the docs homepage at docs/_build/html/index.html.\n\033[0m"