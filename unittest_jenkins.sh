#!/bin/bash

# check python versi.on
python -V

# install libraries.
pip install -U -r requirements.txt

# create migrate file
python manage.py makemigrations ats

# execute unittest
python manage.py jenkins ats --enable-coverage --settings=toolproj.settings_jenkins
