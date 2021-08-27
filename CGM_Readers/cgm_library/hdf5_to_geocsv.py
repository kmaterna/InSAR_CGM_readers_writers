"""
Library functions to generate a geoCSV file for each time-series pixel queried
"""

from . import io_cgm_hdf5
import numpy as np
import datetime as dt
import re


def extract_csv_wrapper(hdf_file_list, pixel_list, output_dir):
    """
    Multiple-HDF5-File access function for sending multiple tracks, multiple pixels to GeoCSV.
    One track per geoCSV (we are not storing more than one look vector in GeoCSV header).
    Pixel_list must have [lon, lat].
    :param hdf_file_list: name of one or several SCEC HDF5 Files, list
    :param pixel_list: list of structures [lon, lat]
    :param output_dir: directory where pixels' GeoCSVs will live
    """
    for hdf_file in hdf_file_list:
        extract_csv_from_file(hdf_file, pixel_list, output_dir);
    return;


def extract_vels_wrapper(hdf_file_list, pixel_list):
    """
    Multiple-HDF5-File access function for sending multiple tracks, multiple pixel velocities
    Pixel_list must have [lon, lat].
    :param hdf_file_list: name of one or several SCEC HDF5 Files, list
    :param pixel_list: list of structures [lon, lat]
    :returns: velocity_list: list of velocities in mm/yr, look vectors, and track numbers. ex: [0.0, [lkvENU], 'D071']
    """
    velocity_list = [];
    for hdf_file in hdf_file_list:
        velocity_list_one_track = extract_vel_from_file(hdf_file, pixel_list);
        velocity_list = velocity_list + velocity_list_one_track;
    return velocity_list;


def extract_csv_from_file(hdf_file, pixel_list, output_dir):
    """
    Single-HDF5-File access function: Write GeoCSVs for a list of one or more pixels.
    Pixel_list must have [lon, lat].
    :param hdf_file: name of SCEC HDF5 File
    :param pixel_list: list of structures [lon, lat]
    :param output_dir: directory where pixels' GeoCSVs will live
    """
    cgm_data_structure = io_cgm_hdf5.read_cgm_hdf5_full_data(hdf_file);  # list of tracks
    for pixel in pixel_list:

        # Find each track in hdf5 file
        for track_dict in cgm_data_structure:
            current_track = track_dict["track_name"];
            # Find nearest row and column in array
            rownum, colnum = get_nearest_rowcol(pixel, track_dict["lon"], track_dict["lat"]);
            if np.isnan(rownum):
                # print("Pixel", pixel, "is outside bounding box for track %s " % current_track);  # just logging
                continue;  # pixel is outside bounding box of this track

            # Extract pixel time series data
            pixel_time_series = extract_pixel_ts(track_dict, rownum, colnum);
            pixel_lkv = [track_dict["lkv_E"][rownum][colnum],
                         track_dict["lkv_N"][rownum][colnum],
                         track_dict["lkv_U"][rownum][colnum]]
            pixel_hgt = track_dict["dem"][rownum][colnum];
            if np.sum(np.isnan(pixel_time_series[1])) == len(pixel_time_series[1]):   # if all values are np.nan
                # print("Pixel", pixel, "is not in valid-data domain for track %s " % current_track);  # just logging
                continue;  # pixel is outside valid data domain of this track

            # Write GeoCSV format
            outfile = output_dir+"/pixel_"+str(pixel[0])+"_"+str(pixel[1])+"_"+str(current_track)+".csv";
            write_geocsv2p0(pixel, track_dict, pixel_time_series, pixel_lkv, pixel_hgt, outfile);
    return;


def extract_vel_from_file(hdf_file, pixel_list):
    """
    Single-HDF5-File access function: get velocities for 1 or more pixels
    Pixel_list must have [lon, lat].
    :param hdf_file: name of SCEC HDF5 File
    :param pixel_list: list of structures [lon, lat]
    :returns: velocity_list: list of velocities in mm/yr, look vectors, and track numbers. ex: [0.0, [lkvENU], 'D071']
    """
    cgm_data_structure = io_cgm_hdf5.read_cgm_hdf5_full_data(hdf_file);  # list of tracks
    velocity_list = [];
    for pixel in pixel_list:

        # Find each track in hdf5 file
        for track_dict in cgm_data_structure:
            current_track = track_dict["track_name"];
            # Find nearest row and column in array
            rownum, colnum = get_nearest_rowcol(pixel, track_dict["lon"], track_dict["lat"]);
            if np.isnan(rownum):
                # print("Pixel", pixel, "is outside bounding box for track %s " % current_track);  # just logging
                continue;  # pixel is outside bounding box of this track

            # Extract pixel time series data
            [pixel_vel, lkv] = extract_pixel_vel(track_dict, rownum, colnum);
            velocity_list.append([pixel_vel, lkv, current_track]);

    return velocity_list;


def get_nearest_rowcol(pixel, lon_array, lat_array):
    """
    :param pixel: [lon, lat]
    :param lon_array: 1D array of numbers representing geocoded longitudes in geocoded array
    :param lat_array: 1D array of numbers representing geocoded latitudes in geocoded array
    :return: rownum, colnum
    """
    pixel_lon = pixel[0];
    pixel_lat = pixel[1];
    if pixel_lon < lon_array[0] or pixel_lon > lon_array[-1]:
        return np.nan, np.nan
    if pixel_lat < lat_array[0] or pixel_lat > lat_array[-1]:
        return np.nan, np.nan
    colnum = np.argmin(np.abs(lon_array - pixel_lon));
    rownum = np.argmin(np.abs(lat_array - pixel_lat));
    return rownum, colnum;


def extract_pixel_ts(track_dict, rownum, colnum):
    """
    Extract time series slice for a particular pixel
    :param track_dict: data structure
    :param rownum: int
    :param colnum: int
    :return: array of dates, array of numbers
    """
    dates_array, single_ts, single_unc = [], [], [];
    for keyname in track_dict.keys():
        if re.match(r"[0-9]{8}T[0-9]{6}", keyname):  # if we have time series slice, such as '20150121T134347'
            dates_array.append(dt.datetime.strptime(keyname, "%Y%m%dT%H%M%S"));
            single_ts.append(track_dict[keyname][rownum][colnum]);
            single_unc.append(0);
    # Put dates_array and single_time_series in proper chronological order
    single_time_series = [x for _, x in sorted(zip(dates_array, single_ts))];
    single_unc_series = [x for _, x in sorted(zip(dates_array, single_unc))];
    dates_array = sorted(dates_array);
    return [dates_array, single_time_series, single_unc_series];


def extract_pixel_vel(track_dict, rownum, colnum):
    """
    Extract velocity / LOS for a particular pixel
    :param track_dict: data structure
    :param rownum: int
    :param colnum: int
    :return: velocity, array of [ENU] look vector
    """
    velocity = track_dict["velocities"][rownum][colnum];
    lkv_e = track_dict["lkv_E"][rownum][colnum]
    lkv_n = track_dict["lkv_N"][rownum][colnum]
    lkv_u = track_dict["lkv_U"][rownum][colnum]
    return [velocity, [lkv_e, lkv_n, lkv_u]];


def write_geocsv2p0(pixel, metadata_dictionary, pixel_time_series, lkv, pixel_hgt, outfile):
    """
    :param pixel: structure with [lon, lat]
    :param metadata_dictionary: a dictionary with many attributes
    :param pixel_time_series: [list_of_dts, list_of_displacements, list_of_uncs]
    :param lkv: [lkv_e, lkv_n, lkv_u]
    :param pixel_hgt: height of target point on DEM
    :param outfile: name of file where csv will be stored
    :return: nothing
    """
    print("Writing %s " % outfile);
    ofile = open(outfile, 'w');
    ofile.write("# dataset: GeoCSV 2.0\n");
    ofile.write("# field_unit: ISO 8601 datetime UTC, mm, mm\n");
    ofile.write("# field_type: string, float, float\n");
    ofile.write("# attribution: %s \n" % metadata_dictionary["citation_info"]);
    ofile.write("# Request_URI: %s \n" % metadata_dictionary["website_link"]);
    ofile.write("# Source file: %s \n" % metadata_dictionary["filename"].split('/')[-1]);
    ofile.write("# SAR mission: %s \n" % metadata_dictionary["platform"]);
    ofile.write("# SAR track: %s\n" % metadata_dictionary["track_name"]);
    ref_lon = float(metadata_dictionary["reference_frame"].split('/')[1]);
    ref_lat = float(metadata_dictionary["reference_frame"].split('/')[2]);
    ofile.write("# LLH Reference Coordinate: Lon: %f; Lat: %f; Hgt: [future]\n" % (ref_lon, ref_lat) );
    ofile.write("# Geometry Reference Date: %s \n" % metadata_dictionary["reference_image"] );
    ofile.write("# TS Reference Date: \n");
    ofile.write("# Displacement Sign: %s \n" % metadata_dictionary["los_sign_convention"].replace(',', ';') );
    ofile.write("# Line-Of-Sight vector: E: %f; N: %f; U: %f\n" % (lkv[0], lkv[1], lkv[2]));
    ofile.write("# LLH Pixel: Lon: %f; Lat: %f; Hgt: %f\n" % (pixel[0], pixel[1], pixel_hgt));
    ofile.write("# Pixel Height: %s \n" % metadata_dictionary["dem_heights"] );
    ofile.write("# Version: %s \n" % metadata_dictionary["version"]);
    ofile.write("# DOI: %s \n" % metadata_dictionary["doi"]);
    ofile.write("Datetime, LOS, Std Dev LOS\n");
    for i in range(len(pixel_time_series[0])):
        dt_string = dt.datetime.strftime(pixel_time_series[0][i], "%Y-%m-%dT%H:%M:%SZ");
        ofile.write("%s, %f, %f\n" % (dt_string, pixel_time_series[1][i], pixel_time_series[2][i]) );
    ofile.close();
    return;
