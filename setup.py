# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='sample',
    version='0.1.0',
    description='tinyMBSE, model with command line',
    long_description=readme,
    author='Andrés Juez',
    author_email='jdsallinger@gmail.com',
    url='https://github.com/andresjuez/tinyMBSE',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

