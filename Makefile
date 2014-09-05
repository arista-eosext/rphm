#!/usr/bin/make
# WARN: gmake syntax
########################################################
# Makefile for triggertrap extension
#
# useful targets:
#   make clean ----- cleans distutils
#   make install --- installs python modules
#   make pylint ---- source code checks
#   make rpm  ------ produce RPMs
#   make sdist ----- builds a source distribution
#   make tests ----- run the tests
#   make coverage -- run the tests and analyze code coverage
#
########################################################
# variable section

NAME = "triggertrap"

PYTHON=python
SITELIB = $(shell $(PYTHON) -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")

# VERSION file provides one place to update the software version
VERSION := $(shell cat VERSION)

# RPM build parameters
RPMSPECDIR = .
RPMSPEC = $(RPMSPECDIR)/triggertrap.spec
RPMRELEASE = 1
RPMNVR = "$(NAME)-$(VERSION)-$(RPMRELEASE)"

########################################################

all: clean python

pylint:
	find . -name \*.py | xargs pylint --rcfile .pylintrc

clean:
	@echo "---------------------------------------------"
	@echo "Cleaning up distutils stuff"
	@echo "---------------------------------------------"
	rm -rf build
	rm -rf dist
	rm -rf MANIFEST
	@echo "---------------------------------------------"
	@echo "Cleaning up rpmbuild stuff"
	@echo "---------------------------------------------"
	rm -rf rpmbuild
	@echo "---------------------------------------------"
	@echo "Cleaning up byte compiled python stuff"
	@echo "---------------------------------------------"
	find . -type f -regex ".*\.py[co]$$" -delete

tests: clean
	$(PYTHON) -m unittest discover ./test -v

coverage: clean
	PYTHONPATH=. nosetests --verbosity=3 -x --with-xunit \
			   --xunit-file=junit-report.xml  \
			   --with-coverage --cover-erase --cover-html \
			   --cover-package=triggertrap --cover-branches

report:
	coverage report -m

coverageclean:
	rm -rf cover
	rm .coverage

python:
	$(PYTHON) setup.py build

install:
	$(PYTHON) setup.py install

sdist: clean
	$(PYTHON) setup.py sdist
	#$(PYTHON) setup.py sdist -t MANIFEST.in

rpmcommon: sdist
	@mkdir -p rpmbuild
	@cp dist/*.gz rpmbuild/
	@sed -e 's#^Version:.*#Version: $(VERSION)#' -e 's#^Release:.*#Release: $(RPMRELEASE)#' $(RPMSPEC) >rpmbuild/$(NAME).spec

rpm: rpmcommon
	@rpmbuild --define "_topdir %(pwd)/rpmbuild" \
	--define "_builddir %{_topdir}" \
	--define "_rpmdir %{_topdir}" \
	--define "_srcrpmdir %{_topdir}" \
	--define "_specdir $(RPMSPECDIR)" \
	--define "_sourcedir %{_topdir}" \
	--define "_rpmfilename %%{NAME}-%%{VERSION}-%%{RELEASE}.rpm" \
	--define "__python /usr/bin/python" \
	-ba rpmbuild/$(NAME).spec
	@rm -f rpmbuild/$(NAME).spec
	@echo "---------------------------------------------"
	@echo "Triggertrap RPM is built:"
	@echo "    rpmbuild/$(RPMNVR).rpm"
	@echo "---------------------------------------------"

