# How to install for ver 0.8.2

## require application

- apache-2.2+
- postgresql-9.6+
- python-3.5+
- psycopg2.6.2+
- wsgi-4.5.11+
- django-2.2.*

## install target

- [CentOS 6](#install-for-centos-6)

---

## install for CentOS-6

### instsall external repo

 - use postgresql-9.6, so same version on debian-9's official package.

<pre>

$ sudo yum check-update
$ sudo yum install epel-release
$ sudo rpm -ivh https://dl.iuscommunity.org/pub/ius/stable/CentOS/6/x86_64/ius-release-1.0-15.ius.centos6.noarch.rpm
$ sudo rpm -ivh https://download.postgresql.org/pub/repos/yum/9.6/redhat/rhel-6-x86_64/pgdg-centos96-9.6-3.noarch.rpm
$ sudo yum check-update

</pre>

### get source code

<pre>

$ sudo yum install --enablerepo=ius git2u
$ cd ~/
$ mkdir work
$ cd work
$ git clone https://github.com/dictoss/active-task-summary.git
$ cd active-task-summary

</pre>


### install database

<pre>

$ sudo yum install --enablerepo=pgdg96 postgresql96-server postgresql96-devel
$ sudo service postgresql-9.6 initdb
$ sudo vi /var/lib/pgsql/9.6/data/pg_hba.conf
host    all             all             127.0.0.1/32            md5
$ sudo service postgresql-9.6 restart
$ sudo -u postgres /usr/pgsql-9.6/bin/createuser --createdb --pwprompt --superuser webapp
Password:
$ sudo -u postgres /usr/pgsql-9.6/bin/createdb --encoding=UTF8 --owner=webapp ats
$ psql -h 127.0.0.1 -U webapp -W ats
Password:
ats=# \q

</pre>


### install modules and librairies

- for use python-3.5

<pre>

$ sudo yum install httpd mod_ssl
$ sudo yum install gcc make
$ sudo yum install --enablerepo=ius python35u python35u-pip python35u-mod_wsgi python35u-devel
$ sudo -s
# export PATH="/usr/pgsql-9.6/bin:$PATH"
# pip3.5 install -r requirements.txt

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

</pre>

### modify config

<pre>

$ sudo vi toolproj/settings/production.py
$ sudo vi ats/apps/ats_production.py

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
$ sudo cp wsgi_apache2_ats.conf.cent6.sample /etc/httpd/conf.d/wsgi_ats.conf

</pre>

- for use python-3.5

<pre>

$ sudo vi /etc/httpd/conf.d/wsgi-python3.5.conf
<IfModule !wsgi_module>
    LoadModule wsgi_module modules/mod_wsgi_python3.5.so
    WSGISocketPrefix run/wsgi
    WSGIScriptReloading On
</IfModule>

</pre>

<pre>

$ sudo service httpd restart

</pre>

### link static file in webapplication.

<pre>

$ sudo mkdir /var/www/html/static
$ cd /var/www/html/static
$ sudo ln -sf /var/www/wsgi_apps/active-task-summary/ats/static ats

</pre>

- for use python-3.5

<pre>

$ sudo ln -sf /usr/lib/python3.5/site-packages/django/contrib/admin/static/admin admin

</pre>


### create database schema for web application

- for use python-3.5

<pre>

$ cd /var/www/wsgi_apps/active-task-summary
$ sudo -u apache python3.5 manage.py makemigrations
$ sudo -u apache python3.5 manage.py migrate auth
$ sudo -u apache python3.5 manage.py migrate
$ sudo -u apache python3.5 manage.py createsuperuser

</pre>


### check exec application

<pre>

$ ps ax | grep wsgi | grep -v grep
 2486 ?        Sl     0:00 (wsgi:ats)

</pre>


### try login

- curl -v http://localhost/toolproj/ats/login/
