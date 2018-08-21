"""
A simple url-shortener service.
"""

from os import path

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

setup(
    name='url-shortener',
    version='1.0.0',
    description='Simple url shortener service',
    url='https://github.com/mvallebr/url-shortener',
    license="Apache License 2.0",
    author='Marcelo Valle',
    author_email='mvallebr@gmail.com',
    packages=find_packages(exclude=['docs', 'tests']),  # Required

    include_package_data=True,
    zip_safe=False,
    install_requires=['Flask', 'cassandra-driver'],
    extras_require={
        'test': [
            'pytest',
            'coverage',
        ],
    },
)
