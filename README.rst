==========
Django Wad
==========

Wad is a collection of Django apps that syncronize database tables with the AdWords API.

The AdWords API is currently read from storage and more information about populating the googleads.yaml file can be found on the Google AdWords API website.

Detailed HTML documentation about using Django Wad can be found in the “docs” directory. 

Sphinx is a program that generates HTML documentation from reStructuredText. Sphinx related files are in the “docs/sphinx” directory.

Install
-------

1. git clone http://github.com/btardio/wad/dist/django-wad-0.0.1.tar.gz

2. pip install django-wad-0.0.1.tar.gz

This install files in your site-packages directory, a new directory is created for each wad module. ie: wad_Campaign, wad_Budget

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



