#!/usr/bin/env python

from setuptools import setup, find_packages
import stayontop
import os


def read(*names):
    values = dict()
    extensions = ['.txt', '.rst']
    for name in names:
        value = ''
        for extension in extensions:
            filename = name + extension
            if os.path.isfile(filename):
                value = open(name + extension).read()
                break
        values[name] = value
    return values

long_description = """
%(README)s

News
====

%(TODO)s

""" % read('README', 'TODO')

setup(
    name='stayontop',
    version=stayontop.__version__,
    description='Keep AWS instances stopped on out of office hours',
    long_description=long_description,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: System :: Systems Administration",
    ],
    keywords='stayontop keep stopped aws instances cost effective',
    author='Yagmur Guraslan',
    author_email='guraslan@gmail.com',
    maintainer='Yagmur Guraslan',
    maintainer_email='guraslan@gmail.com',
    url='https://github.com/guraslan/stayontop',
    download_url = 'https://github.com/guraslan/stayontop/tarball/0.1a0',
    license='BSD',
    packages=['stayontop'],
    entry_points={
        'console_scripts': [
            'stayontop = stayontop.stayontop:command_line_main',
        ]
    },
    install_requires=[
        'boto',
        'botocore',
        'colorama',
        'PyYAML',
        'argparse'
    ]
)
