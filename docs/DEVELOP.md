# DEVELOP INFOMATION

## unittest

- run unittest 

`$ python3 -Wd manage.py test -v2 ats`

- coverage tool

  - use coverage.py
  - see https://docs.djangoproject.com/ja/2.2/topics/testing/advanced/#integration-with-coverage-py
  - install coverage

`$ sudo pip3 install coverage`

  - run unittest

`$ coverage run --source='.' manage.py test -v2 ats`
`$ coverage report`
