"""
Library functions to generate a geoCSV file for each time-series pixel queried
"""

from . import io_cgm_hdf5
import numpy as np
import datetime as dt
import re
import json


def extract_csv_wrapper(hdf_file_list, pixel_list, output_dir):
    """
    Multiple-HDF5-File access function for sending multiple tracks, multiple pixels to GeoCSV.
    One track per geoCSV (we are not storing more than one look vector in GeoCSV header).
    Pixel_list must have [lon, lat].
    :param hdf_file_list: name of one or several SCEC HDF5 Files, list
    :param pixel_list: list of structures [lon, lat]
    :param output_dir: directory where pixels' GeoCSVs will live
    :returns: a list of pixel structures of metadata with velocity: [lon, lat, vel, lkv, track]
    for convenient extracting of one pixel TS on the public website.
    """
    pixel_structure_list = [];
    for hdf_file in hdf_file_list:
        pixel_structures = extract_csv_from_file(hdf_file, pixel_list, output_dir);
        pixel_structure_list = pixel_structure_list + pixel_structures;
    return pixel_structure_list;


def extract_vels_wrapper(hdf_file_list, pixel_list):
    """
    Multiple-HDF5-File access function for sending multiple tracks, multiple pixel velocities
    Pixel_list must have [lon, lat].
    :param hdf_file_list: name of one or several SCEC HDF5 Files, list
    :param pixel_list: list of structures [lon, lat]
    :returns: velocity_list: list of velocities in mm/yr, look vectors, and track numbers.
    ex: [lon, lat, 0.0, [lkvENU], 'D071']
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
    :returns: a list of pixel structures of metadata [lon, lat, vel, lkv, ]
    for convenient extracting of one pixel TS on the public website.
    """
    cgm_data_structure = io_cgm_hdf5.read_cgm_hdf5_full_data(hdf_file);  # list of tracks
    pixel_structures = extract_csv_from_cgm_data_structure(cgm_data_structure, pixel_list, output_dir);
    # perform CSV write function
    return pixel_structures;


def extract_vel_from_file(hdf_file, pixel_list):
    """
    Single-HDF5-File access function: get velocities for 1 or more pixels
    Pixel_list must have [lon, lat].
    :param hdf_file: name of SCEC HDF5 File
    :param pixel_list: list of structures [lon, lat]
    :returns: velocity_list: list of velocities in mm/yr, look vectors, and track numbers.
    ex: [lon, lat, 0.0, [lkvENU], 'D071']
    """
    cgm_data_structure = io_cgm_hdf5.read_cgm_hdf5_full_data(hdf_file);  # list of tracks
    velocity_list = extract_vel_from_cgm_data_structure(cgm_data_structure, pixel_list);
    return velocity_list;


def write_full_track_vels_to_csv(hdf_file, output_dir):
    """
    Writes a CSV of all velocities within one track. Takes a minute and writes a large file. Useful for caching.
    :param hdf_file: name of HDF file with one or more tracks
    :param output_dir: string
    :returns: bounding box metadata, [W, E, S, N, nx, ny]
    """
    cgm_data_structure = io_cgm_hdf5.read_cgm_hdf5_full_data(hdf_file);  # list of tracks
    track_dict = cgm_data_structure[0];  # take the first track, a safe assumption given we use 1-track-per-file
    bounding_box = [np.min(track_dict["lon"]), np.max(track_dict["lon"]),
                    np.min(track_dict["lat"]), np.max(track_dict["lat"])];
    pixel_list, bounding_box_metadata = unpack_bounding_box(bounding_box);  # 1D list of pixels (each are [lon, lat])
    velocity_list = extract_vel_from_cgm_data_structure(cgm_data_structure, pixel_list);
    write_vels_to_csv(velocity_list, output_dir);  # Then write to CSV
    return bounding_box_metadata;


def velocities_to_csv(hdf_file, bounding_box, output_dir):
    """
    Writes a CSV of velocities within the bounding box
    :param hdf_file: name of HDF file with one or more tracks
    :param bounding_box: [W, E, S, N] in longitude and latitude
    :param output_dir: string
    :returns: bounding box metadata, [W, E, S, N, nx, ny]
    """
    cgm_data_structure = io_cgm_hdf5.read_cgm_hdf5_full_data(hdf_file);  # list of tracks
    pixel_list, bounding_box_metadata = unpack_bounding_box(bounding_box);  # 1D list of pixels (each are [lon, lat])
    velocity_list = extract_vel_from_cgm_data_structure(cgm_data_structure, pixel_list);
    write_vels_to_csv(velocity_list, output_dir);  # Then write to CSV
    return bounding_box_metadata;


def velocities_to_json(hdf_file, bounding_box, output_dir):
    """
    Writes a json of velocities within the bounding box
    :param hdf_file: name of HDF file with one or more tracks
    :param bounding_box: [W, E, S, N] in longitude and latitude
    :param output_dir: string
    :returns: bounding box metadata [W, E, S, N, nx, ny]
    """
    cgm_data_structure = io_cgm_hdf5.read_cgm_hdf5_full_data(hdf_file);  # list of tracks
    pixel_list, bounding_box_metadata = unpack_bounding_box(bounding_box);  # 1D list of pixels (each are [lon, lat])
    velocity_list = extract_vel_from_cgm_data_structure(cgm_data_structure, pixel_list);
    write_vels_to_json(velocity_list, output_dir);  # Then write to JSON
    return bounding_box_metadata;


def extract_vel_from_cgm_data_structure(cgm_data_structure, pixel_list):
    """
    get velocities for 1 or more pixels
    Pixel_list must have [lon, lat].
    :param cgm_data_structure: list of dictionaries
    :param pixel_list: list of structures [lon, lat]
    :returns: velocity_list: list of velocities in mm/yr, look vectors, and track numbers.
    ex: [lon, lat, 0.0, [lkvENU], 'D071']
    """
    pixel_found_list, velocity_list = [], [];
    for pixel in pixel_list:
        # Find each track in data structure
        for track_dict in cgm_data_structure:
            current_track = track_dict["track_name"];
            # Find nearest row and column in array
            rownum, colnum = get_nearest_rowcol(pixel, track_dict["lon"], track_dict["lat"]);
            if np.isnan(rownum):
                # print("Pixel", pixel, "is outside bounding box for track %s " % current_track);  # just logging
                continue;  # pixel is outside bounding box of this track

            # Extract pixel time series data
            [lon_found, lat_found, pixel_vel, lkv] = extract_pixel_vel(track_dict, rownum, colnum);
            velocity_list.append([lon_found, lat_found, pixel_vel, lkv, current_track]);
    return velocity_list;


def extract_csv_from_cgm_data_structure(cgm_data_structure, pixel_list, output_dir):
    """
    Writes GeoCSV. Pixel_list must have [lon, lat].
    :param cgm_data_structure: list of dictionaries
    :param pixel_list: list of structures [lon, lat]
    :param output_dir: directory where pixels' GeoCSVs will live
    :returns: a list of pixel structures of metadata [lon, lat, vel, lkv, ]
    for convenient extracting of one pixel TS on the public website.
    """
    pixel_structures = [];
    for pixel in pixel_list:

        # Find each track in hdf5 file
        for track_dict in cgm_data_structure:
            current_track = track_dict["track_name"];
            # Find nearest row and column in array
            rownum, colnum = get_nearest_rowcol(pixel, track_dict["lon"], track_dict["lat"]);
            if np.isnan(rownum):
                # print("Pixel", pixel, "is outside bounding box for track %s " % current_track);  # just logging
                pixel_structures.append([]);   # error code for velocity out of bounds
                continue;  # pixel is outside bounding box of this track

            # Extract pixel time series data
            pixel_time_series = extract_pixel_ts(track_dict, rownum, colnum);
            pixel_lkv = [track_dict["lkv_E"][rownum][colnum],
                         track_dict["lkv_N"][rownum][colnum],
                         track_dict["lkv_U"][rownum][colnum]]
            pixel_hgt = track_dict["dem"][rownum][colnum];
            pixel_velocity = track_dict["velocities"][rownum][colnum];
            if np.sum(np.isnan(pixel_time_series[1])) == len(pixel_time_series[1]):   # if all values are np.nan
                # print("Pixel", pixel, "is not in valid-data domain for track %s " % current_track);  # just logging
                pixel_structures.append([]);  # error code for no velocity data
                continue;  # pixel is outside valid data domain of this track

            # Write GeoCSV format
            pixel_lon_found = np.round(track_dict["lon"][colnum], 3);   # filename based on nearest InSAR pixel
            pixel_lat_found = np.round(track_dict["lat"][rownum], 3);   # filename based on nearest InSAR pixel
            pixel_found = [pixel_lon_found, pixel_lat_found];
            # print(pixel_lon_found, pixel_lat_found);   # debugging
            outfile = output_dir+"/pixel_"+str(pixel_lon_found)+"_"+str(pixel_lat_found)+"_"+str(current_track)+".csv";
            write_geocsv2p0(pixel_found, track_dict, pixel_time_series, pixel_lkv, pixel_hgt, outfile);  # write csv
            pixel_metadata = [pixel_lon_found, pixel_lat_found, pixel_velocity, pixel_lkv, current_track];
            pixel_structures.append(pixel_metadata);   # save off pixel velocity and metadata
    return pixel_structures;


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


def unpack_bounding_box(bounding_box, xinc=0.002, yinc=0.002):
    """
    Just a geometric function on a bounding box. xinc and yinc are in degrees
    Default xinc/yinc are same as default posting for cgm insar product
    We start on a valid InSAR pixel (rounded to odd increments of 0.002).
    Returns a 1D list of pixels, in the form [lon, lat]
    Returns an expended bounding box metadata: [W, E, S, N, nx, ny]
    """
    [w, e, s, n] = bounding_box;
    w = nearest_odd_thousanth(w, -0.001);
    e = nearest_odd_thousanth(e, 0.001);
    s = nearest_odd_thousanth(s, -0.001);
    n = nearest_odd_thousanth(n, 0.001);
    lon_array = np.arange(w, e, xinc);
    lat_array = np.arange(s, n, yinc);
    X, Y = np.meshgrid(lon_array, lat_array);
    pixel_list = np.vstack([X.ravel(), Y.ravel()])
    pixel_list = [[pixel_list[0][i], pixel_list[1][i]] for i in range(len(pixel_list[0]))];  # unpacking
    expanded_bounding_box = [w, e, s, n, len(lon_array), len(lat_array)];
    return pixel_list, expanded_bounding_box;


def nearest_odd_thousanth(number, potential_offset):
    """Take an arbitrary number, and return the nearest InSAR pixel coordinate, given that pixels are every 0.002 on
    odd numbered thousanths"""
    retval = np.round(number, 3);
    if np.mod(retval*1000, 2) == 0:
        retval = retval + potential_offset;
    return retval;


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
    :return: lon, lat, velocity, array of [ENU] look vector
    """
    pixel_lon_found = np.round(track_dict["lon"][colnum], 3);  # nearest InSAR pixel
    pixel_lat_found = np.round(track_dict["lat"][rownum], 3);  # nearest InSAR pixel
    velocity = track_dict["velocities"][rownum][colnum];
    lkv_e = track_dict["lkv_E"][rownum][colnum]
    lkv_n = track_dict["lkv_N"][rownum][colnum]
    lkv_u = track_dict["lkv_U"][rownum][colnum]
    return [pixel_lon_found, pixel_lat_found, velocity, [lkv_e, lkv_n, lkv_u]];


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


def write_vels_to_csv(velocity_list, output_dir):
    """Write pixels and their locations / velocities / Look vectors / tracks into a CSV file"""
    if len(velocity_list) == 0:
        print("No pixels found. Not creating velocity csv. ");
        return;
    ofile = open(output_dir+"/velocity_list.csv", 'w');
    ofile.write("# lon, lat, velocity(mm/yr), lkv_E, lkv_N, lkv_U, track\n");
    for item in velocity_list:
        ofile.write("%f, %f, " % (item[0], item[1]) );
        ofile.write("%f, %f, %f, %f, %s\n" % (item[2], item[3][0], item[3][1], item[3][2], item[4]) );
    ofile.close();
    return;


def write_vels_to_json(velocity_list, output_dir):
    """Write pixels and their locations / velocities / Look vectors / tracks into a JSON file"""
    dictionary_list = [];
    for item in velocity_list:
        dictionary_list.append({"lon": item[0].astype(float), "lat": item[1].astype(float),
                                "velocity": item[2].astype(float),
                                "lkv_E": item[3][0].astype(float), "lkv_N": item[3][1].astype(float),
                                "lkv_U": item[3][2].astype(float), "track": item[4]});
    with open(output_dir+"/velocity_list.json", 'w') as fp:
        json.dump(dictionary_list, fp);
    return;
