import os

import numpy
import pytest
import pydicom
from pydicom.data import get_testdata_files

import pydicom_split

@pytest.fixture
def directory_testdata_files():
    testdata_files = get_testdata_files('MR700')
    yield set(map(os.path.dirname, testdata_files)).pop(), testdata_files

@pytest.fixture
def dataset():
    yield pydicom.Dataset()

@pytest.fixture
def pixel_array():
    yield numpy.zeros((3, 3), numpy.uint16)

@pytest.fixture
def pixel_arrays():
    n = 3
    yield [numpy.zeros((3, 3)) + i for i in range(n)]

@pytest.fixture
def affine_dataset(dataset):
    dataset.ImagePositionPatient = [0, 0, 0]
    dataset.ImageOrientationPatient = [0, 1, 0, 1, 0, 0]
    dataset.PixelSpacing = [1, 1]
    yield dataset

@pytest.fixture
def file_dataset(tmpdir):
    dicom_file = tmpdir.join('test.dcm')
    file_meta = pydicom.Dataset()
    file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.2'
    file_meta.MediaStorageSOPInstanceUID = "1.2.3"
    file_meta.ImplementationClassUID = "1.2.3.4"
    dataset = pydicom.FileDataset(dicom_file, {}, file_meta=file_meta)
    dataset.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
    dataset.is_little_endian = True
    dataset.is_implicit_VR = True
    dataset.PixelRepresentation = 0
    dataset.BitsAllocated = 16
    dataset.SamplesPerPixel = 0
    yield dataset

def testDICOMDirectory(directory_testdata_files):
    directory, filenames = directory_testdata_files
    dicom_directory = pydicom_split.DICOMDirectory(directory)
    assert directory == dicom_directory.directory
    assert [path for path, _ in dicom_directory] == filenames

def testDICOMSplitter(pixel_arrays):
    axis = 0
    pixel_arrays = list(pixel_arrays)
    n = len(pixel_arrays)
    pixel_array = numpy.concatenate(pixel_arrays, axis=axis)
    dicom_splitter = pydicom_split.DICOMSplitter(pixel_array, axis=axis, n=n)
    for index, start, array in dicom_splitter:
        assert array.shape == pixel_arrays[index].shape

def testAffine(affine_dataset):
    affine_matrix = pydicom_split.affine(affine_dataset)
    vector = numpy.array([4, 2, 0, 1], affine_matrix.dtype)
    position = affine_matrix.dot(vector)
    numpy.testing.assert_array_equal(position, vector)

def testMakeOutputPaths(tmpdir):
    directory = tmpdir.mkdir('test_directory').strpath
    n = 5
    for output_path in pydicom_split.make_output_paths(directory, n):
        assert os.path.exists(output_path)
        assert os.path.isdir(output_path)

def testSetPixelData(file_dataset, pixel_array):
    pydicom_split.set_pixel_data(file_dataset, pixel_array)
    numpy.testing.assert_array_equal(file_dataset.pixel_array, pixel_array)
    assert file_dataset.Rows == pixel_array.shape[0]
    assert file_dataset.Columns == pixel_array.shape[1]
