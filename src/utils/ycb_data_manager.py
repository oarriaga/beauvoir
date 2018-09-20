import os
from glob import glob

YCB_DATA_PATH = '../data/models/'


class YCBVideoDataManager(object):

    def __init__(self, data_path=YCB_DATA_PATH, class_names='all'):
        self.data_path = data_path
        self.class_names = class_names
        if self.class_names == 'all':
            self.class_names = self.get_class_names()

    def load_data(self):
        """ Makes a dictionary containing the data samples paths as keys
        and their corresponding class as values.
        args:
            data_prefix: string data prefix containing all offsets
            and each offset contains several models.
            class_names: List of strings containing the class names
            which will be loaded. If values is None it will load all.
        returns:
            path_to_class: dictionary that maps paths to classes.
        """
        path_to_class = dict()
        for class_name in self.class_names:
            class_path = os.path.join(self.data_path, class_name)
            obj_path = class_path + '/textured.obj'
            mtl_path = class_path + '/textured.mtl'
            # path_to_class[class_name] = [obj_path, mtl_path]
            path_to_class[class_name] = obj_path
        return path_to_class

    def get_class_names(self):
        """ Helper function for obtaining all classes in the YCB_Video dataset.
        args:
            string containing the path the YCB models
        returns:
            list with strings
        """
        class_names = glob(self.data_path + '*')
        class_names = sorted([os.path.basename(name) for name in class_names])
        # class_names = ['_'.join(name.split('_')[1:]) for name in class_names]
        return class_names
