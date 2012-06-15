SHELL := /bin/bash

# these files should pass pyflakes
# exclude ./env/, which may contain virtualenv packages
PYFLAKES_WHITELIST=$(shell find . -name "*.py" ! -path "./docs/*" \
                    ! -path "./.tox/*" ! -path "./pyvantagepro/__init__.py" \
                    ! -path "./pyvantagepro/compat.py")

test:
	tox

pyflakes:
	pyflakes ${PYFLAKES_WHITELIST}

doc:
	cd docs; make html

upload-doc:
	python setup.py upload_sphinx

pep:
	pep8 --first pyvantagepro

clean:
	git clean -Xfd

dist:
	python setup.py sdist

upload:
	python setup.py sdist upload
