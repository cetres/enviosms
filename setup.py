"""EnvioSMS
See:
https://github.com/cetres/enviosms
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='enviosms',
    version='0.1.0',
    description='SMS Sender',
    long_description=long_description,
    url='https://github.com/cetres/enviosms',
    author='cetres',
    author_email='cetres@gmail.com',
    license='GPLv2',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Topic :: Communications :: SMS',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Framework :: Flask',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    keywords='sms messages broker',

    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),

    install_requires=['flask', 'flask-restful', 'qpid-python'],

)
