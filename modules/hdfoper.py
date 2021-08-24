#!/usr/bin/python

import h5py

class HDFOper(object):

    def __init__(self, filename):
        self.filename = filename
        try:
            self.hdf_handle = h5py.File(filename, 'r')           
        except BaseException as e:
            raise e

    def get_attr(self, attr_name, group_name):
        try:
            result = self.hdf_handle[group_name].attrs[attr_name][0]
        except BaseException as e:
            result = None
        return result

    def get_dataset_byindex(self, dataset_name, cn):
        return self.hdf_handle[dataset_name][cn, ...]

    def get_dataset(self, dataset_name):
        return self.hdf_handle[dataset_name]

    def closehandle(self):
        self.hdf_handle.close()