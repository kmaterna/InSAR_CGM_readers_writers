#!/usr/bin/env python
"""
Read SCEC CGM Working Group results (i.e., from a google drive) and package them into HDF5 file.
Will be called when the product is ready to be packaged and distributed.
"""


import argparse
from CGM_Readers import library


def welcome_and_parse_runstring():
    print("\nWrite a SCEC InSAR HDF5 file from local files.  Requires a file_level_config.txt file for "
          "system-specific file i/o options and top-level metadata. ");
    parser = argparse.ArgumentParser(description='Write a SCEC InSAR HDF5 file from local files. ',
                                     epilog='\U0001f600 \U0001f600 \U0001f600 ');
    parser.add_argument('config', type=str, help='name of file_level_config file. Required.')
    args = parser.parse_args()
    return args;


if __name__ == "__main__":
    args = welcome_and_parse_runstring();
    library.cgm_packaging_functions.drive_scec_hdf5_packaging(args.config);
