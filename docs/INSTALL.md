# How to install

## require application

- apache-2.2+
- postgresql-9+
- python-2.7 or python-3.4+
- wsgi-4.3+
- psycopg2


## install for debian-8 (jessie)

### get source code

<pre>

$ sudo apt-get update
$ sudo apt-get install git
$ cd ~/
$ mkdir work
$ cd work
$ git clone https://github.com/dictoss/active-task-summary.git
$ cd active-task-summary

</pre>

### install modules and librairies
- for use python-2.7

<pre>

$ sudo apt-get install python python-pip apache2 libapache2-mod-wsgi python-psycopg2
$ sudo pip2 install -r requirements.txt

</pre>

- for use python-3.4

<pre>

$ sudo apt-get install python3.4 python3-pip apache2 libapache2-mod-wsgi-py3 python3-psycopg2
$ sudo pip3 install -r requirements.txt

</pre>

### install database

<pre>

$ sudo apt-get install postgresql-9.4
$ sudo -u postgres /usr/lib/postgresql/9.4/bin/createuser --createdb --pwprompt --superuser webapp
Password:
$ sudo -u postgres /usr/lib/postgresql/9.4/bin/createdb --encoding=UTF8 --owner=webapp ats
$ psql -h 127.0.0.1 -U webapp -W ats
Password:
ats=# \q

</pre>


### deploy app

<pre>

$ sudo mkdir -p /var/www/wsgi_apps
$ pwd
~/work/active-task-summary
$ cd ..
$ sudo cp -rf active-task-summary /var/www/wsgi_apps/
$ cd /var/www/wsgi_apps/active-task-summary
$ sudo find . -name "*.pyc" -delete
$ sudo find . -name "*_devel.py" -delete

</pre>

### modify config

<pre>

$ sudo vi toolproj/settings.py
$ sudo vi ats/ats_settings.py

</pre>

### create log and eggs directory

<pre>

$ sudo mkdir /var/log/ats
$ sudo chown -fR www-data:www-data /var/log/ats
$ sudo mkdir /var/www/eggs
$ sudo chown -fR www-data:www-data /var/www/eggs

</pre>

### setup wsgi deamon used apache2.

<pre>

$ cd ~/work/active-task-summary
$ cd conf
$ sudo cp wsgi_apache2_ats.conf.debian8.sample /etc/apache2/conf-available/wsgi_ats.conf
$ sudo /usr/sbin/a2enconf wsgi_ats.conf
$ sudo service apache2 reload

</pre>

### check exec application

<pre>

$ ps ax | grep wsgi
9907 ?        Sl     0:00 (wsgi:ats)        -k start

</pre>

### try login

- curl -v http://localhost/toolproj/ats/login/

---
