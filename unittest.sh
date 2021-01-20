#!/bin/bash

TEST_MODE=

if [ $# -gt 0 ]; then
    TEST_MODE=$1
fi

if [ "${TEST_MODE}" = "jenkins" ]; then
    # check python version
    python -V

    # install libraries.
    pip install -U -r requirements.txt

    # create migrate file
    python manage.py makemigrations ats --settings=toolproj.settings_test
elif  [ "${TEST_MODE}" = "jenkins-docker" ]; then
    echo "test mode is jenkins-docker, running..."

    # check python version
    python3 -V

    # install libraries.
    pip3 install -U -r requirements.txt
    pip3 install -U -r requirements_dev.txt

    # create diretory.
    mkdir -p ~/log

    # create migrate file
    python3 manage.py makemigrations ats --settings=toolproj.settings_test
fi

# execute unittest
coverage run --source='.' manage.py test -v3 ats --settings=toolproj.settings_test
RET=$?
echo "unittest result code: ${RET}"
coverage report
coverage xml
exit ${RET}
