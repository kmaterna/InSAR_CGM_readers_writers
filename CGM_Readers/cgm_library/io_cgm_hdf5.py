"""
Utility function to read/write SCEC CGM InSAR Working Group results packaged into HDF5 file.
Will be called when the product is ready to be packaged and distributed.
cgm_data_structure: a dictionary for each track:
{
    lots_of_product_metadata : generally strings
    lots_of_track_metadata : generally strings
    lon : 1D array
    lat : 1D array
    lkv_E : 2D array
    lkv_N : 2D array
    lkv_U : 2D array
    dem : 2D array
    velocities : 2D array
    yyyymmddThhmmss (n time series slices)... : 2D arrays
}
"""

import h5py, re
from datetime import date
import numpy as np


def read_cgm_hdf5_demo_python(input_filename):
    """
    Input function for HDF5 file of CGM working group. An example of how to read this file in Python.
    This function would be given to advanced users for parsing the entire CGM HDF5 file.

    :param input_filename: an HDF5 file
    :return: Nothing, just prints metadata
    """
    print("\n\nReading hdf5 file %s in Python " % input_filename);
    hf = h5py.File(input_filename, 'r');

    # Print all available top levels:
    all_keys = [x for x in hf.keys()];  # returns a list of the top level directories
    print("HDF5 file has the following top level directories: ", all_keys);

    # Read metadata (we don't store it here)
    general_metadata = hf.get('Product_Metadata');
    print('---------- Product Metadata ----------');
    for item in general_metadata.attrs.keys():
        print(item + ":", general_metadata.attrs[item]);
    print('---------- End product metadata ---------- \n');

    # Read each track in the hdf file
    all_keys.remove('Product_Metadata');  # return the keys that correspond to tracks of InSAR data
    for track in all_keys:
        track_data = hf.get(track);
        track_name = track_data.attrs["track_name"];

        # Reading metadata
        print('---------- Track %s metadata ----------' % track_name);
        for item in track_data.attrs.keys():
            print(item + ":", track_data.attrs[item]);
        print('---------- End Track %s metadata ----------' % track_name);

        # Reading Grid Info
        print('---------- Track %s Grid Data ----------' % track_name);
        Grid_Info = track_data.get('Grid_Info');
        for item in Grid_Info.keys():
            print(item + ":", np.shape(np.array(Grid_Info.get(item))));

        # Reading Velocity Information
        print('---------- Track %s Velocity Data ----------' % track_name);
        Velocities = track_data.get('Velocities');
        for item in Velocities.keys():
            print(item + ":", np.shape(np.array(Velocities.get(item))));

        # Reading time series information
        print('---------- Track %s Time Series Data ----------' % track_name);
        TS = track_data.get('Time_Series');
        print(TS)
        for item in TS.keys():
            print(item + ":", np.shape(np.array(TS.get(item))));

    hf.close();
    return None;


def read_cgm_hdf5_full_data(input_filename):
    """
    Input function for HDF5 file of CGM working group with velocities and time series.
    Only operates on full HDF5 files, not velocity-only

    :param input_filename: an HDF5 file
    :return: internal data structure for the data in an hdf5 file.
        - one list element for each track (a dictionary for each track)
        - in each grid, the lon arrays increase from left to right, and lat arrays increase upward,
          while columns increase downward. This means that the data grids will be stored with latitude increasing down,
          and should be plotted with plt.gca().invert_yaxis().
        - dict for each track contains track-specific metadata and top-level file metadata for redundancy.
    """
    print("Reading file %s " % input_filename);
    cgm_data_structure = [];
    hf = h5py.File(input_filename, 'r');
    # Read each track in the hdf file
    product_metadata = hf.get("Product_Metadata");
    all_keys = [x for x in hf.keys()];  # returns a list of top level directories
    all_keys.remove('Product_Metadata');  # just loop through the keys that correspond to tracks of InSAR data
    for track in all_keys:
        track_data = hf.get(track);  # read from hdf5 file

        # Get metadata for track and for file, combined into one dictionary
        track_dict = {};  # the big dictionary for this track
        print("Reading track %s: " % track_data.attrs["track_name"]);
        for item in track_data.attrs.keys():
            track_dict[item] = track_data.attrs[item];
        for item in product_metadata.attrs.keys():   # duplicate file metadata into track_metadata_dict for convenience
            track_dict[item] = product_metadata.attrs[item];

        # Get look vectors, DEM, and grid arrays
        Grid_Info = track_data.get('Grid_Info');
        track_dict["lon"] = np.array(Grid_Info.get("lon"));
        track_dict["lat"] = np.array(Grid_Info.get("lat"));
        track_dict["lkv_E"] = np.flipud(np.array(Grid_Info.get("lkv_E")));
        track_dict["lkv_N"] = np.flipud(np.array(Grid_Info.get("lkv_N")));
        track_dict["lkv_U"] = np.flipud(np.array(Grid_Info.get("lkv_U")));
        track_dict["dem"] = np.flipud(np.array(Grid_Info.get("dem")));

        # Get velocities: [2D_array_of_velocities]
        Velocities = track_data.get('Velocities');
        track_dict["velocities"] = np.flipud(np.array(Velocities.get("velocities")));

        # Get time series: [2D_array_of_positions] for each time
        TS = track_data.get('Time_Series');
        for item in TS.keys():
            track_dict[item] = np.flipud(np.array(TS.get(item)));

        cgm_data_structure.append(track_dict);  # a list of dictionaries
        # print(track_dict.keys());
    return cgm_data_structure;


def write_cgm_hdf5(cgm_data_structure, configobj, output_filename, write_velocities=True, write_time_series=True):
    """
    Output function to create HDF5 file from CGM working group's data.
    Useful for individuals who want to package their own data from a Python cgm_data_structure dictionary

    :param cgm_data_structure: a list of dictionaries
    :param configobj: configobj read from file-level config file (can be replaced within the dictionary later)
    :param output_filename: the name of the HDF5 file that will be written.
    :param write_velocities: bool, whether to write velocities into the hdf5 file
    :param write_time_series: bool, whether to write time series into the hdf5 file
    :type output_filename: string
    """
    print("Writing file %s " % output_filename);
    hf = h5py.File(output_filename, 'w');
    prod_metadata = hf.create_group('Product_Metadata');  # create a metadata group
    prod_metadata.attrs['version'] = str(configobj["general-config"]["scec_cgm_version"]);
    prod_metadata.attrs['production_date'] = str(date.today());
    prod_metadata.attrs['website_link'] = str(configobj["general-config"]["website_link"]);
    prod_metadata.attrs['documentation_link'] = str(configobj["general-config"]["documentation_link"]);
    prod_metadata.attrs['citation_info'] = str(configobj["general-config"]["citation_info"]);
    prod_metadata.attrs['contributing_institutions'] = str(configobj["general-config"]["contributing_institutions"]);
    prod_metadata.attrs['contributing_researchers'] = str(configobj["general-config"]["contributing_researchers"]);
    prod_metadata.attrs['filename'] = str(configobj["general-config"]["hdf5_file"]);
    prod_metadata.attrs['doi'] = str(configobj["general-config"]["doi"]);
    prod_metadata.attrs['node_offset'] = 1;    # for pixel-node registration (in theory, not practice)

    for track_dict in cgm_data_structure:
        print("Packaging track %s " % track_dict["track_name"]);
        track_data = hf.create_group('Track_'+track_dict["track_name"]);
        track_data.attrs["track_name"] = track_dict["track_name"];
        track_data.attrs["platform"] = track_dict["platform"];
        track_data.attrs["orbit_direction"] = track_dict["orbit_direction"];
        track_data.attrs["polygon_boundaries"] = track_dict["polygon_boundaries"];
        track_data.attrs["geocoded_increment"] = track_dict["geocoded_increment"];
        track_data.attrs["geocoded_range"] = track_dict["geocoded_range"];
        track_data.attrs["approx_posting"] = track_dict["approx_posting"];
        track_data.attrs["grdsample_flags"] = track_dict["grdsample_flags"];
        track_data.attrs["los_sign_convention"] = track_dict["los_sign_convention"];
        track_data.attrs["lkv_sign_convention"] = track_dict["lkv_sign_convention"];
        track_data.attrs["coordinate_reference_system"] = track_dict["coordinate_reference_system"];
        track_data.attrs["time_series_units"] = track_dict["time_series_units"];
        track_data.attrs["velocity_units"] = track_dict["velocity_units"];
        track_data.attrs["dem_source"] = track_dict["dem_source"];
        track_data.attrs["dem_heights"] = track_dict["dem_heights"];
        track_data.attrs["start_time"] = track_dict["start_time"];
        track_data.attrs["end_time"] = track_dict["end_time"];
        track_data.attrs["n_times"] = track_dict["n_times"];
        track_data.attrs["reference_image"] = track_dict["reference_image"];
        track_data.attrs["reference_frame"] = track_dict["reference_frame"];

        # Package grid information
        lon_array = track_dict["lon"];
        lat_array = track_dict["lat"];
        grid_group = track_data.create_group('Grid_Info')
        lon_ds = grid_group.create_dataset('lon', data=lon_array);
        lon_ds.make_scale(name='longitude');
        lat_ds = grid_group.create_dataset('lat', data=track_dict["lat"]);
        lat_ds.make_scale(name='latitude');
        # Requiring the gmt_range for each track because of extracting the grid in GMT later.
        gmt_range = str(np.round(np.min(lon_array), 4))+'/'+str(np.round(np.max(lon_array), 4))+'/' + \
                    str(np.round(np.min(lat_array), 4))+'/'+str(np.round(np.max(lat_array), 4));
        grid_group.attrs["gmt_range"] = gmt_range;
        tmp_e = grid_group.create_dataset('lkv_E', data=np.flipud(track_dict["lkv_E"]));
        tmp_e.attrs["node_offset"] = 1;
        tmp_e.dims[1].attach_scale(lon_ds);
        tmp_e.dims[0].attach_scale(lat_ds);
        tmp_n = grid_group.create_dataset('lkv_N', data=np.flipud(track_dict["lkv_N"]));
        tmp_n.attrs["node_offset"] = 1;
        tmp_n.dims[1].attach_scale(lon_ds);
        tmp_n.dims[0].attach_scale(lat_ds);
        tmp_u = grid_group.create_dataset('lkv_U', data=np.flipud(track_dict["lkv_U"]));
        tmp_u.attrs["node_offset"] = 1;
        tmp_u.dims[1].attach_scale(lon_ds);
        tmp_u.dims[0].attach_scale(lat_ds);
        tmp_dem = grid_group.create_dataset('dem', data=np.flipud(track_dict["dem"]));
        tmp_dem.attrs["node_offset"] = 1;
        tmp_dem.dims[1].attach_scale(lon_ds);
        tmp_dem.dims[0].attach_scale(lat_ds);

        # Package velocity information
        if write_velocities:
            vel_group = track_data.create_group('Velocities')
            tmp = vel_group.create_dataset('velocities', data=np.flipud(track_dict["velocities"]));
            tmp.attrs["node_offset"] = 1;
            tmp.dims[1].attach_scale(lon_ds);
            tmp.dims[0].attach_scale(lat_ds);
            tmp.dims[0].label = 'latitude'
            tmp.dims[1].label = 'longitude'

        # Package time series information
        if write_time_series:
            ts_group = track_data.create_group('Time_Series');
            for keyname in track_dict.keys():
                if re.match(r"[0-9]{8}T[0-9]{6}", keyname):  # if we have time series slice, such as '20150121T134347'
                    print("  time series: ", keyname);
                    tmp = ts_group.create_dataset(keyname, data=np.flipud(track_dict[keyname]));
                    tmp.attrs["node_offset"] = 1;
                    tmp.dims[1].attach_scale(lon_ds);
                    tmp.dims[0].attach_scale(lat_ds);

    hf.close();
    return;
