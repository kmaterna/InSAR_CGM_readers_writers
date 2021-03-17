"""
Utility function to read SCEC CGM Working Group results (i.e., from a google drive) and package them into HDF5 file.
Will be called when the product is ready to be packaged and distributed.
Placeholder right now.
"""

import h5py


def read_cgm_working_group_data(input_filenames):
    """
    Input function for data of CGM working group. Placeholder.

    :param input_filenames: a list of some kind, not defined yet.
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


if __name__ == "__main__":
    scec_filenames = [];
    cgm_data_structure = read_cgm_working_group_data(scec_filenames);
    write_cgm_hdf5(cgm_data_structure, "SCEC_CGM_INSAR_v0.hdf5");
