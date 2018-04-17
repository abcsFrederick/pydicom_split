# pydicom_split

pydicom_split is a simple script than splits the DICOM into a specified number of volumes along the specified axis into equal sized volumes without resampling. The series and SOP instance UIDs are updated with an appended period and integer for the split number. The image position (patient) is updated as necessary. Each split volume is saved in the same parent directory as the parent volume, in a directory with an appended period and integer for the split number. The script currently works for DICOM directories only.

```
usage: pydicom_split.py [-h] DICOM_directory axis N

positional arguments:
  DICOM_directory
  axis             axis (0 for rows, 1 for columns)
  N                split into N volumes

optional arguments:
  -h, --help       show this help message and exit
```
