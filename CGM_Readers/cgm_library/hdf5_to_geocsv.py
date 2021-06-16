"""
Library functions to generate a geoCSV file for each time series pixel queried
"""

from . import io_cgm_hdf5
import numpy as np
import datetime as dt
import re


def extract_csv_wrapper(hdf_file, pixel_list, output_dir):
    """
    Write GeoCSV for a list of one or more pixels and tracks. Pixel_list must have [lon, lat, track].
    Each pixel can only handle one track for the moment.
    :param hdf_file: name of SCEC HDF5 File
    :param pixel_list: list of structures [lon, lat, track]
    :param output_dir: directory where pixels' GeoCSVs will live
    """
    cgm_data_structure = io_cgm_hdf5.read_cgm_hdf5_full_data(hdf_file);  # list of tracks
    for pixel in pixel_list:
        desired_track = pixel[2];

        # Find the desired track in the hdf5 file
        track_dict = {};
        for item in cgm_data_structure:
            if item["track_name"] == desired_track:
                track_dict = item;
        assert track_dict, ValueError("Desired track %s not found in hdf5 file " % desired_track);

        # Find the nearest row and column in the array
        rownum, colnum = get_nearest_rowcol(pixel, track_dict["lon"], track_dict["lat"]);

        # Extract pixel time series data
        pixel_time_series = extract_pixel_ts(track_dict, rownum, colnum);
        pixel_lkv = [track_dict["lkv_E"][rownum][colnum],
                     track_dict["lkv_N"][rownum][colnum],
                     track_dict["lkv_U"][rownum][colnum]]
        pixel_hgt = track_dict["dem"][rownum][colnum];

        # Write the GeoCSV format
        outfile = output_dir+"/pixel_"+str(pixel[0])+"_"+str(pixel[1])+"_"+str(pixel[2])+".csv";
        write_geocsv2p0(pixel, track_dict, pixel_time_series, pixel_lkv, pixel_hgt, outfile);
    return;


def get_nearest_rowcol(pixel, lon_array, lat_array):
    """
    :param pixel: [lon, lat, track]
    :param lon_array: 1D array of numbers representing geocoded longitudes in the geocoded array
    :param lat_array: 1D array of numbers representing geocoded latitudes in the geocoded array
    :return: rownum, colnum
    """
    pixel_lon = pixel[0];
    pixel_lat = pixel[1];
    colnum = np.argmin(np.abs(lon_array - pixel_lon));
    rownum = np.argmin(np.abs(lat_array - pixel_lat));
    return rownum, colnum;


def extract_pixel_ts(track_dict, rownum, colnum):
    """
    Extract the time series slice for a particular pixel
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
    # Put dates_array and single_time_series in the proper chronological order
    single_time_series = [x for _, x in sorted(zip(dates_array, single_ts))];
    single_unc_series = [x for _, x in sorted(zip(dates_array, single_unc))];
    dates_array = sorted(dates_array);
    return [dates_array, single_time_series, single_unc_series];


def write_geocsv2p0(pixel, metadata_dictionary, pixel_time_series, lkv, pixel_hgt, outfile):
    """
    :param pixel: structure with [lon, lat, track]
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
