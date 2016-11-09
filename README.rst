==========
Django Wad
==========

Wad is a collection of Django apps that syncronize database tables with the AdWords API.

The AdWords API is currently read from storage and more information about populating the googleads.yaml file can be found on the Google AdWords API website.

Detailed HTML documentation about using Django Wad can be found in the “docs” directory. 

Sphinx is a program that generates HTML documentation from reStructuredText. Sphinx related files are in the “docs/sphinx” directory.

Install
-------

1. git clone http://github.com/btardio/wad

2. pip install wad/dist/django-wad-0.0.1.tar.gz

OR

1. wget https://github.com/btardio/wad/raw/master/dist/django-wad-0.0.1.tar.gz

2. pip install django-wad-0.0.1.tar.gz


This installs files in your site-packages directory, a new directory is created for each wad module. ie: wad_Campaign, wad_Budget

Install Requirements
--------------------

Google AdWords API Lib

1. pip install googleads

Configure a googleads.yaml file and place it in your home directory.

Configuring googleads goes beyond the scope of this documentation. At the very minimum a googleads.yaml file will need to be placed in your home directory.

Quick Start
-----------

1. Add Django Wad applications to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ....
        'wad_Budget',
        'wad_Campaign',
    ]

2. Run `python manage.py makemigrations` to create Django Wad migrations.

3. Run `python manage.py migrate` to apply Django Wad migrations.

4. Run `python manage.py test` to test Django Wad functionality.

5. Consult the HTML docs to determine which synchronize commands to run, such as `python manage.py budgetsync`.

6. Start the development server and visit http://127.0.0.1:8000/admin/ to view the items synchronized. ( Remember that Google API Developer accounts are limited to 10,000 queries a day )



Running Tests
-------------

python manage.py test wad_Budget

python manage.py test wad_Campaign

