# How to install for ver 4.0.0

## require application

- apache-2.4+
- python-3.8+ (use django-4.2, require python-3.8+)
- wsgi-4.5.11+
- django-4.2.*
- postgresql-12+
- psycopg-2.8.6+ (use python-3.11, require psycopg-2.9.5+)


## install target

- [Debian GNU/Linux 11](#install-for-debian-11-bullseye)
- [AlmaLinux 8](#install-for-almalinux-8)

---

## install for debian-11 (bullseye)

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


### install database

<pre>

$ sudo apt-get install postgresql-13
$ sudo -u postgres /usr/lib/postgresql/13/bin/createuser --createdb --pwprompt --superuser webapp
Password:
$ sudo -u postgres /usr/lib/postgresql/13/bin/createdb --encoding=UTF8 --owner=webapp ats
$ psql -h 127.0.0.1 -U webapp -W ats
Password:
ats=# \q

</pre>


### install modules and librairies

<pre>

$ sudo apt-get install python3 python3-pip python3-psycopg2 apache2 libapache2-mod-wsgi-py3
$ sudo pip3 install -r requirements.txt

</pre>


### deploy app

<pre>

$ sudo mkdir -p /var/www/wsgi_apps
$ pwd
~/work/active-task-summary
$ cd ..
$ sudo cp -rf active-task-summary /var/www/wsgi_apps/
$ cd /var/www/wsgi_apps
$ sudo chown -fR www-data:www-data active-task-summary
$ cd active-task-summary
$ cd toolproj/settings
$ sudo ln -fs production.py __init__.py
$ cd ../..
$ cd ats/apps
$ sudo ln -fs apps_production.py __init__.py

</pre>


### modify config

<pre>

$ sudo vi toolproj/settings/production.py
$ sudo vi ats/apps/apps_production.py

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
$ sudo cp wsgi_apache2_ats.conf.debian11.sample /etc/apache2/conf-available/wsgi_ats.conf
$ sudo /usr/sbin/a2enconf wsgi_ats.conf
$ sudo service apache2 reload

</pre>


### link static file in webapplication.

<pre>

$ sudo mkdir /var/www/html/static
$ cd /var/www/html/static
$ sudo ln -sf /var/www/wsgi_apps/active-task-summary/ats/static/ats ats

</pre>

<pre>

$ sudo ln -sf /usr/local/lib/python3.9/dist-packages/django/contrib/admin/static/admin admin

</pre>


### create database schema for web application

<pre>

$ cd /var/www/wsgi_apps/active-task-summary
$ sudo -u www-data python3 manage.py makemigrations ats
$ sudo -u www-data python3 manage.py migrate
$ sudo -u www-data python3 manage.py createsuperuser

</pre>


### compile message catalogs

<pre>

$ sudo -u www-data python3 manage.py compilemessages

</pre>

### check exec application

<pre>

$ ps ax | grep wsgi
9907 ?        Sl     0:00 (wsgi:ats)        -k start

</pre>

### try login

- curl -v http://localhost/toolproj/ats/login/

---

## install for AlmaLinux-8

### install external repo

<pre>

$ sudo dnf check-update
$ sudo dnf install https://download.postgresql.org/pub/repos/yum/reporpms/EL-8-x86_64/pgdg-redhat-repo-latest.noarch.rpm
$ sudo dnf check-update

</pre>


### get source code

<pre>

$ sudo yum install git
$ cd ~/
$ mkdir work
$ cd work
$ git clone https://github.com/dictoss/active-task-summary.git
$ cd active-task-summary

</pre>


### install database

<pre>

$ sudo dnf -qy module disable postgresql
$ sudo dnf install --enablerepo=pgdg13 postgresql13-server postgresql13-devel
$ sudo /usr/pgsql-13/bin/postgresql-13-setup initdb
$ sudo vi /var/lib/pgsql/13/data/pg_hba.conf
host    all             all             127.0.0.1/32            scram-sha-256
$ sudo systemctl restart postgresql-13
$ sudo -u postgres /usr/pgsql-13/bin/createuser --createdb --pwprompt --superuser webapp
Password:
$ sudo -u postgres /usr/pgsql-13//bin/createdb --encoding=UTF8 --owner=webapp ats
$ psql -h 127.0.0.1 -U webapp -W ats
Password:
ats=# \q

</pre>


### install modules and librairies

- for use python-3.9

<pre>

$ sudo dnf install gcc make
$ sudo dnf module enable httpd:2.4
$ sudo dnf install httpd
$ sudo dnf module enable python39
$ sudo dnf install python39 python39-devel python39-setuptools python39-pip python39-mod_wsgi
$ sudo -s
# export PATH="/usr/pgsql-13/bin:$PATH"
# pip3.9 install -r requirements.txt

</pre>


### deploy app

<pre>

$ sudo mkdir -p /var/www/wsgi_apps
$ pwd
~/work/active-task-summary
$ cd ..
$ sudo cp -rf active-task-summary /var/www/wsgi_apps/
$ cd /var/www/wsgi_apps
$ sudo chown -fR apache:apache active-task-summary
$ cd active-task-summary
$ cd toolproj/settings
$ sudo ln -fs production.py __init__.py
$ cd ../..
$ cd ats/apps
$ sudo ln -fs apps_production.py __init__.py
$ cd ../..

</pre>

### modify config

<pre>

$ sudo vi toolproj/settings/production.py
$ sudo vi ats/apps/apps_production.py

</pre>


### create log and eggs directory

<pre>

$ sudo mkdir /var/log/ats
$ sudo chown -fR apache:apache /var/log/ats
$ sudo mkdir /var/www/eggs
$ sudo chown -fR apache:apache /var/www/eggs

</pre>


### setup wsgi deamon used apache2.

<pre>

$ cd ~/work/active-task-summary
$ cd conf
$ sudo cp wsgi_apache2_ats.conf.almalinux8.sample /etc/httpd/conf.d/wsgi_ats.conf

</pre>

- for use python-3.9

<pre>

$ sudo vi /etc/httpd/conf.modules.d/10-wsgi-python3.conf

<IfModule !wsgi_module>
    LoadModule wsgi_module modules/mod_wsgi_python3.so
    WSGISocketPrefix run/wsgi
    WSGIScriptReloading On
</IfModule>

</pre>

<pre>

$ sudo apachectl configtest
Syntax OK
$ sudo systemctl restart httpd

</pre>

### link static file in webapplication.

<pre>

$ sudo mkdir /var/www/html/static
$ cd /var/www/html/static
$ sudo ln -sf /var/www/wsgi_apps/active-task-summary/ats/static/ats ats

</pre>

- for use python-3.9

<pre>

$ cd /var/www/html/static
$ sudo ln -sf /usr/local/lib/python3.9/site-packages/django/contrib/admin/static/admin admin

</pre>


### create database schema for web application

- for use python-3.9

<pre>

$ cd /var/www/wsgi_apps/active-task-summary
$ sudo -u apache python3.9 manage.py makemigrations ats
$ sudo -u apache python3.9 manage.py migrate
$ sudo -u apache python3.9 manage.py createsuperuser

</pre>

### compile message catalogs

<pre>

$ sudo -u apache python3.9 manage.py compilemessages

</pre>

### check exec application

<pre>

$ ps ax | grep wsgi | grep -v grep
16247 ?        Sl     0:00 (wsgi:ats)      -DFOREGROUND

</pre>


### try login

- curl -v http://localhost/toolproj/ats/login/
