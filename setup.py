from __future__ import unicode_literals

import re

from setuptools import find_packages, setup


def get_version(filename):
    content = open(filename).read()
    metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", content))
    return metadata['version']


setup(
    name='Mopidy-Headless',
    version=get_version('mopidy_headless/__init__.py'),
    url='https://github.com/qurben/mopidy-headless',
    license='Apache License, Version 2.0',
    author='Gerben Oolbekkink',
    author_email='g.j.w.oolbekkink@gmail.com',
    description='Mopidy extension for controlling via input devices',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'setuptools',
        'Mopidy >= 3.0',
        'Pykka >= 1.1',
        'evdev >= 0.7',
    ],
    entry_points={
        'mopidy.ext': [
            'headless = mopidy_headless:Extension',
        ],
    },
)
