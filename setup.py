import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
  README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-wad',
    version='0.0.01',
    packages=find_packages(),
    include_package_data=True,
    license='GNU GPL3 License',  # example license
    description='A collection of Django apps to syncronize with AdWords API.',
    long_description=README,
    url='https://www.github.com/btardio/wad',
    author='Brandon Tardio',
    author_email='btardio@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.9',  # replace "X.Y" as appropriate
        'Intended Audience :: Developers',
        'Topic :: Database',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7.11',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)

