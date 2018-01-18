import os
import glob
from xml.dom import minidom
import xml.etree.ElementTree as ET

import numpy as np

from .data_manager import get_class_names


def prettify(elem, doctype=None):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    if doctype is not None:
        reparsed.insertBefore(doctype, reparsed.documentElement)
    return reparsed.toprettyxml(indent="    ")


def write_xml(xml_pathname, folder_name, file_name,
              img_shape, coordinates, names):
    root = ET.Element('annotation')

    folder = ET.SubElement(root, 'folder')
    folder.text = folder_name

    filename = ET.SubElement(root, 'filename')
    filename.text = file_name

    size = ET.SubElement(root, 'size')
    width = ET.SubElement(size, 'width')
    width.text = str(img_shape[0])

    height = ET.SubElement(size, 'height')
    height.text = str(img_shape[1])

    depth = ET.SubElement(size, 'depth')
    depth.text = str(img_shape[2])

    for object_arg in range(len(coordinates)):
        obj = ET.SubElement(root, 'object')

        obj_class_name = names[object_arg]
        name = ET.SubElement(obj, 'name')
        name.text = obj_class_name

        difficulty = ET.SubElement(obj, 'difficult')
        difficulty.text = str(0)

        obj_coordinates = coordinates[object_arg]
        bndbox = ET.SubElement(obj, 'bndbox')

        x_min = ET.SubElement(bndbox, 'xmin')
        x_min.text = str(obj_coordinates[0])

        y_min = ET.SubElement(bndbox, 'ymin')
        y_min.text = str(obj_coordinates[1])

        x_max = ET.SubElement(bndbox, 'xmax')
        x_max.text = str(obj_coordinates[2])

        y_max = ET.SubElement(bndbox, 'ymax')
        y_max.text = str(obj_coordinates[3])

    pretty_root = prettify(root)
    text_file = open(xml_pathname, 'w')
    text_file.write(pretty_root)
    text_file.close()


class XMLParser(object):
    """xml annotations parser.

    # Arguments
        data_path: Data path to detection dataset. By default the
        detection dataset contains two directories 'annotations'
        and 'images'.

    # Return
        data: Dictionary which keys correspond to the image names
        and values are numpy arrays of shape (num_objects, 4 + num_classes)
        num_objects refers to the number of objects in that specific image
    """

    def __init__(self, dataset_path, class_names='all'):

        self.dataset_path = dataset_path
        self.annotations_path = self.dataset_path + 'annotations/'
        if not os.path.exists(self.annotations_path):
            raise Exception(
                "'annotations' directory not found inside", self.dataset_path)

        self.images_path = self.dataset_path + 'images/'
        if not os.path.exists(self.images_path):
            raise Exception(
                "'images' directory not found inside", self.dataset_path)

        self.class_names = class_names
        if self.class_names == 'all':
            self.class_names = get_class_names()
        self.num_classes = len(self.class_names)
        class_keys = np.arange(self.num_classes)
        self.arg_to_class = dict(zip(class_keys, self.class_names))
        self.class_to_arg = {value: key for key, value
                             in self.arg_to_class.items()}

    def load_data(self):
        data = dict()
        filenames = glob.glob(self.annotations_path + '*.xml')
        for filename_path in filenames:
            tree = ET.parse(filename_path)
            root = tree.getroot()
            bounding_boxes = []
            one_hot_classes = []
            for object_tree in root.findall('object'):
                class_name = object_tree.find('name').text
                if class_name in self.class_names:
                    one_hot_class = self._to_one_hot(class_name)
                    one_hot_classes.append(one_hot_class)
                    for bounding_box in object_tree.iter('bndbox'):
                        xmin = float(bounding_box.find('xmin').text)
                        ymin = float(bounding_box.find('ymin').text)
                        xmax = float(bounding_box.find('xmax').text)
                        ymax = float(bounding_box.find('ymax').text)
                    bounding_box = [xmin, ymin, xmax, ymax]
                    bounding_boxes.append(bounding_box)
            if len(one_hot_classes) == 0:
                continue
            image_name = root.find('filename').text
            bounding_boxes = np.asarray(bounding_boxes)
            one_hot_classes = np.asarray(one_hot_classes)
            image_data = np.hstack((bounding_boxes, one_hot_classes))
            if len(bounding_boxes.shape) == 1:
                image_data = np.expand_dims(image_data, axis=0)
            data[image_name + '.png'] = image_data
        return data

    def _to_one_hot(self, class_name):
        one_hot_vector = [0] * self.num_classes
        class_arg = self.class_to_arg[class_name]
        one_hot_vector[class_arg] = 1
        return one_hot_vector
