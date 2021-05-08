#!/usr/bin/env python

"""
A simple script to generate 2 new config files with default information.
Call this from a new directory to get valid config file templates
"""

import argparse
import cgm_library


def welcome_and_parse_runstring():
    print("\nWrite empty file_level_config and track_metadata_config file for packaging files into "
          "SCEC InSAR HDF5 file.");
    parser = argparse.ArgumentParser(description='Write two empty config files into a specified directory',
                                     epilog='\U0001f600 \U0001f600 \U0001f600 ');
    parser.add_argument('directory', type=str, help='name of directory (can be . for current directory). Required.')
    args = parser.parse_args()
    return args;


if __name__ == "__main__":
    args = welcome_and_parse_runstring();
    cgm_library.io_cgm_configs.write_empty_file_level_config(args.directory);
    cgm_library.io_cgm_configs.write_empty_track_metadata_config(args.directory);
