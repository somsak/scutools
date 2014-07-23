# in case setuptools become default in RHEL
from setuptools import setup, find_packages
import os, glob, sys, re
from distutils.core import setup
import distutils.sysconfig

name = 'scutools'
version = '0.6'

setup(
    name = name,
    version = version,
    packages = find_packages(),
    scripts = glob.glob('scripts/*-*'),

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
#    install_requires = ['docutils >= 0.3'],

    data_files = [
        ('share/doc/' + name + '-' + version, ['scutools.conf', 'COPYING']),
        ('share/man/man1', ['man/pexec.1']),
    ],
#    package_data = {
#        # If any package contains *.txt or *.rst files, include them:
#        '': ['*.txt', '*.rst'],
#        # And include any *.msg files found in the 'hello' package, too:
#        'hello': ['*.msg'],
#    },
    # metadata for upload to PyPI
    entry_points = {
        'console_scripts': [
            'pexec = scutools.app:main',
            'pls = scutools.app:main',
            'pps = scutools.app:main',
            'pcp = scutools.app:main',
            'pmv = scutools.app:main',
            'prm = scutools.app:main',
            'pcat = scutools.app:main',
            'pfind = scutools.app:main',
            'pdist = scutools.app:main',
            'pfps = scutools.app:main',
            'pkillps = scutools.app:main',
            'pkillu = scutools.app:main',
            'ppred = scutools.app:main',
            'ptest = scutools.app:main',
            'phost = scutools.app:main',
        ]
    },
    author = "Somsak Sriprayoonsakul",
    author_email = "somsaks@gmail.com",
    description = "Scalable Unix Tool packages",
    license = "GPLv3",
    keywords = "cluster grid unix",
    url = "http://code.google.com/p/scutools",   # project home page, if any

    # could also include long_description, download_url, classifiers, etc.
)
