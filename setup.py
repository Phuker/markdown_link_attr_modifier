#!/usr/bin/env python3
# encoding: utf-8

from setuptools import setup

# Impossible? to update only Readme.md but keep version number in PyPI.
# Gancui use a dummy readme file instead.
with open('Readme.PyPI.md', 'r') as f:
    long_description = f.read()

setup(
    name = 'markdown_link_attr_modifier',
    description = 'A Python-Markdown extension to modify attributes of <a> tag links',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author = 'Phuker',
    author_email = 'Phuker@users.noreply.github.com',
    url = 'https://github.com/Phuker/markdown_link_attr_modifier',
    license = 'GNU General Public License v3.0',
    packages = [],
    py_modules = ['markdown_link_attr_modifier'],
    scripts = [],
    install_requires = [
        'markdown>=3',
    ],
    classifiers = [
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Text Processing :: Markup :: Markdown',
    ],
    python_requires = '>=3.6', # PEP 498, f-strings
)
