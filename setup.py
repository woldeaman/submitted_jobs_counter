#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup as stsetup


if __name__ == "__main__":
    # poission boltzmann solver
    stsetup(name='check_optimizations',
            packages=['watch_jobs'],
            version="0.1",
            license='MIT',
            description=('Checking current process of optimization jobs.'),
            author="Amanuel Wolde-Kidan",
            author_email="amanuel.wolde-kidan@fu-berlin.de",
            include_package_data=True,
            zip_safe=False,
            requires=['pandas (>=0.22)'],
            install_requires=['pandas (>=0.22)'],
            entry_points={'console_scripts': ['check_optimizations=watch_jobs.watch_jobs:main', ], }, )
