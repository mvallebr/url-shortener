"""
A simple url-shortener service.
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='url-shortener',
    version='1.0.0',
    description='Simple url shortener service',
    url='https://github.com/mvallebr/url-shortener',
    author='Marcelo Valle',
    author_email='mvallebr@gmail.com',
    packages=find_packages(exclude=['docs', 'tests']),  # Required

    # This field lists other packages that your project depends on to run.
    # Any package you put here will be installed by pip when your project is
    # installed, so they must be valid existing projects.
    #
    # For an analysis of "install_requires" vs pip's requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['peppercorn'],  # Optional


)
