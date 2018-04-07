# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 KuraLabs S.R.L
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
Usage:

::

    ./setup.py sdist
    ./setup.py bdist_wheel
"""

from setuptools import setup


def check_directory():
    """
    You must always change directory to the parent of this file before
    executing the setup.py script. setuptools will fail reading files,
    including and excluding files from the MANIFEST.in, defining the library
    path, etc, if not.
    """
    from os import getcwd
    from os.path import dirname, abspath
    return getcwd() == abspath(dirname(__file__))


assert check_directory(), 'Call setup.py from its parent directory'


#####################
# Utilities         #
#####################

def read(filename):
    """
    Read the content of a file.

    :param str filename: The file to read.

    :return: The content of the file.
    :rtype: str
    """
    with open(filename, mode='rt', encoding='utf-8') as fd:
        return fd.read()


#####################
# Finders           #
#####################

def find_version(filename):
    """
    Find version of a package.

    This will read and parse a Python module that has defined a __version__
    variable. This function does not import the file.

    ::

        setup(
            ...
            version=find_version('lib/package/__init__.py'),
            ...
        )

    :param str filename: Path to a Python module with a __version__ variable.

    :return: The version of the package.
    :rtype: str
    """
    import re

    content = read(filename)
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", content, re.M
    )
    if not version_match:
        raise RuntimeError('Unable to find version string.')

    version = version_match.group(1)

    print('Version found:')
    print('  {}'.format(version))
    print('--')

    return version


setup(
    name='multiexit',
    py_modules=['multiexit'],
    version=find_version('multiexit.py'),

    # Metadata
    author='KuraLabs S.R.L',
    author_email='info@kuralabs.io',
    description='atexit replacement that supports multiprocessing',
    long_description=read('README.rst'),
    url='https://github.com/kuralabs/multiexit',
    keywords='multiexit multiprocessing atexit',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
    ],
)
