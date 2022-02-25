
import h5py
import numpy as np
from . import io_cgm_hdf5


def convert_cgm_to_mintpy(cgm_filename, out_mintpy_filename):
    """Read CGM data. Write mini file of mintpy data.

    :param cgm_filename: string
    :param out_mintpy_filename: string
    """
    [track_dict] = io_cgm_hdf5.read_cgm_hdf5_full_data(cgm_filename);
    write_pseudo_mintpy_file(track_dict, out_mintpy_filename);
    return;


def read_overview_mintpy_file(filename):
    """ Just a scratch function to view array shapes and metadata from Mintpy files"""
    print("Reading file %s " % filename);
    hf = h5py.File(filename, 'r');   # hf has keys(): ["bperp", "date", "timeseries"]
    array = hf.get('timeseries')   # getting a Dataset
    x = np.array(array);  # getting the 3D data cube
    print("Shape of mintpy timeseries:", np.shape(x))
    width, length = hf.attrs["WIDTH"], hf.attrs["LENGTH"]  # getting metadata
    print("WIDTH, LENGTH:", width, length)
    ref_x, ref_y = hf.attrs["REF_X"], hf.attrs["REF_Y"]  # getting metadata
    print("REF_X, REF_Y:", ref_x, ref_y)
    utc = hf.attrs["CENTER_LINE_UTC"]  # getting metadata
    print("UTC:", utc)
    return;


def get_cgm_dates(track_dict):
    """
    Start with a Track_dict.
    Return a list of acquisition dates in byte-string YYYYMMDD format, like b"20190622"
    """
    dates = [str(x[0:8]).encode() for x in track_dict.keys() if len(x) == 15 and x[0] in ['1', '2']];
    return dates;


def get_cgm_data_cube(track_dict):
    """
    Start with a Track_dict. Return a 3D data cube flipped in ascending order.
    """
    dates = [x for x in track_dict.keys() if len(x) == 15 and x[0] in ['1', '2']];
    slice_shape = np.shape(track_dict[dates[0]]);
    total_shape = (len(dates), slice_shape[0], slice_shape[1]);
    total_cube = np.zeros(total_shape);
    for i in range(len(dates)):
        total_cube[i, :, :] = track_dict[dates[i]];
    return total_cube;


def write_pseudo_mintpy_file(track_dict, output_filename):
    """
    Write a barebones mintpy file with data from a CGM track.
    Populate a few necessary metadata fields, leaving others unpopulated
    """
    dtarray = get_cgm_dates(track_dict);   # return a list of byte strings associated with each acquisition date
    data_cube = get_cgm_data_cube(track_dict);   # return a 3D data array
    refdate = track_dict["reference_image"]  # string, YYYYMMDD
    reflon = track_dict["reference_frame"].split('/')[1]
    reflat = track_dict["reference_frame"].split('/')[2]

    print("Writing file %s" % output_filename);
    hf = h5py.File(output_filename, 'w');
    hf.create_dataset('bperp', (len(dtarray),));
    hf.create_dataset('date', (len(dtarray),), dtype='|S8', data=dtarray);
    # THIS WANTS TO BE FLIPPED NORTH SOUTH
    hf.create_dataset('timeseries', np.shape(data_cube), dtype='<f4', data=np.multiply(data_cube, 0.001));  # in meters
    hf.attrs["LENGTH"] = np.shape(data_cube)[1];
    hf.attrs["WIDTH"] = np.shape(data_cube)[2];
    hf.attrs["START_DATE"] = dtarray[0];
    hf.attrs["END_DATE"] = dtarray[-1];
    hf.attrs["REF_DATE"] = refdate;
    hf.attrs["REF_LON"] = reflon
    hf.attrs["REF_LAT"] = reflat
    refx = np.abs(track_dict["lon"] - float(reflon)).argmin()
    refy = np.abs(track_dict["lat"] - float(reflat)).argmin()
    hf.attrs["REF_X"] = refx
    hf.attrs["REF_Y"] = refy;
    hf.attrs["CENTER_LINE_UTC"] = 0;
    return;
