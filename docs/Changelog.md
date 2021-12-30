# changelog

- [version 3.x](#version-3x)
- [version 2.x](#version-2x)
- [version 1.x](#version-1x)
- [version 0.8.x](#version-08x)
- [version 0.6.x](#version-06x)
- [old version](#old-version)

## version 3.x

### version 3.1.0

- enhancement
  - #44 add user-defined columns on Task Table.
  - #45 write comment on the regist screen.
  - #46 improved performance on checkbox event in javascript.

### version 3.0.0

- major release.
  - The verion 3.0 series is the successor to 2.0.x.
  - require python-3.6 or higher, and Django-3.2.
  - upgrade dependency libraries and packages.
- supports the following operating systems.
  - debian-11
  - debian-10
  - AlmaLinux-8
  - CentOS-7.7+
- drop support operation system.
  - debian-9

## version 2.x

### version 2.0.1

- bugfix
  - fix #43 error makemigrations to 1.0.0 from 0.6.1.

### version 2.0.0

- major release.
  - The verion 2.0 series is the successor to 0.8.x.
  - require python-3.5 or higher, and Django-2.2.
- enhancement
  - fix #15 (Add multiple ProjectWorker models on admin project window at one time.)
  - fix #27 (insert ,update and delete multiple tasks on admin job model at once)
  - fix #28
    - add code colmun on project summary and user summary.
    - add ExternalProject and ForeignKey.
  - fix #29 (export csv file with task detail data on Summary User.)
  - fix #34 (add filter job on admin task model.)
  - fix #35 (update jquery-3.6.0)
  - fix #37 (can hidden default super user name.)
- refactoring
  - fix #38 (use AUTH_PASSWORD_VALIDATORS on password change window.)
- bugfix
  - fix #36 (add @login_required decorator)

## version 1.x

### version 1.1.0

- enhancement
  - #44 add user-defined columns on Task Table.
  - #45 write comment on the regist screen.
  - #46 improved performance on checkbox event in javascript.

### version 1.0.1

- bugfix
  - fix #43 error makemigrations to 1.0.0 from 0.6.1.

### version 1.0.0

- major release.
  - The verion 1.0 series is the successor to 0.6.x.
  - require python-2.7, and Django-1.11.
- backport 2.0.0.
  - enhancement
    - fix #15 (Add multiple ProjectWorker models on admin project window at one time.)
    - fix #27 (insert ,update and delete multiple tasks on admin job model at once)
    - fix #28
      - add code colmun on project summary and user summary.
      - add ExternalProject and ForeignKey.
    - fix #29 (export csv file with task detail data on Summary User.)
    - fix #34 (add filter job on admin task model.)
    - fix #35 (update jquery-3.6.0)
    - fix #37 (can hidden default super user name.)
  - refactoring
    - fix #38 (use AUTH_PASSWORD_VALIDATORS on password change window.)
  - bugfix
    - fix #36 (add @login_required decorator)


## version 0.8.x

### version 0.8.2

- bugfix.
  - #30 migrate django.db.backends.postgresql_psycopg2
  - #31 move apps AtsConfig from ats_settings.py.
- refactoring.
  - update comment based django-1.11. (before django-1.6)
  - add apps.py and apps directory. based on django-1.11.
  - support multiple app.
    - fix move to ats/static/ats/* from ats/static/* .
    - fix move to ats/templates/ats/* from ats/templates/* .
- install.
  - change install operation.
    - require symblic link to toolproj/settins/__init__.py.
    - require symblic link to ats/apps/__init__.py.
- change target system.
  - require centos-7.7 or higher.
    - Sinse centos-7.7, added python3 package (python3.6) on base. no require ius.
  - drop support centos-6 (2020-11-30 EoL ended)

### version 0.8.1

- refactoring.
  - use reverse().
  - fix pep8.
  - fix handler404 and handler500.
  - use LOGGING.
  - replace BigAutoField.
  - remove unuse files.
- add more test code.
- add Dockerfile for jenkins and docker at same host.
- fix apache wsgi config.

### version 0.8.0

- support debian 10 (buster).
  - continue support debian 9 (stretch).
  - support python3.5+. python 3.7 is also supported.

- change supported django version.
  - supported django-2.2 and django-3.0.
  - drop support django-1.11.

### version 0.7.0

- drop support python2.7.
  - suupport python3.5+.

- change supported django version.
  - supported django-1.11 and django-2.2.
  - drop support django-2.0.

## version 0.6.x (LTS)

### version 0.6.3

- backport 0.8.2 with support python2.7 and django-1.11.
  - bugfix.
    - #30 migrate django.db.backends.postgresql_psycopg2
    - #31 move apps AtsConfig from ats_settings.py.
  - refactoring.
    - update comment based django-1.11. (before django-1.6)
    - add apps.py and apps directory. based on django-1.11.
    - support multiple app.
      - fix move to ats/static/ats/* from ats/static/* .
      - fix move to ats/templates/ats/* from ats/templates/* .
  - install.
    - change install operation.
      - require symblic link to toolproj/settins/__init__.py.
      - require symblic link to ats/apps/__init__.py.
  - change target system.
    - require centos-7.7 or higher.
      - Sinse centos-7.7, added python3 package (python3.6) on base. no require ius.
    - drop support centos-6 (2020-11-30 EoL ended)

### version 0.6.2

- backport 0.8.1 with support python2.7 and django-1.11.
  - refactoring.
    - use reverse().
    - fix pep8.
    - fix handler404 and handler500.
    - use LOGGING.
    - replace BigAutoField.
    - remove unuse files.
  - add more test code.
  - add Dockerfile for jenkins and docker at same host.
  - fix apache wsgi config.

### version 0.6.1

- drop support django-1.8. If use python2.7, use 0.6.x branch and django-1.11.

### version 0.6.0

- upgrade jquery-3.3.1

## old version

### version 0.5.0

- support debian 9 (stretch)
  - drop support debian 8 (jessie)
  - support python2.7 and python3.5, drop support python3.4
  - require upgrade "psycopg2-2.6.2"

- change supported django version.
  - supported django-1.11 and django-2.0
  - drop support django-1.8

### version 0.4.0

- change supported django version.
  - supported django-1.8 and django-1.11.
  - drop support django-1.6.

- detail for update and fix.
  - fix #5  double post when quick double press regist button at /regist
  - fix #6  reverse sort order on job-sortkey in exist data this day table at /regist
  - fix #7  want to improve select speed "exist data this day"
  - fix #8  add repoert [project,job,year,month] at /summary/job
  - fix #9  add repoert [project,job,year,month] at /summary/project
  - fix #10 support django-1.11

### version 0.3.0

- show month summary in summary project.
- show month summary graph in summary project.
- add checkbox 'show task detail' in project summary.
  - improve performance.
- adjust word.
- add installation guide. see INSTALL.md


### version 0.2.0

- implement regist and summary.
- implement a part of manage. (change password)


### version 0.1.0

  - initial release.
