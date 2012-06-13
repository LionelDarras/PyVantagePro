SHELL := /bin/bash

# these files should pass pyflakes
# exclude ./env/, which may contain virtualenv packages
PYFLAKES_WHITELIST=$(shell find . -name "*.py" ! -path "./docs/*" ! -path "./tests/*" \
	! -path "./.tox/*" ! -path "./pyvantagepro/__init__.py" ! -path "./requests/compat.py")

# hack: if pyflakes is available, set this to the location of pyflakes
# if it's not, e.g., in the Python 3 or PyPy Jenkins environments, set it to
# the location of the no-op `true` command.
PYFLAKES_IF_AVAILABLE=$(shell if which pyflakes > /dev/null ; \
	then which pyflakes; \
	else which true; fi )

test:
	tox

pyflakes:
	pyflakes ${PYFLAKES_WHITELIST}

docs:
	cd docs; make dirhtml

clean:
	git clean -Xfd
