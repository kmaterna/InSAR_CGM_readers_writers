## Readers and Writers for the SCEC Commuinity Geodetic Model InSAR Products

### OVERVIEW
We aim to present the SCEC CGM InSAR Product as a single HDF5 file that can be parsed and presented by the SCEC CGM website. 

**For standard users:** we want the CGM website to run a script that extracts a velocity or time series at one or more lon/lat pairs and returns a time series in geoCSV for the user.   

**For advanced users:** we want the user to download the full SCEC CGM HDF5 file and parse their own useful features with some guidance and reading tools from SCEC. 


### CGM InSAR HDF5 STRUCTURE 

The current HDF5 structure is envisioned as follows: 
```bash
SCEC_CGM_InSAR.hdf5
    ├── Product_Metadata
    │   └── Attributes
    │     ├── version, data_production_date, filename
    │     ├── scec_website_link, documentation_link, citation_info, DOI 
    │     └── contributing_institutions, contributing_researchers 
    └── Track_D071
        ├── Attributes
        │   ├── platform, orbit_direction
        │   ├── polygon_boundaries
        │   ├── geocoded_increment, geocoded_range, approx_posting, grdsample_flags
        │   ├── los_sign_convention, lkv_sign_convention
        │   ├── coordinate_reference_system
        │   ├── time_series_units, velocity_units
        │   ├── dem_source, dem_heights
        │   ├── start_time, end_time, n_times
        │   ├── reference_image
        │   └── reference_frame
        ├── Grid_Info
        │   ├── lon_array
        │   ├── lat_array
        │   ├── lkv_east_ll_grd
        │   ├── lkv_north_ll_grd
        │   ├── lkv_up_ll_grd
        │   └── dem_ll_grd   
        ├── Time_Series
        │   ├── Time_Array
        │   │   └── dates
        │   ├── Time_Series_Grids
        │   │   ├── 20150327_ll_grd
        │   │   ├── 20150421_ll_grd
        │   │   └── 20150515_ll_grd
        │   │   └── ....
        │   └── Uncertainties
        │       └── (undecided)
        └── Velocities
            ├── velo_unc_grd(undecided)
            └── velocities_grd
```

### NECESSARY TOOLS
To implement the HDF5 file format, the CGM team must create:
1. ~~Function(s) to construct the SCEC CGM HDF5 from the CGM analysis [for internal use only].~~ **DONE**
2. Example reader functions to read the full SCEC HDF5 file into a practical data structure, as an advanced user would do, in several commonly used programming languages:
    * ~~Python~~
    * Matlab
    * Jupyter Notebook
3. ~~A tool to extract a certain pixel's time series from the HDF5 and convert it into a geoCSV.~~  
4. Detailed documentation of the CGM product.


### SCEC CGM USAGE
Directions to package up CGM InSAR HDF5 file from local files: 

1. Clone CGM_Readers repo onto your local machine in a directory that is on your PYTHONPATH. Install requirements from package manager if necessary.
2. Get into fresh directory where you want to do the HDF5 packaging.  
3. From working directory, call ```$PATH_TO_BIN/generage_empty_configs.py .``` in a terminal.  This will generate two empty files into the working directory, "file_level_config.txt" and "TRAC_metadata.txt"
4. Manually fill in all the fields for the appropriate track(s) being packaged in both file_level_config.txt and TRAC_metadata.txt. Information regarding highest-level product metadata or file I/O options specific to your file system will be placed in the file_directory config. Track-specific metadata (nothing file-specific) will be placed in the TRAC_metadata config. When you're done, feel free to move TRAC_metadata into a more reasonable directory closer to the data, and feel free to rename it. Just make sure it can be properly found in the file_level_config.
5. From the working directory, call ```$PATH_TO_BIN/write_cgm_hdf5.py file_level_config.txt```
6. Check out your brand new HDF5 file.  I check the file out on my own computer this way: 
```python
#!/usr/bin/env python
from CGM_Readers import library

filename = "test_SCEC_CGM_InSAR_v0_0_1.hdf5"
library.io_cgm_hdf5.read_cgm_hdf5_demo_python(filename);
```

7. You can extract pixels as GeoCSV using the library. Each pixel's time series will be saved in a GeoCSV file. 
 ```python
#!/usr/bin/env python
from CGM_Readers import library

reference_pixel = [-116.57164, 35.32064, "D071"];
los_angeles = [-118.2437, 34.0522, "D071"];
pixel_list = [reference_pixel, los_angeles];
library.hdf5_to_geocsv.extract_csv_wrapper("test_SCEC_CGM_InSAR_v0_0_1.hdf5", pixel_list, ".");
```
