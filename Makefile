# these files should pass pyflakes
# exclude ./env/, which may contain virtualenv packages
PYFLAKES_WHITELIST=$(/bin/bash find . -name "*.py" ! -path "./docs/*" \
                    ! -path "./.tox/*" ! -path "./pyvantagepro/__init__.py" \
                    ! -path "./pyvantagepro/compat.py")

env:
	virtualenv ./env
	/bin/bash -c 'source ./env/bin/activate ; pip install hg+https://bitbucket.org/birkenfeld/sphinx ; pip install tox ; pip install -e . '

test:
	tox

pyflakes:
	pyflakes ${PYFLAKES_WHITELIST}

pep:
	pep8 --first pyvantagepro

doc:
	cd docs; make html

upload-doc:
	python setup.py upload_sphinx

clean:
	git clean -Xfd

dist:
	python setup.py sdist

upload:
	python setup.py sdist upload
