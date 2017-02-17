# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 11:52:44 2017

"""

#!/usr/bin/env python

try:
	from setuptools import setup
except:
    from distutils.core import setup
#from distutils.core import setup

setup(name='BiobankRead',
      packages = ['BiobankRead2'],
      version='1.1',
      description='UKBiobank Python pre-processing',
      author='Deborah Schneider-luftman',
      author_email='ds711@imperial.ac.uk',
      url='',
      download_url = '',
      plong_description=open('README.rst').read(),
      install_requires=[
	"bs4", "numpy", "pandas", "urllib3"
	],
      package_data = {
        # include aux data files:
        'BiobankRead2': ['data/*.txt', 'data/*.tsv'],},
     )
