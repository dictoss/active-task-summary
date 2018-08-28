#!/bin/bash

# check python versi.on
python -V

# install libraries.
pip install -U -r requirements.txt

# create migrate file
python manage.py makemigrations ats

# execute unittest
python manage.py test ats --settings=toolproj.settings_test
