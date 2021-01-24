# changelog

## version 0.6.1

- drop support django-1.8. If use python2.7, use 0.6.x branch and django-1.11.

## version 0.6.0

- upgrade jquery-3.3.1

## version 0.5.0

- support debian 9 (stretch)
  - drop support debian 8 (jessie)
  - support python2.7 and python3.5, drop support python3.4
  - require upgrade "psycopg2-2.6.2"

- change supported django version.
  - supported django-1.11 and django-2.0
  - drop support django-1.8

## version 0.4.0

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

## version 0.3.0

- show month summary in summary project.
- show month summary graph in summary project.
- add checkbox 'show task detail' in project summary.
  - improve performance.
- adjust word.
- add installation guide. see INSTALL.md


## version 0.2.0

- implement regist and summary.
- implement a part of manage. (change password)


## version 0.1.0

  - initial release.
