#!/bin/bash

TEST_MODE=
APP_NAME=ats
BIN_PYTHON=python
BIN_PIP=pip
APP_ENV=test

if [ $# -gt 0 ]; then
    TEST_MODE=$1
fi

if [ "${TEST_MODE}" = "jenkins" ]; then
    # check python version
    python -V

    # install libraries.
    pip install -U -r requirements.txt

    # create migrate file
    python manage.py makemigrations ats --settings=toolproj.settings.test
elif  [ "${TEST_MODE}" = "jenkins-docker" ]; then
    echo "test mode is jenkins-docker, running..."

    # check python version
    ${BIN_PYTHON} -V

    # install libraries.
    ${BIN_PIP} install -U -r requirements.txt
    ${BIN_PIP} install -U -r requirements_dev.txt

    # create diretory.
    mkdir -p ~/log

    # create symlink for settings and app_settings.
    cd toolproj/settings
    ln -fs ${APP_ENV}.py __init__.py

    cd ../../
    cd ats/apps
    ln -fs apps_${APP_ENV}.py __init__.py

    cd ../../

    # create migrate file
    ${BIN_PYTHON} manage.py makemigrations ats
fi

# execute unittest
coverage run --source='.' manage.py test -v2 ${APP_NAME}
RET=$?
echo "unittest result code: ${RET}"
coverage report
coverage xml
coverage html
exit ${RET}
