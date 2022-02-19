#!/bin/bash

ATS_DOCKER_TAG=debian11
# ATS_DOCKER_TAG=alma8-pgsql13

if [ $# -gt 0 ]; then
    ATS_DOCKER_TAG=$1
fi

ATS_DOCKERFILE=Dockerfile.${ATS_DOCKER_TAG}

docker build -t dictoss/ats:${ATS_DOCKER_TAG} - < ${ATS_DOCKERFILE}
