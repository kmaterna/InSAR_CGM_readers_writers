"""
Utility function to read/write SCEC CGM InSAR Working Group results packaged into HDF5 file.
Will be called when the product is ready to be packaged and distributed.
"""

import h5py
from datetime import date
import numpy as np


def read_cgm_hdf5_demo_python(input_filename):
    """
    Input function for HDF5 file of CGM working group. An example of how to read this file in Python.
    This function would be given to advanced users for parsing the entire CGM HDF5 file.

    :param input_filename: an HDF5 file
    :return: several data structures of some kind, not defined yet.
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
        TS = track_data.get('Time Series');
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
        - one element for each track
        - in each track: [metadata_dict, data]
        - data = [[lkv_obj], [velocities], [time_series]]
        - in each grid, the lon arrays increase from left to right, and lat arrays increase upward,
          while columns increase downward. This means that the data grids will be stored with latitude increasing down,
          and should be plotted with plt.gca().invert_yaxis().
        - metadata_dict for each track contains the track-specific metadata and the top-level file metadata.
    """
    print("Reading file %s " % input_filename);
    cgm_data_structure = [];
    hf = h5py.File(input_filename, 'r');
    # Read each track in the hdf file
    product_metadata = hf.get("Product_Metadata");
    all_keys = [x for x in hf.keys()];  # returns a list of the top level directories
    all_keys.remove('Product_Metadata');  # return the keys that correspond to tracks of InSAR data
    for track in all_keys:
        track_data = hf.get(track);

        # Get metadata for track and for file, combined into one dictionary
        track_dict = {};
        print("Reading track %s " % track_data.attrs["track_name"]);
        for item in track_data.attrs.keys():
            track_dict[item] = track_data.attrs[item];
        for item in product_metadata.attrs.keys():   # duplicate file metadata into track_metadata_dict for convenience
            track_dict[item] = product_metadata.attrs[item];

        # Get look vectors, DEM, and grid arrays
        grid_object = [];
        Grid_Info = track_data.get('Grid_Info');
        grid_object.append(np.array(Grid_Info.get("lon")));
        grid_object.append(np.array(Grid_Info.get("lat")));
        grid_object.append(np.array(Grid_Info.get("lkv_E")));
        grid_object.append(np.array(Grid_Info.get("lkv_N")));
        grid_object.append(np.array(Grid_Info.get("lkv_U")));
        grid_object.append(np.array(Grid_Info.get("dem")));

        # Get velocities: [2D_array_of_velocities]
        velocity_object = [];
        Velocities = track_data.get('Velocities');
        velocity_object.append(np.array(Velocities.get("velocities")));

        # Get time series: [list_of_str, 3D_array_of_TS]
        time_series_object = [];
        TS = track_data.get('Time_Series');
        dates_array = np.array(TS.get('Time_Array'));
        dates_array = [x.decode() for x in np.array(dates_array)];
        time_series_object.append(dates_array);
        time_series_object.append(np.array(TS.get('Time_Series_Grids')));

        track_data_internal_struct = [grid_object, velocity_object, time_series_object];
        track_data_package = [track_dict, track_data_internal_struct];
        cgm_data_structure.append(track_data_package);
    return cgm_data_structure;


def write_cgm_hdf5(cgm_data_structure, configobj, output_filename, write_velocities=True, write_time_series=True):
    """
    Output function to create HDF5 file from CGM working group's data.

    :param cgm_data_structure: a structure of some kind, not defined yet.
    :param configobj: configobj read from file-level config file
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

    for track_datastructure in cgm_data_structure:
        item = track_datastructure[0];
        data = track_datastructure[1];   # unpacking the datastructure created previously
        track_data = hf.create_group('Track_'+item["track-config"]["track_name"]);
        track_data.attrs["track_name"] = item["track-config"]["track_name"];
        track_data.attrs["platform"] = item["track-config"]["platform"];
        track_data.attrs["orbit_direction"] = item["track-config"]["orbit_direction"];
        track_data.attrs["polygon_boundaries"] = item["track-config"]["polygon_boundaries"];
        track_data.attrs["geocoded_increment"] = item["track-config"]["geocoded_increment"];
        track_data.attrs["geocoded_range"] = item["track-config"]["geocoded_range"];
        track_data.attrs["approx_posting"] = item["track-config"]["approx_posting"];
        track_data.attrs["grdsample_flags"] = item["track-config"]["grdsample_flags"];
        track_data.attrs["los_sign_convention"] = item["track-config"]["los_sign_convention"];
        track_data.attrs["lkv_sign_convention"] = item["track-config"]["lkv_sign_convention"];
        track_data.attrs["coordinate_reference_system"] = item["track-config"]["coordinate_reference_system"];
        track_data.attrs["time_series_units"] = item["track-config"]["time_series_units"];
        track_data.attrs["velocity_units"] = item["track-config"]["velocity_units"];
        track_data.attrs["dem_source"] = item["track-config"]["dem_source"];
        track_data.attrs["dem_heights"] = item["track-config"]["dem_heights"];
        track_data.attrs["time_start"] = item["track-config"]["start_time"];
        track_data.attrs["time_end"] = item["track-config"]["end_time"];
        track_data.attrs["time_steps_number"] = item["track-config"]["n_times"];
        track_data.attrs["reference_image"] = item["track-config"]["reference_image"];
        track_data.attrs["reference_frame"] = item["track-config"]["reference_frame"];

        # Package grid information
        # data now has onetrack_datastructure = [lkv_datastructure, velocity_datastructure, ts_datastructure]
        lkv_datastruct = data[0];
        grid_group = track_data.create_group('Grid_Info')
        grid_group.create_dataset('lon', data=lkv_datastruct[0]);
        grid_group.create_dataset('lat', data=lkv_datastruct[1]);
        grid_group.create_dataset('lkv_E', data=lkv_datastruct[2]);
        grid_group.create_dataset('lkv_N', data=lkv_datastruct[3]);
        grid_group.create_dataset('lkv_U', data=lkv_datastruct[4]);
        grid_group.create_dataset('dem', data=lkv_datastruct[5]);

        # Package velocity information
        if write_velocities:
            vel_datastruct = data[1];
            vel_group = track_data.create_group('Velocities')
            vel_group.create_dataset('velocities', data=vel_datastruct[0]);

        # Package time series information
        if write_time_series:
            ts_datastructure = data[2];
            datelist = ts_datastructure[0]
            ts_group = track_data.create_group('Time Series');
            for i in range(len(datelist)):
                ts_group.create_dataset(datelist[i], data=ts_datastructure[1][i]);

    hf.close();
    return;
