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


### link static file in webapplication.

<pre>

$ sudo mkdir /var/www/html/static
$ cd /var/www/html/static
$ sudo ln -sf /var/www/wsgi_apps/active-task-summary/ats/static ats

- for use python-2.7
$ sudo ln -sf /usr/local/lib/python2.7/dist-packages/django/contrib/admin/static/admin admin

- for use python-3.4
$ sudo ln -sf /usr/local/lib/python3.4/dist-packages/django/contrib/admin/static/admin admin

</pre>


### create database schema for web application

<pre>

- for use python-2.7
$ cd /var/www/wsgi_apps/active-task-summary
$ sudo -u www-data python2.7 manage.py makemigrations
$ sudo -u www-data python2.7 manage.py migrate auth
$ sudo -u www-data python2.7 manage.py migrate
$ sudo -u www-data python2.7 manage.py createsuperuser

- for use python-3.4
$ cd /var/www/wsgi_apps/active-task-summary
$ sudo -u www-data python3.4 manage.py makemigrations
$ sudo -u www-data python3.4 manage.py migrate auth
$ sudo -u www-data python3.4 manage.py migrate
$ sudo -u www-data python3.4 manage.py createsuperuser

</pre>


### check exec application

<pre>

$ ps ax | grep wsgi
9907 ?        Sl     0:00 (wsgi:ats)        -k start

</pre>

### try login

- curl -v http://localhost/toolproj/ats/login/

---

## install for CentOS-6

### instsall external repo

<pre>

$ sudo yum check-update
$ sudo yum install epel-release
$ sudo rpm -ivh https://dl.iuscommunity.org/pub/ius/stable/CentOS/6/x86_64/ius-release-1.0-14.ius.centos6.noarch.rpm
$ sudo rpm -ivh https://download.postgresql.org/pub/repos/yum/9.4/redhat/rhel-6-x86_64/pgdg-centos94-9.4-3.noarch.rpm
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

$ sudo yum install --enablerepo=pgdg94 postgresql94-server postgresql94-devel
$ sudo service postgresql-9.4 initdb
$ sudo vi /var/lib/pgsql/9.4/data/pg_hba.conf
host    all             all             127.0.0.1/32            md5
$ sudo service postgresql-9.4 restart
$ sudo -u postgres /usr/pgsql-9.4/bin/createuser --createdb --pwprompt --superuser webapp
Password:
$ sudo -u postgres /usr/pgsql-9.4/bin/createdb --encoding=UTF8 --owner=webapp ats
$ psql -h 127.0.0.1 -U webapp -W ats
Password:
ats=# \q

</pre>


### install modules and librairies
- for use python-2.7

<pre>

$ sudo yum install httpd mod_ssl
$ sudo yum install gcc make
$ sudo yum install --enablerepo=ius python27 python27-pip python27-mod_wsgi python27-devel
$ sudo -s
\# export PATH="/usr/pgsql-9.4/bin:$PATH"
\# pip2.7 install -r requirements.txt

</pre>


- for use python-3.5

<pre>

$ sudo yum install httpd mod_ssl
$ sudo yum install gcc make
$ sudo yum install --enablerepo=ius python35u python35u-pip python35u-mod_wsgi python35u-devel
$ sudo -s
\# export PATH="/usr/pgsql-9.4/bin:$PATH"
\# pip3.5 install -r requirements.txt

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
$ sudo chown -fR apache:apache /var/log/ats
$ sudo mkdir /var/www/eggs
$ sudo chown -fR apache:apache /var/www/eggs

</pre>


### setup wsgi deamon used apache2.

<pre>

$ cd ~/work/active-task-summary
$ cd conf
$ sudo cp wsgi_apache2_ats.conf.cent6.sample /etc/httpd/conf.d/wsgi_ats.conf

- for use python-2.7
$ sudo vi /etc/httpd/conf.d/python27-mod_wsgi.conf

<IfModule !python_module>
    <IfModule !wsgi_module>
        LoadModule wsgi_module modules/python27-mod_wsgi.so
        WSGISocketPrefix run/wsgi
        WSGIScriptReloading On
    </IfModule>
</IfModule>

- for use python-3.5
$ sudo vi /etc/httpd/conf.d/wsgi-python3.5.conf
<IfModule !wsgi_module>
    LoadModule wsgi_module modules/mod_wsgi_python3.5.so
    WSGISocketPrefix run/wsgi
    WSGIScriptReloading On
</IfModule>

$ sudo service httpd restart

</pre>


### link static file in webapplication.

<pre>

$ sudo mkdir /var/www/html/static
$ cd /var/www/html/static
$ sudo ln -sf /var/www/wsgi_apps/active-task-summary/ats/static ats

- for use python-2.7
$ sudo ln -sf /usr/lib/python2.7/site-packages/django/contrib/admin/static/admin admin

- for use python-3.5
$ sudo ln -sf /usr/lib/python3.5/site-packages/django/contrib/admin/static/admin admin

</pre>


### create database schema for web application

<pre>

- for use python-2.7
$ cd /var/www/wsgi_apps/active-task-summary
$ sudo -u apache python2.7 manage.py makemigrations
$ sudo -u apache python2.7 manage.py migrate auth
$ sudo -u apache python2.7 manage.py migrate
$ sudo -u apache python2.7 manage.py createsuperuser

- for use python-3.5
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

---
