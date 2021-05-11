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
        │   ├── Time_Series_Grids (format: yyyymmddTHHMMSS, UTC time)
        │   │   ├── 20150327T135156_ll_grd
        │   │   ├── 20150421T135158_ll_grd
        │   │   └── 20150515T135159_ll_grd
        │   │   └── ....
        │   └── Uncertainties
        │       └── (undecided)
        └── Velocities
            ├── velo_unc_grd(undecided)
            └── velocities_grd
```

### SCEC CGM USAGE
Directions to package up CGM InSAR HDF5 file from local files: 

1. Git clone "InSAR_CGM_readers_writers" repo onto your local machine.  Install requirements if necessary (can set up dedicated conda environment if desired).  Install software by calling ```python setup.py install```    
2. Get into directory where you want to do the HDF5 packaging.  
3. From working directory, call ```cgm_generage_empty_configs.py .``` .  This will generate two empty files into the working directory, "file_level_config.txt" and "TRAC_metadata.txt"
4. Manually fill in all the fields for the appropriate track(s) being packaged in both file_level_config.txt and TRAC_metadata.txt. Information regarding highest-level product metadata or file I/O options specific to your file system will be placed in the file_directory config. Track-specific metadata (nothing file-specific) will be placed in the TRAC_metadata config. When you're done, feel free to move TRAC_metadata into a more reasonable directory closer to the data, and feel free to rename it. Just make sure it can be properly found in the file_level_config.
5. From the working directory, call ```cgm_write_hdf5.py file_level_config.txt```



### USER'S CORNER FOR SCEC HDF5 FILE
1. Git clone "InSAR_CGM_readers_writers" repo onto your local machine.  Install requirements if necessary (can set up dedicated conda environment if desired).  Install software by calling ```python setup.py install```
2. Check out your brand new HDF5 file.  One option is to view the basic metadata and its contents in bash:  
```bash
#!/bin/bash 
h5dump --contents test_SCEC_CGM_InSAR_v0_0_1.hdf5    # basic table of contents 
h5dump --header test_SCEC_CGM_InSAR_v0_0_1.hdf5      # detailed metadata table 
h5dump --a /Product_Metadata/version test_SCEC_CGM_InSAR_v0_0_1.hdf5  # view value of attribute
```
Alternately, you can look at the basic metadata in gdal:
```
#!/bin/bash
gdalinfo test_SCEC_CGM_InSAR_v0_0_1.hdf5
```
As a third option, you can look at the basic metadata in Python:
```python
#!/usr/bin/env python
import cgm_library

filename = "test_SCEC_CGM_InSAR_v0_0_1.hdf5"
cgm_library.io_cgm_hdf5.read_cgm_hdf5_demo_python(filename);
```
##### Extracting Data
You can extract pixels as GeoCSV using this library. Each pixel's time series will be saved in a GeoCSV file. 
 ```python
#!/usr/bin/env python
import cgm_library

reference_pixel = [-116.57164, 35.32064, "D071"];
los_angeles = [-118.2437, 34.0522, "D071"];
pixel_list = [reference_pixel, los_angeles];
cgm_library.hdf5_to_geocsv.extract_csv_wrapper("test_SCEC_CGM_InSAR_v0_0_1.hdf5", pixel_list, ".");
```

You can also extract a layer of data for a particular track into a GMT grid file. 
A GMT installation with GDAL is required. 
```bash 
#!/bin/bash

# FILE CONFIGURATION
infile="test_SCEC_CGM_InSAR_v0_0_1.hdf5"
track="Track_D071"
layer="Velocities/velocities"   # reference the metadata table or ToC for exact locations 
outfile="D071_vels.grd"

# EXTACT A SINGLE GRD FILE FROM HDF5 FILE!!!!  
# All three lines are necessary for a complete data extraction.  
gmt_range=`h5dump -a //$track/Grid_Info/gmt_range $infile | grep -o "[0-9.-]*/[0-9.-]*/[0-9.-]*/[0-9.-]*"`   # see what's inside gmt_range attribute
gmt grdedit $infile=gd?HDF5:"$infile"://$track/$layer -R$gmt_range -G$outfile   # send layer out to grdfile, using GDAL. 
gmt grdedit $outfile -T    # turn the file to pixel node registration. Must be done in second step. 

# GMT PLOTTING. 
Range="-121/-115/32/37"
Proj="M5i"
gmt makecpt -T-32/7/1 -Croma > mycpt.cpt
gmt grdimage $outfile -R$range -J$Proj -B1 -Cmycpt.cpt -K -P > out_vel.ps # 
```
Results for velocities of Track D071 are shown below: 

![velocities](https://github.com/kmaterna/InSAR_CGM_readers_writers/blob/master/example_configs/track_71_vels.png)


#### SOFTWARE TO-DOS FOR SCEC TEAM
To implement the HDF5 file format, the CGM team must create:
1. ~~Function(s) to construct the SCEC CGM HDF5 from the CGM analysis [for internal use only].~~ **DONE**
2. Example reader functions to read the full SCEC HDF5 file into a practical data structure, as an advanced user would do, in several commonly used programming languages:
    * ~~Python~~
    * Matlab
    * Jupyter Notebook
3. ~~A tool to extract a certain pixel's time series from the HDF5 and convert it into a geoCSV.~~  
4. Detailed documentation of the CGM product.
