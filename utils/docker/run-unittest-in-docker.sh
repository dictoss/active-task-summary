#!/bin/bash

#docker run -v ${JENKINS_HOME}/workspace/${JOB_NAME}:/mnt dictoss/ats:debian10 \
docker run dictoss/ats:debian10 \
    sh -c "pg_ctlcluster 11 main start && \
    git clone https://github.com/dictoss/active-task-summary.git && \
    cd active-task-summary && \
    sh unittest.sh jenkins-docker && \
    cp -fv coverage.xml /mnt/"
