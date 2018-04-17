#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import glob
import os
#import time

import numpy

import pydicom


def affine(image_position_patient, image_orientation_patient, pixel_spacing):
    S = numpy.array(image_position_patient)
    F = numpy.array([image_orientation_patient[3:],
                     image_orientation_patient[:3]]).T
    delta_r, delta_c = pixel_spacing

    A = numpy.array([[F[0, 0]*delta_r, F[0, 1]*delta_c, 0, S[0]],
                     [F[1, 0]*delta_r, F[1, 1]*delta_c, 0, S[1]],
                     [F[2, 0]*delta_r, F[2, 1]*delta_c, 0, S[2]],
                     [              0,               0, 0,    1]])
    return A


def crop_data(ds, data, start, size):
    cropped = data[start[0]:start[0] + size[0],
                   start[1]:start[1] + size[1]]
    ds.PixelData = cropped.tostring()
    ds.Rows, ds.Columns = cropped.shape


def split_data(ds, data, axis, size, i, image_position_patient,
               image_orientation_patient, pixel_spacing):
    start = [0]*len(data.shape)
    start[axis] = i*size[axis]

    crop_data(ds, data, start, size)

    # update image position (patient)
    A = affine(image_position_patient, image_orientation_patient, pixel_spacing)
    position = A.dot(start + [0, 1])
    ds.ImagePositionPatient = list(position[:3])


def split_dicom_file(filename, axis, output_paths):
    ds = pydicom.dcmread(filename)
    n = len(output_paths)

    sop_instance_uid = ds.SOPInstanceUID
    series_instance_uid = ds.SeriesInstanceUID

    try:
        pixel_spacing = list(map(float, ds.PixelSpacing))
        image_position_patient = list(map(float, ds.ImagePositionPatient))
        image_orientation_patient = list(map(float, ds.ImageOrientationPatient))
    except AttributeError:
        pixel_spacing = None
        image_position_patient = None
        image_orientation_patient = None

    #series_description = ds.SeriesDescription

    try:
        data = ds.pixel_array
        size = list(data.shape)
        size[axis] = int(size[axis]/n)
    except TypeError:
        data = None
        size = None

    for i, output_path in enumerate(output_paths):
        ds.SeriesInstanceUID = '%s.%d' % (series_instance_uid, i + 1)
        ds.SOPInstanceUID = '%s.%d' % (sop_instance_uid, i + 1)

        #ds.SeriesDate = modification_date
        #ds.SeriesTime = modification_time
        #ds.ImageType = ['DERIVED', 'SECONDARY']
        #ds.SeriesDescription = \
        #    '%s (split, %d of %d)' % (series_description, i + 1, n)

        #ds.Manufacturer (???)
        #ds.ManufacturerModelName (???)
        #ds.DerivationDescription (not set)
        #ds.SourceImageSequence (not set)

        if data is not None:
            split_data(ds, data, axis, size, i, image_position_patient,
                       image_orientation_patient, pixel_spacing)

        ds.save_as(os.path.join(output_path, os.path.basename(filename)))


def directory_name(directory, i):
    directory = directory.rstrip(os.sep)
    return directory + '.%d' % (i + 1)


def split_dicom_directory(directory, axis, n):
    output_paths = [directory_name(directory, i) for i in range(n)]
    for output_path in output_paths:
        try:
            os.mkdir(output_path)
        except FileExistsError:
            pass

    #modification_date = time.strftime('%Y%m%d')
    #modification_time = time.strftime('%H%M%S')

    for filename in glob.glob(os.path.join(directory, '*.dcm')):
        split_dicom_file(filename, axis, output_paths)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('DICOM_directory')
    parser.add_argument('axis', type=int,
                        help='axis (0 for rows, 1 for columns)')
    parser.add_argument('N', type=int, help='split into N volumes')

    args = parser.parse_args()

    split_dicom_directory(args.DICOM_directory, args.axis, args.N)
