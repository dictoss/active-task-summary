#!/bin/bash

ATS_PGSQL_VERSION=13

ATS_DOCKER_TAG=debian11
# ATS_DOCKER_TAG=alma8-pgsql13

if [ $# -gt 0 ]; then
    ATS_DOCKER_TAG=$1
fi

if [ $# -gt 1 ]; then
    ATS_PGSQL_VERSION=$2
fi

if [[ "${ATS_DOCKER_TAG}" =~ "debian" ]]; then
    ATS_PG_CTLCLUSTER_PATH="pg_ctlcluster ${ATS_PGSQL_VERSION} main "
else
    ATS_PG_CTLCLUSTER_PATH="sudo -u postgres /usr/pgsql-${ATS_PGSQL_VERSION}/bin/pg_ctl -D /var/lib/pgsql/${ATS_PGSQL_VERSION}/data"
fi

#docker run -v ${JENKINS_HOME}/workspace/${JOB_NAME}:/mnt dictoss/ats:${ATS_DOCKER_TAG} \
docker run dictoss/ats:${ATS_DOCKER_TAG} \
    sh -c "${ATS_PG_CTLCLUSTER_PATH} start && \
    git clone https://github.com/dictoss/active-task-summary.git && \
    cd active-task-summary && \
    sh unittest.sh jenkins-docker && \
    cp -fv coverage.xml /mnt/"
