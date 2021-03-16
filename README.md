## Readers and Writers for the SCEC Commuinity Geodetic Model InSAR Products

### OVERVIEW
We aim to present the SCEC CGM InSAR Product as a single HDF5 file that can be parsed and presented by the SCEC CGM website. 

**For standard users:** we expect the CGM website to run a script that extracts a velocity or time series at one or more lon/lat pairs and returns a time series in geoCSV for the user.   

**For advanced users:** we expect the user to download the full SCEC CGM HDF5 file and parse their own useful features with some guidance and reading tools from SCEC. 


### SUGGESTED HDF5 STRUCTURE 

The current HDF5 structure is envisioned as follows: 
```bash
SCEC_CGM_InSAR.hdf5
    └── Track_D071
        ├── Reference
        │   ├── Look_Vectors
        │   │   ├── unit_east_ll_grd
        │   │   ├── unit_north_ll_grd
        │   │   └── unit_up_ll_grd
        │   ├── contributors_txt
        │   ├── more_information_txt
        │   ├── polygon_boundaries_txt
        │   ├── production_date_txt
        │   └── refpixel_txt
        ├── Time_Series
        │   ├── Time_Array
        │   │   └── dates_txt
        │   ├── Time_Steps
        │   │   ├── SCEC_CGM_20150327_ll_grd
        │   │   ├── SCEC_CGM_20150421_ll_grd
        │   │   └── SCEC_CGM_20150515_ll_grd
        │   │   └── ....
        │   └── Uncertainties
        │       └── something_here?
        └── Velocities
            ├── Uncertainty
            │   └── velo_unc_grd
            └── Velocities
                ├── velocities_grd
                └── velocities_png
```

### NECESSARY TOOLS
To implement the HDF5 file format, the CGM team must create:
1. A tool to extract a certain pixel's time series from the HDF5 and convert it into a geoCSV. 
2. Several example functions to read the full SCEC HDF5 file into a practical data structure, as an advanced user would do, in several commonly used programming languages (Python, Matlab, others?).
3. Function(s) to construct the SCEC CGM HDF5 from the CGM analysis [for internal use only].
4. Detailed documentation of the CGM product.

