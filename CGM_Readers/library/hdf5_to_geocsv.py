"""
Library functions to generate a geoCSV file for each time series pixel queried
"""

from . import io_cgm_hdf5
import numpy as np


def extract_csv(hdf_file, pixel_list, output_dir):
    """
    Write GeoCSV for a list of one or more pixels and tracks. Pixel_list must have [lon, lat, track]
    :param hdf_file: name of SCEC HDF5 File
    :param pixel_list: list of structures [lon, lat, track]
    :param output_dir: directory where pixels' GeoCSVs will live
    """
    cgm_data_structure = io_cgm_hdf5.read_cgm_hdf5_full_data(hdf_file);
    for pixel in pixel_list:
        desired_track = pixel[2];

        # First find the track that we're working on.
        track_idx = 0;  # temporary. Will be replaced with finding desired track.
        track_data_structure = cgm_data_structure[track_idx];
        track_metadata = track_data_structure[0];
        track_total_data = track_data_structure[1];
        lkv_data = track_total_data[0];
        lon_array = lkv_data[0];
        lat_array = lkv_data[1];
        ts_data = track_total_data[2];

        # Find the nearest row and column in the array
        rownum, colnum = get_nearest_rowcol(pixel, lon_array, lat_array);
        # THERE IS A BUG HERE. WILL COME BACK TOMORROW.
        print(lon_array);
        print(lat_array);
        print(rownum, colnum);

        # Extract pixel time series data
        pixel_time_series = extract_pixel(ts_data, rownum, colnum);

        outfile = output_dir+"/test_pixel.csv";
        write_csv(pixel, track_metadata, pixel_time_series, outfile);
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
    colnum = np.abs(lon_array - pixel_lon).argmin()
    rownum = np.abs(lat_array - pixel_lat).argmin();
    return rownum, colnum;


def extract_pixel(ts_data, rownum, colnum):
    """
    Extract the time series for a particular pixel
    :param ts_data: data structure [dates, many arrays]
    :param rownum: int
    :param colnum: int
    :return: array of dates, array of numbers
    """
    dates_array = ts_data[0];
    full_grids = ts_data[1];
    single_time_series = [];
    for i in range(len(full_grids)):
        single_time_series.append(full_grids[i][rownum][colnum]);
    dates_array = [x.decode() for x in np.array(dates_array)];
    return dates_array, single_time_series;


def write_csv(pixel, metadata_dictionary, pixel_time_series, outfile):
    """
    :param pixel: structure with [lon, lat, track]
    :param metadata_dictionary: a dictionary with many attributes
    :param pixel_time_series: [list of dates, list of displacements]
    :param outfile: name of file where csv will be stored
    :return: nothing
    """
    ofile = open(outfile, 'w');
    ofile.write("%f, %f, %s \n" % (pixel[0], pixel[1], metadata_dictionary["track_name"]));
    for i in range(len(pixel_time_series[0])):
        ofile.write("%s, %f\n" % (pixel_time_series[0][i], pixel_time_series[1][i]) );
    ofile.close();
    return;
