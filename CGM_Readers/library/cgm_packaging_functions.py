"""
Coordinating the packaging of HDF5 files for SCEC CGM InSAR
"""

from . import io_cgm_hdf5
from . import io_cgm_configs
from netCDF4 import Dataset
import numpy as np
import glob
import re


def drive_scec_hdf5_packaging(fileio_config_file):
    """A coordinator function to package up an HDF5 file with SCEC InSAR CGM results from local files."""
    toplevel_config = io_cgm_configs.read_file_level_config(fileio_config_file);
    all_tracks = toplevel_config.sections()[1:];  # get 1 or more tracks in the top-level config
    tracks_datastructure = [];
    for one_track in all_tracks:  # loop through tracks in the fileio_config_file, reading metadata and data
        print("Reading data from track %s..." % one_track);
        onetrack_config = io_cgm_configs.read_track_metadata_config(toplevel_config[one_track]["metadata_file"]);
        onetrack_data = read_one_track_data(toplevel_config[one_track]);
        tracks_datastructure.append([onetrack_config, onetrack_data]);
    io_cgm_hdf5.write_cgm_hdf5(tracks_datastructure, toplevel_config, toplevel_config["general-config"]["hdf5_file"]);
    return;


def read_one_track_data(fileio_config_dict):
    """Read grd data for velocities, time series, and look vectors associated with one track.
    fileio_config_dict should just print out the filenames"""
    print("Reading grid data from track.")

    # Getting look vectors
    [lon, lat, unit_east_ll_grd] = read_netcdf4(fileio_config_dict["unit_east_ll_grd"]);
    [_, _, unit_north_ll_grd] = read_netcdf4(fileio_config_dict["unit_north_ll_grd"]);
    [_, _, unit_up_ll_grd] = read_netcdf4(fileio_config_dict["unit_up_ll_grd"]);
    lkv_datastructure = [lon, lat, unit_east_ll_grd, unit_north_ll_grd, unit_up_ll_grd];

    # Getting velocities
    [_, _, velocity_grid] = read_netcdf4(fileio_config_dict["velocity_ll_grd"]);
    velocity_datastructure = [velocity_grid];

    # Getting time series
    ts_grd_files = glob.glob(fileio_config_dict["ts_directory"] + '/*.grd');
    ts_datestr_list = [];
    ts_array_list = [];
    for onefile in ts_grd_files:
        datestr = re.findall(r"\d\d\d\d\d\d\d\d", onefile)[0];
        ts_datestr_list.append(str(datestr));
        [_, _, ts_array] = read_netcdf4(onefile);
        ts_array_list.append(ts_array);
    ts_datastructure = [ts_datestr_list, ts_array_list];

    # PACKAGING DATA STRUCTURE
    onetrack_datastructure = [lkv_datastructure, velocity_datastructure, ts_datastructure];
    verify_same_shapes(onetrack_datastructure);  # defensive programming
    return onetrack_datastructure;


def read_netcdf4(filename):
    """
    A netcdf4 reading function for pixel-node registered files with recognized key patterns.

    :param filename: name of netcdf4 file
    :type filename: string
    :returns: [xdata, ydata, zdata]
    :rtype: list of 3 np.ndarrays
    """
    print("Reading file %s " % filename);
    rootgrp = Dataset(filename, "r");
    [xkey, ykey, zkey] = rootgrp.variables.keys();  # assuming they come in a logical order like (lon, lat, z)
    xvar = rootgrp.variables[xkey];
    yvar = rootgrp.variables[ykey];
    zvar = rootgrp.variables[zkey];
    return [xvar[:], yvar[:], zvar[:, :]];


def verify_same_shapes(onetrack_datastructure):
    """Defensive programming for one track of CGM data before packaging"""
    [lkv_datastructure, velocity_datastructure, ts_datastructure] = onetrack_datastructure;
    lon = lkv_datastructure[0];
    lat = lkv_datastructure[1];
    expected_shape = (len(lat), len(lon));
    assert (np.shape(lkv_datastructure[2]) == expected_shape), ValueError("look_vector_east wrong size");
    assert (np.shape(lkv_datastructure[3]) == expected_shape), ValueError("look_vector_north wrong size");
    assert (np.shape(lkv_datastructure[4]) == expected_shape), ValueError("look_vector_up wrong size");
    assert (np.shape(velocity_datastructure[0]) == expected_shape), ValueError("velocity grid wrong size");
    for ts_array in ts_datastructure[1]:
        assert (np.shape(ts_array) == expected_shape), ValueError("ts grid wrong size");
    return;
