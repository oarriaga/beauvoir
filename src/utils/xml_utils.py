import xml.etree.ElementTree as ET
import numpy as np
from xml.dom import minidom


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
    # print(pretty_root)
    # tree = ET.ElementTree(pretty_root)
    # tree.write(xml_pathname)


# cords = np.array([[2, 3, 4, 5], [6, 6, 7, 7]])
# names = ['horse', 'television']
# write_xml('xml_example.xml', 'CLARA2017', '00001.jpg',
#  (256, 256, 3), cords, names)
