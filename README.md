# active-task-summary

a web application of input and summary task time by team member.

# Current Stable Version

- 0.8.0 (use django-2.2, require python3.5+)
- 0.6.0 (use django-1.11, require python2.7 or python3.5+)

# Develop Environment

## for 0.8.x series

- Debian GNU/Linux 10 (buster) amd64
- Django 2.2 and 3.0
- python 3.7.3
- apache 2.4
- python3-psycopg2 2.6.2
- postgresql-11

## for 0.6.x series

- Debian GNU/Linux 9 (stretch) amd64
- Django 1.11
- python 2.7.13 and 3.5.3
- apache 2.4
- python-psycopg2 and python3-psycopg2 2.6.2
- postgresql-9.6 (from pgdg)

# NOTICE

This application used Django and must use postgresql.
(If you use sqlite3 or mysql, it is not work to GROUP BY.)

# ToDo

- management to master record.
- user permission and filter.
- brush up site design.

# Install

see docs/INSTALL.md file.

# Screenshot

![summary_project](docs/screenshot/summary_project.png "summary project form")
![regist](docs/screenshot/regist.png "regist form")
