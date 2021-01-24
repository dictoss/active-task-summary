# How to install for ver 0.6.2

## require application

- apache-2.2+
- postgresql-9.6+
- python-2.7 or python-3.5+
- psycopg2.8.6+
- wsgi-4.5.11
- django-1.11.29


## install target

- [Debian GNU/Linux 10](#install-for-debian-10-buster)
- [Debian GNU/Linux 9](#install-for-debian-9-stretch)
- [CentOS 6](#install-for-centos-6)
- [CentOS 7](#install-for-centos-7)

## install for debian-10 (buster)

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

$ sudo apt-get install postgresql-11
$ sudo -u postgres /usr/lib/postgresql/11/bin/createuser --createdb --pwprompt --superuser webapp
Password:
$ sudo -u postgres /usr/lib/postgresql/11/bin/createdb --encoding=UTF8 --owner=webapp ats
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

- for use python-3.7

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
$ sudo cp wsgi_apache2_ats.conf.debian10.sample /etc/apache2/conf-available/wsgi_ats.conf
$ sudo /usr/sbin/a2enconf wsgi_ats.conf
$ sudo service apache2 reload

</pre>


### link static file in webapplication.

<pre>

$ sudo mkdir /var/www/html/static
$ cd /var/www/html/static
$ sudo ln -sf /var/www/wsgi_apps/active-task-summary/ats/static ats

</pre>

- for use python-2.7

<pre>

$ sudo ln -sf /usr/local/lib/python2.7/dist-packages/django/contrib/admin/static/admin admin

</pre>

- for use python-3.7

<pre>

$ sudo ln -sf /usr/local/lib/python3.7/dist-packages/django/contrib/admin/static/admin admin

</pre>


### create database schema for web application

- for use python-2.7

<pre>

$ cd /var/www/wsgi_apps/active-task-summary
$ sudo -u www-data python2.7 manage.py makemigrations
$ sudo -u www-data python2.7 manage.py migrate auth
$ sudo -u www-data python2.7 manage.py migrate
$ sudo -u www-data python2.7 manage.py createsuperuser

</pre>

- for use python-3.7

<pre>

$ cd /var/www/wsgi_apps/active-task-summary
$ sudo -u www-data python3 manage.py makemigrations
$ sudo -u www-data python3 manage.py migrate auth
$ sudo -u www-data python3 manage.py migrate
$ sudo -u www-data python3 manage.py createsuperuser

</pre>


### check exec application

<pre>

$ ps ax | grep wsgi
9907 ?        Sl     0:00 (wsgi:ats)        -k start

</pre>

### try login

- curl -v http://localhost/toolproj/ats/login/

---

## install for debian-9 (stretch)

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

$ sudo apt-get install postgresql-9.6
$ sudo -u postgres /usr/lib/postgresql/9.6/bin/createuser --createdb --pwprompt --superuser webapp
Password:
$ sudo -u postgres /usr/lib/postgresql/9.6/bin/createdb --encoding=UTF8 --owner=webapp ats
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

- for use python-3.5

<pre>

$ sudo apt-get install python3.5 python3-pip apache2 libapache2-mod-wsgi-py3 python3-psycopg2
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
$ sudo cp wsgi_apache2_ats.conf.debian9.sample /etc/apache2/conf-available/wsgi_ats.conf
$ sudo /usr/sbin/a2enconf wsgi_ats.conf
$ sudo service apache2 reload

</pre>


### link static file in webapplication.

<pre>

$ sudo mkdir /var/www/html/static
$ cd /var/www/html/static
$ sudo ln -sf /var/www/wsgi_apps/active-task-summary/ats/static ats

</pre>

- for use python-2.7

<pre>

$ sudo ln -sf /usr/local/lib/python2.7/dist-packages/django/contrib/admin/static/admin admin

</pre>

- for use python-3.5

<pre>

$ sudo ln -sf /usr/local/lib/python3.5/dist-packages/django/contrib/admin/static/admin admin

</pre>


### create database schema for web application

- for use python-2.7

<pre>

$ cd /var/www/wsgi_apps/active-task-summary
$ sudo -u www-data python2.7 manage.py makemigrations
$ sudo -u www-data python2.7 manage.py migrate auth
$ sudo -u www-data python2.7 manage.py migrate
$ sudo -u www-data python2.7 manage.py createsuperuser

</pre>

- for use python-3.5

<pre>

$ cd /var/www/wsgi_apps/active-task-summary
$ sudo -u www-data python3.5 manage.py makemigrations
$ sudo -u www-data python3.5 manage.py migrate auth
$ sudo -u www-data python3.5 manage.py migrate
$ sudo -u www-data python3.5 manage.py createsuperuser

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
- for use python-2.7

<pre>

$ sudo yum install httpd mod_ssl
$ sudo yum install gcc make
$ sudo yum install --enablerepo=ius python27 python27-pip python27-mod_wsgi python27-devel
$ sudo -s
# export PATH="/usr/pgsql-9.6/bin:$PATH"
# pip2.7 install -r requirements.txt

</pre>


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

</pre>

- for use python-2.7

<pre>

$ sudo vi /etc/httpd/conf.d/python27-mod_wsgi.conf

<IfModule !python_module>
    <IfModule !wsgi_module>
        LoadModule wsgi_module modules/python27-mod_wsgi.so
        WSGISocketPrefix run/wsgi
        WSGIScriptReloading On
    </IfModule>
</IfModule>

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

- for use python-2.7

<pre>

$ sudo ln -sf /usr/lib/python2.7/site-packages/django/contrib/admin/static/admin admin

</pre>

- for use python-3.5

<pre>

$ sudo ln -sf /usr/lib/python3.5/site-packages/django/contrib/admin/static/admin admin

</pre>


### create database schema for web application


- for use python-2.7

<pre>

$ cd /var/www/wsgi_apps/active-task-summary
$ sudo -u apache python2.7 manage.py makemigrations
$ sudo -u apache python2.7 manage.py migrate auth
$ sudo -u apache python2.7 manage.py migrate
$ sudo -u apache python2.7 manage.py createsuperuser

</pre>

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

---

## install for CentOS-7

### install external repo

<pre>

$ sudo yum check-update
$ sudo yum install epel-release
$ sudo rpm -ivh https://dl.iuscommunity.org/pub/ius/stable/CentOS/7/x86_64/ius-release-1.0-15.ius.centos7.noarch.rpm
$ sudo rpm -ivh http://download.postgresql.org/pub/repos/yum/9.6/redhat/rhel-7-x86_64/pgdg-centos96-9.6-3.noarch.rpm
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
$ sudo /usr/pgsql-9.6/bin/postgresql96-setup initdb
$ sudo vi /var/lib/pgsql/9.6/data/pg_hba.conf
host    all             all             127.0.0.1/32            md5
$ sudo systemctl restart postgresql-9.6
$ sudo -u postgres /usr/pgsql-9.6/bin/createuser --createdb --pwprompt --superuser webapp
Password:
$ sudo -u postgres /usr/pgsql-9.6/bin/createdb --encoding=UTF8 --owner=webapp ats
$ psql -h 127.0.0.1 -U webapp -W ats
Password:
ats=# \q

</pre>


### install modules and librairies

- for use python-2.7

<pre>

$ sudo yum install httpd mod_ssl python mod_wsgi python-devel gcc make
$ sudo yum install --enablerepo=epel python-pip
$ sudo -s
# export PATH="/usr/pgsql-9.6/bin:$PATH"
# pip2.7 install -r requirements.txt

</pre>

- for use python-3.5

<pre>

$ sudo yum install httpd mod_ssl gcc make
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
$ sudo cp wsgi_apache2_ats.conf.cent7.sample /etc/httpd/conf.d/wsgi_ats.conf

</pre>

- for use python-2.7

<pre>

$ sudo vi /etc/httpd/conf.modules.d/10-wsgi.conf

LoadModule wsgi_module modules/mod_wsgi.so
WSGISocketPrefix run/wsgi
WSGIScriptReloading On

</pre>

- for use python-3.5

<pre>

$ sudo vi /etc/httpd/conf.modules.d/10-wsgi-python3.5.conf

<IfModule !wsgi_module>
    LoadModule wsgi_module modules/mod_wsgi_python3.5.so
    WSGISocketPrefix run/wsgi
    WSGIScriptReloading On
</IfModule>

</pre>

<pre>

$ sudo systemctl restart httpd

</pre>

### link static file in webapplication.

<pre>

$ sudo mkdir /var/www/html/static
$ cd /var/www/html/static
$ sudo ln -sf /var/www/wsgi_apps/active-task-summary/ats/static ats

</pre>

- for use python-2.7

<pre>

$ sudo ln -sf /usr/lib/python2.7/site-packages/django/contrib/admin/static/admin admin

</pre>

- for use python-3.5

<pre>

$ sudo ln -sf /usr/lib/python3.5/site-packages/django/contrib/admin/static/admin admin

</pre>


### create database schema for web application


- for use python-2.7

<pre>

$ cd /var/www/wsgi_apps/active-task-summary
$ sudo -u apache python2.7 manage.py makemigrations
$ sudo -u apache python2.7 manage.py migrate auth
$ sudo -u apache python2.7 manage.py migrate
$ sudo -u apache python2.7 manage.py createsuperuser

</pre>

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
16247 ?        Sl     0:00 (wsgi:ats)      -DFOREGROUND

</pre>


### try login

- curl -v http://localhost/toolproj/ats/login/
