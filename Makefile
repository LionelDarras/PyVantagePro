SHELL := /bin/bash

# these files should pass pyflakes
# exclude ./env/, which may contain virtualenv packages
PYFLAKES_WHITELIST=$(shell find . -name "*.py" ! -path "./docs/*" \
                    ! -path "./.tox/*" ! -path "./env/*" \
                    ! -path "./pyvantagepro/__init__.py" \
                    ! -path "./pyvantagepro/compat.py")

env:
	rm ./env -fr
	virtualenv ./env
	/bin/bash -c 'source ./env/bin/activate ; pip install pep8 ; \
        pip install pyflakes ; \
        pip install tox ; pip install -e . '
test:
	tox

pyflakes:
	pyflakes ${PYFLAKES_WHITELIST}

pep:
	pep8 --first pyvantagepro

doc:
	cd docs; make html

clean:
	git clean -Xfd

dist:
	python setup.py sdist

upload:
	python setup.py sdist upload
