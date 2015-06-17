import os
from setuptools import setup
from siteflags import VERSION


PATH_BASE = os.path.dirname(__file__)

f = open(os.path.join(PATH_BASE, 'README.rst'))
README = f.read()
f.close()

setup(
    name='django-siteflags',
    version='.'.join(map(str, VERSION)),
    url='https://github.com/idlesign/django-siteflags',

    description='Reusable application for Django allowing users to flag/bookmark site objects',
    long_description=README,
    license='BSD 3-Clause License',

    author='Igor `idle sign` Starikov',
    author_email='idlesign@yandex.ru',

    packages=['siteflags'],
    include_package_data=True,
    zip_safe=False,

    install_requires=['django-etc'],

    classifiers=[
        # As in https://pypi.python.org/pypi?:action=list_classifiers
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'License :: OSI Approved :: BSD License'
    ],
)

