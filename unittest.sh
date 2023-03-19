#!/bin/bash

TEST_MODE=
APP_NAME=ats
BIN_PYTHON=python3
BIN_PIP=pip3
APP_ENV=test

function has_pip_break_system_packages {
    if [ ! -e "/etc/debian_version" ]; then
        return 0
    fi

    # for debian/ubuntu.  ex) Python 3.11.2
    python3_ver=`/usr/bin/python3 --version | sed -e 's/Python //g'`
    ver_list=(${python3_ver//./ })
    python3_ver_minor=${ver_list[1]}

    if [ ${python3_ver_minor} -lt 11 ]; then
        return 0
    else
        return 1
    fi
}

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
    has_pip_break_system_packages
    func_ret=$?

    if [ ${func_ret} -eq 0 ]; then
        ${BIN_PIP} install -U -r requirements.txt
        ${BIN_PIP} install -U -r requirements_dev.txt
    else
        PIP_OPT_PEP668="--break-system-packages"

        ${BIN_PIP} install -U -r requirements.txt ${PIP_OPT_PEP668}
        ${BIN_PIP} install -U -r requirements_dev.txt ${PIP_OPT_PEP668}
    fi

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
PYTHONWARNINGS=default coverage run --source='.' manage.py test -v2 ${APP_NAME}
RET=$?
echo "unittest result code: ${RET}"
coverage report
coverage xml
coverage html
exit ${RET}
