#
# Dockerfile for ats.
#
FROM debian:10

RUN apt-get update

# for ats

RUN apt-get install -y locales git
RUN apt-get clean
RUN echo "ja_JP.UTF-8 UTF-8" > /etc/locale.gen
RUN locale-gen

# for web application.
RUN apt-get install -y python python-dev python-setuptools python-pip libpq-dev python-psycopg2
# RUN apt-get install -y apache2 libapache2-mod-wsgi-py3
RUN apt-get clean

RUN apt-get install -y postgresql-11
RUN apt-get clean

# setup user account for unittest.
USER postgres
RUN pg_ctlcluster 11 main start && \
    psql --command="CREATE USER webapp WITH SUPERUSER PASSWORD 'password'" && \
    createdb --encoding=UTF8 --owner=webapp ats
USER root

# execute mysql-server on start docker image.
# CMD ["/usr/lib/postgresql/11/bin/postgres", "-D", "/var/lib/postgresql/11/main", "-c", "config_file=/etc/postgresql/11/main/postgresql.conf"]
