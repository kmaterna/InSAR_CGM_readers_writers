#!/usr/bin/env python3
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Author: Kathryn Materna, Ekaterina Tymofyeyeva, Kang Wang
# Copyright 2021. ALL RIGHTS RESERVED.
# United States Government Sponsorship acknowledged.
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os
import re
from setuptools import find_packages, setup

# Parameter defs
CWD = os.getcwd()


def get_version():
    with open('version.txt', 'r') as f:
        m = re.match("""version=['"](.*)['"]""", f.read())

    assert m, "Malformed 'version.txt' file!"
    return m.group(1)


setup(
    name='CGM_Readers',
    version=get_version(),
    description='This is the SCEC CGM InSAR HDF5 package',
    package_dir={
        'CGM_Readers': 'CGM_Readers',
        '': 'CGM_Readers'
    },
    packages=['CGM_Readers'] + find_packages('CGM_Readers'),
    scripts=[
        'CGM_Readers/bin/cgm_generate_empty_configs.py',
        'CGM_Readers/bin/cgm_write_hdf5.py',
    ],
    zip_safe=False,
)
