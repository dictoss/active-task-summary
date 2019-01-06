# DEVELOP INFOMATION

## unittest

- run unittest 

`$ python3 manage.py test ats --settings=toolproj.settings_test`

- coverage tool

  - use coverage.py
  - see https://docs.djangoproject.com/ja/2.1/topics/testing/advanced/#integration-with-coverage-py
  - install coverage

`$ sudo pip3 install coverage`

  - run unittest

`$ coverage run --source='.' manage.py test --settings=toolproj.settings_test`
`$ coverage report`
