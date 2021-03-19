"""
Coordinating the packaging of HDF5 files for SCEC CGM InSAR
"""

from . import io_cgm_hdf5
from . import io_cgm_configs

def drive_scec_hdf5_packaging(fileio_config_file):
    """A coordinator function to package up an HDF5 file with SCEC InSAR CGM results from local files."""
    toplevel_config = io_cgm_configs.read_file_level_config(fileio_config_file);

    # READ THE DATA SOMEHOW HERE
    datastructure = 0;

    io_cgm_hdf5.write_cgm_hdf5(datastructure, toplevel_config["general-config"]["hdf5_file"]);
    return;
