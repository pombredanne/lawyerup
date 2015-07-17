#!/usr/bin/env python
# Copyright (c) 2013, RedJack, LLC.
# All rights reserved.
#
# Please see the COPYING file in this distribution for license details.

import ast
import re

from setuptools import setup


_version_re = re.compile(r'__version__\s+=\s+(.*)')


# From <https://github.com/mitsuhiko/click/blob/master/setup.py>
with open('lawyerup/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')


install_requires = [
]


extras_require = {
    ':python_version=="2.6"': ['argparse'],
}


setup(
    name='lawyerup',
    version=version,
    description='LawyerUp adds license headers to your code',
    long_description=readme + '\n\n' + '\n\n' + history,
    author='Andy Freeland',
    author_email='andy.freeland@redjack.com',
    url='https://github.com/redjack/lawyerup',
    packages=[
        'lawyerup',
    ],
    package_dir={'lawyerup': 'lawyerup'},
    entry_points={
        'console_scripts': ['lawyerup=lawyerup.core:main'],
    },
    include_package_data=True,
    install_requires=install_requires,
    extras_require=extras_require,
    zip_safe=False,
    keywords='lawyerup',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
