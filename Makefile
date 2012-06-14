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

docs:
	cd docs; make html

pep:
	pep8 --first pyvantagepro

clean:
	git clean -Xfd
