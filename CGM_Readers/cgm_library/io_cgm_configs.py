"""
Library functions to create and write config files for InSAR CGM products
"""

import configparser
import os


def read_file_level_config(configfile):
    """Read a file_level_config into an object (works kind of like a dictinoary)"""
    print("Reading file dictionary config file: ", configfile);
    assert(os.path.isfile(configfile)), FileNotFoundError("config file "+configfile+" not found.");
    configobj = configparser.ConfigParser();
    configobj.read(configfile);
    return configobj;


def write_empty_file_level_config(directory):
    """Produce an empty template for file_level_config file"""
    configobj = configparser.ConfigParser()
    configobj["general-config"] = {};
    genconfig = configobj["general-config"];
    genconfig["hdf5_file"] = "test_cgm_insar_total.hdf5"
    genconfig["hdf5_vel_file"] = "test_cgm_insar_vels.hdf5"
    genconfig["tracks"] = "[D071]"
    genconfig["scec_cgm_version"] = "0.0.1"
    genconfig["website_link"] = "[future]"
    genconfig["documentation_link"] = "[future]"
    genconfig["citation_info"] = "[future]"
    genconfig["contributing_institutions"] = "UC San Diego, UC Berkeley, UC Riverside, US Geological Survey, NASA JPL"
    genconfig["contributing_researchers"] = "Ekaterina Tymofyeyeva, David Sandwell, Xiaohua Xu, Zhen Liu, Kathryn " \
                                            "Materna, Kang Wang, Gareth Funning, David Bekaert, Michael Floyd, " \
                                            "Katherine Guns, Niloufar Abolfathian "
    genconfig["doi"] = "[future]"

    configobj["D071-config"] = {};
    trackconfig = configobj["D071-config"];
    trackconfig["unit_east_ll_grd"] = ""
    trackconfig["unit_north_ll_grd"] = ""
    trackconfig["unit_up_ll_grd"] = ""
    trackconfig["dem_ll_grd"] = ""
    trackconfig["safes_list"] = ""
    trackconfig["velocity_ll_grd"] = ""
    trackconfig["ts_directory"] = ""
    trackconfig["metadata_file"] = ""
    with open(directory+'/empty_file_level_config.txt', 'w') as configfile:
        configobj.write(configfile)
    print("Writing file %s " % directory+"/empty_file_level_config.txt");
    return;


def read_track_metadata_config(configfile):
    """Read a track metadata config into an object (works kind of like a dictinoary)"""
    print("Reading track metadata config file: ", configfile);
    assert(os.path.isfile(configfile)), FileNotFoundError("config file "+configfile+" not found.");
    configobj = configparser.ConfigParser();
    configobj.read(configfile);
    return configobj;


def write_empty_track_metadata_config(directory):
    """Produce an empty template for track metadata config file (information that can change with each track)"""
    configobj = configparser.ConfigParser()
    configobj["track-config"] = {};
    genconfig = configobj["track-config"];
    genconfig["track_name"] = ""
    genconfig["platform"] = "Sentinel-1"
    genconfig["orbit_direction"] = ""
    genconfig["polygon_boundaries"] = "lon1/lat1, lon2/lat2, lon3/lat3, lon4/lat4"
    genconfig["geocoded_increment"] = "-Ixinc/yinc"
    genconfig["geocoded_range"] = "-Rw/e/s/n"
    genconfig["approx_posting"] = "200m"
    genconfig["grdsample_flags"] = ""
    genconfig["los_sign_convention"] = "positive towards satellite, negative away from satellite"
    genconfig["lkv_sign_convention"] = "vector from ground to satellite in local enu coordinates"
    genconfig["coordinate_reference_system"] = ""
    genconfig["time_series_units"] = "mm"
    genconfig["velocity_units"] = "mm/yr"
    genconfig["dem_source"] = "SRTM3"
    genconfig["dem_heights"] = "ellipsoid"
    genconfig["start_time"] = ""
    genconfig["end_time"] = ""
    genconfig["n_times"] = ""
    genconfig["reference_image"] = ""
    genconfig["reference_frame"] = ""
    with open(directory+'/empty_track_metadata.txt', 'w') as configfile:
        configobj.write(configfile)
    print("Writing file %s " % directory + "/empty_track_metadata.txt");
    return;

def build_config_dict(data_dict_list):
    """
    Build a file-level-config dictionary from a dictionary of data for one track, instead of reading it from file.
    """
    data_dict = data_dict_list[0];  # extract one track worth of data
    config_object = {};
    gen_obj = {"scec_cgm_version": data_dict['version'],
               "website_link": data_dict['website_link'],
               "documentation_link": data_dict['documentation_link'],
               "citation_info": data_dict['citation_info'],
               "contributing_institutions": data_dict['contributing_institutions'],
               "contributing_researchers": data_dict['contributing_researchers'],
               "hdf5_file": data_dict['filename'],
               "doi": data_dict['doi']};
    config_object["general-config"] = gen_obj;
    return config_object;
