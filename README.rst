active-task-summary
===================
a web application of input and summary task time by team member.

Current Development Version
====================================
0.7.0 (will support django-2.2)

Current Stable Version
==================================
0.6.0

Develop Environment
===================
- Debian GNU/Linux 9 (stretch) amd64
- Django 2.2 and 1.11
- python 2.7.13 and 3.5.3
- apache 2.4
- python-psycopg2 and python3-psycopg2 2.6.2
- postgresql-9.6 (from pgdg)

NOTICE
===================
This application used Django and must use postgresql.
(If you use sqlite3 or mysql, it is not work to GROUP BY.)

ToDo
===================
- management to master record.
- user permission and filter.
- brush up site design.

Install
===================
see docs/INSTALL.md file.

Screenshot
===================
![summary_project](docs/screenshot/summary_project.png "summary project form")
![regist](docs/screenshot/regist.png "regist form")
