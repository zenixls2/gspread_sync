# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='gspread_sync',
    version='0.0.1',
    description='google spreadsheet wrapper with multithread safety',
    long_description=long_description,
    url='https://github.com/zenixls2/gspread_sync',
    author='Zenix Huang',
    author_email='zenixls2@gmail.com',
    license='Apache License 2.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Monitoring',
    ],
    platforms='any',
    keywords='spreadsheet google',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['google-api-python-client', 'httplib2', 'google-auth',
                      'google-auth-oauthlib', 'google-auth-httplib2'],
)
