# pydicom_split

pydicom_split is a simple script than splits the DICOM into a specified number of volumes along the specified axis into equal sized volumes without resampling. The series and SOP instance UIDs are updated with an appended period and integer for the split number. The image position (patient) is updated as necessary. Each split volume is saved in the same parent directory as the parent volume, in a directory with an appended period and integer for the split number. The script currently works for DICOM directories only.

```
usage: pydicom_split.py [-h] [-o] [-a AXIS]
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
  -n N                  split into N volumes
  -u [UIDS [UIDS ...]], --uids [UIDS [UIDS ...]]
                        split into a volume for each forward slashseparated
                        SOP/series instance UID pair
```
