# pydicom_split

### 1. Description

pydicom_split is a simple script than splits the DICOM into a specified number of volumes along the specified axis into equal sized volumes without resampling. The series and SOP instance UIDs are updated with an appended period and integer for the split number. The image position (patient) is updated as necessary. Each split volume is saved in the same parent directory as the parent volume, in a directory with an appended period and integer for the split number. The script currently works for DICOM directories only.

### 2. Usage: 
```
pydicom_split.py [-h] [-o] [-a AXIS]
                        [-d [DESCRIPTIONS [DESCRIPTIONS ...]]]
                        (-n N | -u [UIDS [UIDS ...]])
                        DICOM_DIRECTORY

positional arguments:
  DICOM_DIRECTORY

optional arguments:
  -h, --help            show this help message and exit
  -o, --origin          origin position from offset from original volume,
                        default no
  -a AXIS, --axis AXIS  axis (0 for rows, 1 for columns), default columns
  -d [DESCRIPTIONS [DESCRIPTIONS ...]], --descriptions [DESCRIPTIONS [DESCRIPTIONS ...]]
                        set the series descriptions
  -u [UIDS [UIDS ...]], --uids [UIDS [UIDS ...]]
                        split into a volume for each forward slashseparated
                        SOP/series instance UID pair
  -Outdir output, --output_dir 
                        Output directory to save split result
For single column or single row dataset
  -n N                  split into N volumes
  -order order          if there is an empty volumn in dataset,
                        specify volume(s) need to be split (1,1,1 means split 
                        all three columns mice, 1,0,1 means middle volumn is empty)
For multiple column or double row dataset
  -nTB N1,N2            split top row into N1 volumes, and bottom row into N2 
                        volumes
  -orderT orderT        if there is an empty volumn in the top row of dataset,
                        specify volume(s) need to be split (1,1 means split 
                        top row into two columns mice, 1,0 means skip the right mice of top row)
  -orderB orderB        if there is an empty volumn in the bottom row of  dataset,
                        specify volume(s) need to be split (1,1 means split 
                        bottom row into two columns mice, 1,0 means skip the right mice of bottom row)
```

### 3. Run
If you want split all three column volume.
<img align="left" width="100" height="100" src="test/SingleRow/thmb_1.3.46.670589.11.17169.5.0.3060.2019082909190671216.jpg">
```
  python pydicom_split.py test/SingleRow/ -n 3 -order 1,1,1 -Outdir ./output
```
If you want remove right column empty volume.
<img align="left" width="100" height="100" src="test/SingRowLastOneEmpty/thmb_1.3.46.670589.11.17169.5.0.7912.2019101010042925516.jpg">
```
  python pydicom_split.py test/SingRowLastOneEmpty/ -n 3 -order 1,1,0 -Outdir ./output

```
If you want split two row volume.
<img align="left" width="100" height="100" src="test/TwoRows/thmb_1.3.6.1.4.1.12842.1.1.14.4.20200910.100022.319.463497616.jpg">
```
  python pydicom_split.py test/TwoRows/ -nTB 1,2 -orderT 1 -orderB 1,1 -Outdir ./output

```
### 4. Web interface
NCI ABCS IVG provides girder based dicom split workflow interface for user to quick and easy visualize and utilize this script, contact IVG group for more informations.
<img align="left" src="test/webInterface.png"> 
