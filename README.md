# Readers and Writers for  SCEC Commuinity Geodetic Model InSAR Products

We aim to present the SCEC CGM InSAR Product as one HDF5 file per track, that can be parsed and presented by the SCEC CGM website and other programs. 

## CGM InSAR HDF5 Structure 

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
        │       └── (not completed)
        └── Velocities
            ├── velo_unc_grd(not completed)
            └── velocities_grd
```


## USER'S CORNER FOR SCEC HDF5 FILE
* Bash/GMT Users: utilities like h5dump, gdal, and GMT can read the HDF5 file.
* Python Users: This repository contains an example Python reader based on the h5py library to bring HDF5 into a dictionary. See "Python Installation" for installation information.  
* Matlab Users: This repository contains an example Matlab reader for the HDF5 file.

### Example 1: Extracting Metadata
Option A: Check out an HDF5 file in bash.  One option is to view the basic metadata and its contents with h5dump:  
```bash
#!/bin/bash 
h5dump --contents test_SCEC_CGM_InSAR_v0_0_1.hdf5    # basic table of contents 
h5dump --header test_SCEC_CGM_InSAR_v0_0_1.hdf5      # detailed metadata table 
h5dump -a /Product_Metadata/filename test_SCEC_CGM_InSAR_v0_0_1.hdf5  # view value of attribute
```
Option B: Alternately, you can look at the basic metadata in gdal:
```bash
#!/bin/bash
gdalinfo test_SCEC_CGM_InSAR_v0_0_1.hdf5
```
Option C: As a third option, you can look at the basic metadata from a dictionary in Python:
```python
#!/usr/bin/env python
import cgm_library

filename = "test_SCEC_CGM_InSAR_v0_0_1.hdf5"
cgm_python_data_structure = cgm_library.io_cgm_hdf5.read_cgm_hdf5_full_data(filename);
print(cgm_python_data_structure[0].keys())
```

### Example 2: Extracting Time Series using Python
You can extract pixels as GeoCSV using this Python library. Each pixel's time series will be saved in a GeoCSV file. 
 ```python
#!/usr/bin/env python
import cgm_library

reference_pixel = [-116.57164, 35.32064];
los_angeles = [-118.2437, 34.0522];
pixel_list = [reference_pixel, los_angeles];
cgm_library.hdf5_to_geocsv.extract_csv_from_file("test_SCEC_CGM_InSAR_v0_0_1.hdf5", pixel_list, ".");
```

### Example 3: Extracting Velocities into other formats using Python
You can extract velocities of individual pixels (returned directly), or of geographic regions (written as CSV or JSON).   Mostly just used by the backend of the CGM website. 
 ```python
#!/usr/bin/env python
import cgm_library

reference_pixel = [-116.57164, 35.32064];
los_angeles = [-118.2437, 34.0522];
pixel_list = [reference_pixel, los_angeles];

# extracting velocities
velocity_list = cgm_library.hdf5_to_geocsv.extract_vel_from_file("test_SCEC_CGM_InSAR_v0_0_1.hdf5", pixel_list);
cgm_library.hdf5_to_geocsv.velocities_to_csv("test_SCEC_CGM_InSAR_v0_0_1.hdf5", [-118.3, -118.2, 34.4, 34.5], "Output");
cgm_library.hdf5_to_geocsv.velocities_to_json("test_SCEC_CGM_InSAR_v0_0_1.hdf5", [-118.3, -118.2, 34.4, 34.5], "Output");
```


### Example 4: Extracting Layers using Bash/GMT
You can also extract a layer of data for a particular track into a GMT grid file. 
A GMT installation with GDAL is required. 
(for more: https://docs.generic-mapping-tools.org/latest/cookbook/features.html?highlight=ndvi#reading-more-complex-multi-band-images-or-grids)
```bash 
#!/bin/bash

# FILE CONFIGURATION
infile="test_SCEC_CGM_InSAR_v0_0_1.hdf5"
track="Track_D071"
dataset="Velocities/velocities"   # reference the file's metadata table (h5dump -n) for exact dataset architecture
outfile="D071_vels.grd"

# EXTACT A SINGLE GRD FILE FROM HDF5 FILE!
# All three lines are necessary for a complete data extraction.  
gmt_range=`h5dump -a //$track/Grid_Info/gmt_range $infile | grep -o "[0-9.-]*/[0-9.-]*/[0-9.-]*/[0-9.-]*"`   # value of gmt_range attribute. 
gmt grdedit $infile=gd?HDF5:"$infile"://$track/$dataset -R$gmt_range -G$outfile   # send layer out to grdfile, using GDAL. 
gmt grdedit $outfile -T    # turn the file to pixel node registration. Must be done in second step.  

# GMT PLOTTING. 
Range="-121/-115/32/37"
gmt makecpt -T-32/7/1 -Croma > mycpt.cpt
gmt grdimage $outfile -R$range -JM5i -B1 -Cmycpt.cpt -K -P > out_vel.ps # 
```
Results for extracting the GMT grd file of velocities in Track D071 are shown below: 

![Velocities](/example_configs/track_071_vels.png)


### Python Installation of cgm_library
The following instructions are useful if you plan to use the cgm_library readers on your own machine to bring HDF5 files into Python dictionaries.   
* Git clone "InSAR_CGM_readers_writers" repo into a desired location for source code on your local machine.   
* Install the (fairly minimal) requirements from requirements.txt. If desired, you can set up a dedicated conda environment using requirements.txt.  
* Install software by calling ```python setup.py install``` from the top-level directory of this repository. 
* Test installation by typing in Python: ```import cgm_library```


## CGM CORNER
Packaging instructions for writing CGM InSAR HDF5 file from local files (mostly for SCEC CGM Team): 

1. Git clone "InSAR_CGM_readers_writers" repo onto your local machine.  Install requirements in requirements.txt. Can set up dedicated conda environment if desired.  Install this software by calling ```python setup.py install``` from the top-level directory of this repository.
2. Get into directory where you want to do the HDF5 packaging.  
3. From working directory, call ```cgm_generage_empty_configs.py .``` .  This will generate two empty files into the working directory, "file_level_config.txt" and "TRAC_metadata.txt"
4. Manually fill in all the fields for the appropriate track(s) being packaged in both file_level_config.txt and TRAC_metadata.txt. Information regarding highest-level product metadata or file I/O options specific to your file system will be placed in the file_directory config. Track-specific metadata (nothing file-specific) will be placed in the TRAC_metadata config. When you're done, feel free to move TRAC_metadata into a more reasonable directory closer to the data, and feel free to rename it. Just make sure it can be properly found in the file_level_config.
5. From the working directory, call ```cgm_write_hdf5.py file_level_config.txt```


## CGM HDF5 to Mintpy HDF5 Time Series
Converting a CGM HDF5 file into a MintPy timeseries file will produce:
- a time series file in mintpy hdf5, in units of meters
- the most important metadata attached (reference pixel, reference image, grid sizes)

To start, enter your favorite Python environment and make sure you have:
* h5py
* numpy
* netCDF4

Clone the CGM reader repo into your favorite Software place on your computer:
```git clone https://github.com/kmaterna/InSAR_CGM_readers_writers.git```

From that directory, in the conda environment you wish to use:
```python setup.py install```

Then, you're ready to convert files into mintpy hdf5.  An example script would be:

```python 
#!/usr/bin/env python

import cgm_library

filedict = {"cgmfile": "path/to/cgm/COMB_hdf5/A064/A064_COMB_CGM_InSAR_v0_0_1.hdf5",
            "output_file": "A064_ts_mintpy.h5"};

if __name__ == "__main__":
    cgm_library.cgm_to_mintpy.convert_cgm_to_mintpy(filedict["cgmfile"], filedict["output_file"]);
    cgm_library.cgm_to_mintpy.read_overview_mintpy_file(filedict["output_file"]);  # just to confirm
```

Then for computing and viewing velocity uncertainties: 
```bash
timeseries2velocity.py A064_ts_mintpy.h5 --bootstrap --bc 1000    # takes about an hour
view.py velocity.h5 velocityStd --pts-ms 5 --pts-marker ks -u 'cm/yr' --flip-ud -v 0 1
```
