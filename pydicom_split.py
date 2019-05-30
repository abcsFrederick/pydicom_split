#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import copy
import math
import os
import sys
import warnings

import numpy

import pydicom


class DICOMDirectory:
    def __init__(self, directory=None):
        self._directory = directory

    @property
    def directory(self):
        return self._directory

    @directory.setter
    def directory(self, directory):
        self._directory = directory

    def __iter__(self):
        if self._directory is None:
            self.filenames = []
        else:
            self.filenames = os.listdir(self._directory)
        return self

    def __next__(self):
        while self.filenames:
            filename = self.filenames.pop(0)
            path = os.path.join(self._directory, filename)
            try:
                dataset = pydicom.dcmread(path)
            except pydicom.errors.InvalidDicomError:
                warnings.warn('%s is not a valid DICOM file' % filename)
                continue
            if not hasattr(dataset, 'SOPInstanceUID'):
                warnings.warn('%s is not a valid DICOM file' % filename)
                continue
            return path, dataset
        raise StopIteration


class DICOMSplitter:
    def __init__(self, pixel_array=None, axis=0, n=2):
        self._pixel_array = pixel_array
        self._axis = axis
        self._n = n

    @property
    def pixel_array(self):
        return self._pixel_array

    @pixel_array.setter
    def pixel_array(self, pixel_array):
        self._pixel_array = pixel_array

    @property
    def axis(self):
        return self._axis

    @axis.setter
    def axis(self, axis):
        self._axis = axis

    @property
    def n(self):
        return self._n

    @n.setter
    def n(self, n):
        self._n = n

    def __iter__(self):
        self.index = 0
        if self._pixel_array is not None:
            size = self._pixel_array.shape[self._axis]
            self.size = int(math.floor(size/self._n))
        return self

    def __next__(self):
        if self.index == self._n:
            raise StopIteration

        index = self.index

        if self._pixel_array is None:
            self.index += 1
            return index, None, None

        start = numpy.zeros(self._pixel_array.ndim, numpy.int16)
        remainder = self._pixel_array.shape[self._axis] % self._n
        offset = max(0, index + 1 + remainder - self._n)
        if offset:
            warnings.warn('image axis %d not divisible by %d'
                          ', split %d offset 1 pixel from previous split'
                          % (self._axis, self._n, index + 1))
        start[self._axis] = index * self.size + offset
        stop = numpy.zeros(self._pixel_array.ndim, numpy.int16)
        stop[self._axis] = start[self._axis] + self.size
        indices = numpy.arange(start[self._axis], stop[self._axis])
        self.index += 1
        return index, start, numpy.take(self._pixel_array, indices, self._axis)


def affine(dataset):
    S = numpy.array(dataset.ImagePositionPatient, numpy.float64)
    F = numpy.array([dataset.ImageOrientationPatient[3:],
                     dataset.ImageOrientationPatient[:3]], numpy.float64).T
    delta_r, delta_c = map(float, dataset.PixelSpacing)
    return numpy.array([[F[0, 0]*delta_r, F[0, 1]*delta_c, 0, S[0]],
                        [F[1, 0]*delta_r, F[1, 1]*delta_c, 0, S[1]],
                        [F[2, 0]*delta_r, F[2, 1]*delta_c, 0, S[2]],
                        [0, 0, 0, 1]])


def directory_name(directory, i):
    return directory.rstrip(os.sep) + '.%d' % (i + 1)


def make_output_paths(directory, n):
    output_paths = []
    for i in range(n):
        output_path = directory_name(directory, i)
        try:
            os.mkdir(output_path)
        except FileExistsError:
            pass
        output_paths.append(output_path)
    return output_paths


def set_pixel_data(dataset, pixel_array):
    dataset.PixelData = pixel_array.tostring()
    dataset.Rows, dataset.Columns = pixel_array.shape


def split_dicom_directory(directory, axis=0, n=2,
                          update_image_position_patient=False,
                          instance_uids=None, series_descriptions=None):
    if instance_uids:
        n = len(instance_uids)
    if n is None:
        raise ValueError
    if series_descriptions and len(series_descriptions) != n:
        raise ValueError

    output_paths = make_output_paths(directory, n)

    for path, dataset in DICOMDirectory(sys.argv[1]):
        try:
            pixel_array = dataset.pixel_array
        except (TypeError, AttributeError):
            pixel_array = None
        dicom_splitter = DICOMSplitter(pixel_array, axis, n)

        for i, origin, pixel_array in dicom_splitter:
            split_dataset = copy.deepcopy(dataset)

            if pixel_array is not None:
                set_pixel_data(split_dataset, pixel_array)

                if update_image_position_patient:
                    affine_matrix = affine(dataset)
                    position = affine_matrix.dot(numpy.append(origin, [0, 1]))
                    split_dataset.ImagePositionPatient = list(position[:3])

            if instance_uids:
                split_dataset.SOPInstanceUID = instance_uids[0]
                split_dataset.SeriesInstanceUID = instance_uids[1]
            else:
                suffix = '.%s' % str(i + 1)
                split_dataset.SOPInstanceUID += suffix
                split_dataset.SeriesInstanceUID += suffix

            if series_descriptions:
                split_dataset.SeriesDescription = series_descriptions[i]

            filename = os.path.join(output_paths[i], os.path.basename(path))
            split_dataset.save_as(filename)


if __name__ == '__main__':
    import argparse

    class ParseAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            values = [value.split('/') for value in values]
            bad = ['/'.join(value) for value in values if len(value) != 2]
            if bad:
                vars(namespace).setdefault(argparse._UNRECOGNIZED_ARGS_ATTR,
                                           bad)
            setattr(namespace, self.dest, values)

    parser = argparse.ArgumentParser()
    parser.add_argument('DICOM_DIRECTORY')
    parser.add_argument('-o', '--origin', action='store_true',
                        help='origin position from offset from original'
                             ' volume, default no')
    parser.add_argument('-a', '--axis', type=int, default=1,
                        help='axis (0 for rows, 1 for columns)'
                             ', default columns')
    parser.add_argument('-d', '--descriptions', nargs='*',
                        help='set the series descriptions')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-n', type=int, help='split into N volumes')
    group.add_argument('-u', '--uids',
                       nargs='*', default=[], action=ParseAction,
                       help='split into a volume for each forward slash'
                            'separated SOP/series instance UID pair')

    args = vars(parser.parse_args())
    split_dicom_directory(args['DICOM_DIRECTORY'],
                          axis=args['axis'],
                          n=args['n'],
                          update_image_position_patient=args['origin'],
                          instance_uids=args['uids'],
                          series_descriptions=args['descriptions'])
