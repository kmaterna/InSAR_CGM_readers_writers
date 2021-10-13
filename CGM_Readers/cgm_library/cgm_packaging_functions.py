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
    tracks_datastructure = [];   # a list of dictionaries
    for one_track in all_tracks:  # loop through tracks in the fileio_config_file, reading metadata and data
        print("Reading data from track %s..." % one_track);
        onetrack_config = io_cgm_configs.read_track_metadata_config(toplevel_config[one_track]["metadata_file"]);
        onetrack_data = read_one_track_data(toplevel_config[one_track]);
        onetrack_dict = {**onetrack_config._sections["track-config"], **onetrack_data};  # merging two dictionaries
        tracks_datastructure.append(onetrack_dict);
    io_cgm_hdf5.write_cgm_hdf5(tracks_datastructure, toplevel_config, toplevel_config["general-config"]["hdf5_file"],
                               write_velocities=True, write_time_series=True);
    io_cgm_hdf5.write_cgm_hdf5(tracks_datastructure, toplevel_config,
                               toplevel_config["general-config"]["hdf5_vel_file"], write_velocities=True,
                               write_time_series=False);
    return;


def read_one_track_data(fileio_config_dict):
    """Read grd data for velocities, time series, and look vectors associated with one track.
    fileio_config_dict should just print out the filenames"""
    print("Reading grid data from track.")
    track_dict = {};

    # Getting look vectors
    [lon, lat, unit_east_ll_grd] = read_netcdf4(fileio_config_dict["unit_east_ll_grd"])
    track_dict["lon"] = lon;
    track_dict["lat"] = lat;
    track_dict["lkv_E"] = unit_east_ll_grd;
    track_dict["lkv_N"] = read_netcdf4(fileio_config_dict["unit_north_ll_grd"])[2];
    track_dict["lkv_U"] = read_netcdf4(fileio_config_dict["unit_up_ll_grd"])[2];
    track_dict["dem"] = read_netcdf4(fileio_config_dict["dem_ll_grd"])[2];

    # Getting velocities
    [_, _, velocity_grid] = read_netcdf4(fileio_config_dict["velocity_ll_grd"]);
    track_dict["velocities"] = velocity_grid;

    # Getting time series. Glob pattern should match only the time series grids, not others.
    ts_grd_files = glob.glob(fileio_config_dict["ts_directory"] + '/*[0-9]_ll.grd');
    if fileio_config_dict["safes_list"]:
        full_safe_list = np.loadtxt(fileio_config_dict["safes_list"], unpack=True,
                                    dtype={'names': ('u10',), 'formats': ('U50',)});
        safe_times = [x[0][17:32] for x in full_safe_list];
    else:
        safe_times = [];
        # providing the full list of safes is strongly encouraged
    print("Found %s time series files" % len(ts_grd_files));
    ts_grd_files = sorted(ts_grd_files);
    for onefile in ts_grd_files:
        datestr_fine = [];
        datestr_coarse = re.findall(r"\d\d\d\d\d\d\d\d", onefile)[0];
        for safe_time in safe_times:
            if datestr_coarse in safe_time:
                datestr_fine = safe_time
        datestr_saving = datestr_fine if datestr_fine else datestr_coarse;
        track_dict[datestr_saving] = read_netcdf4(onefile)[2];  # saving the ts array

    # PACKAGING DATA STRUCTURE
    verify_same_shapes(track_dict);  # defensive programming
    return track_dict;


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
    if len(rootgrp.variables.keys()) == 6:
        # Use a gdal parsing: ['x_range', 'y_range', 'z_range', 'spacing', 'dimension', 'z']
        xinc = float(rootgrp.variables['spacing'][0])
        yinc = float(rootgrp.variables['spacing'][1])
        xstart = float(rootgrp.variables['x_range'][0]) + xinc/2  # pixel-node-registered
        xfinish = float(rootgrp.variables['x_range'][1])
        xvar = np.arange(xstart, xfinish, xinc);
        ystart = float(rootgrp.variables['y_range'][0]) + xinc/2  # pixel-node-registered
        yfinish = float(rootgrp.variables['y_range'][1])
        yvar = np.arange(ystart, yfinish, yinc);
        zvar = rootgrp.variables['z'][:].copy();
        zvar = np.flipud(np.reshape(zvar, (len(yvar), len(xvar))));  # frustrating.
    else:
        [xkey, ykey, zkey] = rootgrp.variables.keys();  # assuming they come in a logical order like (lon, lat, z)
        xvar = rootgrp.variables[xkey][:];
        yvar = rootgrp.variables[ykey][:];
        zvar = rootgrp.variables[zkey][:, :];
    return [xvar, yvar, zvar];


def verify_same_shapes(track_dict):
    """Defensive programming for one track of CGM data before packaging"""
    lon = track_dict["lon"];
    lat = track_dict["lat"];
    expected_shape = (len(lat), len(lon));
    assert (np.shape(track_dict["lkv_E"]) == expected_shape), ValueError("look_vector_east wrong size");
    assert (np.shape(track_dict["lkv_N"]) == expected_shape), ValueError("look_vector_north wrong size");
    assert (np.shape(track_dict["lkv_U"]) == expected_shape), ValueError("look_vector_up wrong size");
    assert (np.shape(track_dict["dem"]) == expected_shape), ValueError("dem wrong size");
    assert (np.shape(track_dict["velocities"]) == expected_shape), ValueError("velocity grid wrong size");
    for keyname in track_dict.keys():
        if re.match(r"[0-9]{8}T[0-9]{6}", keyname):  # if we have time series slice, such as '20150121T134347'
            assert (np.shape(track_dict[keyname]) == expected_shape), ValueError("ts grid wrong size");
    return;
