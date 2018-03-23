#!/bin/bash

# check python versi.on
python -V

# install libraries.
pip install -U requirements.txt

# execute unittest
python manage.py test ats --settings=toolproj.settings_test
