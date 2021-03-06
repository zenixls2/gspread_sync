#!/bin/bash
SCRIPT=`realpath $0`
SCRIPT_DIR=`dirname $SCRIPT`
cd $SCRIPT_DIR/.. && python setup.py sdist bdist_wheel && twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
