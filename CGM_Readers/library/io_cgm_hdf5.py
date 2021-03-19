"""
Utility function to read/write SCEC CGM InSAR Working Group results packaged into HDF5 file.
Will be called when the product is ready to be packaged and distributed.
"""

import h5py

def read_cgm_hdf5(input_filename):
    """
    Input function for HDF5 file of CGM working group.

    :param input_filename: an HDF5 file
    :return: several data structures of some kind, not defined yet.
    """
    cgm_data_structure = [];  # placeholder
    return cgm_data_structure;


def write_cgm_hdf5(cgm_data_structure, output_filename):
    """
    Output function to create HDF5 file from CGM working group's data.

    :param cgm_data_structure: a structure of some kind, not defined yet.
    :param output_filename: the name of the HDF5 file that will be written.
    :type output_filename: string
    """
    return;
