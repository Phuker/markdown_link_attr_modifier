#!/usr/bin/env python
# encoding: utf-8

from setuptools import setup

setup(
    name = "markdown_link_attr_modifier",
    version = "0.1.0",
    description = "Python markdown extension to modify attributes of all links",
    author = "Phuker",
    author_email = 'Phuker@users.noreply.github.com',
    url = "https://github.com/Phuker/",
    license = "GNU General Public License v3.0",
    packages = [],
    py_modules = ['markdown_link_attr_modifier'],
    scripts = [],
    install_requires = [
        'markdown',
    ],
    python_requires = '>=2.7'
)
