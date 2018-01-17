import os
import glob
import random

from numpy.random import uniform
from numpy.random import randint
import numpy as np

from .data_manager import load_data
from .data_manager import get_class_names

from .blender_utils import load_obj
from .blender_utils import change_light_conditions
from .blender_utils import render_image
from .blender_utils import view_selected_object
from .blender_utils import set_render_properties
from .blender_utils import rotate_object
from .blender_utils import translate_object
from .blender_utils import update_scene
from .blender_utils import delete_scene
from .blender_utils import add_plain_background
from .blender_utils import add_random_patch_background
from .blender_utils import change_color
from .blender_utils import zoom_camera
from .blender_utils import get_image_bounding_box

from .xml_utils import write_xml


class ImageDetectorGenerator():
    def __init__(self, obj_models_directory, save_path, class_names='all',
                 num_images=100, resolution=(500, 500),
                 resolution_percentage=100, background='plain',
                 background_images_directory=None,
                 lamp_type='POINT', max_num_lamps=4,
                 lamp_location_range=[-15, 15], lamp_energy_range=[1, 5],
                 rotation_range=[0, 360], max_num_objects_in_scene=3,
                 translation_range=None, zoom_range=None):

        if background not in ['plain', 'crop']:
            raise Exception("Backgrounds available are: 'plain' or 'crop'")
        if background == 'crop' and background_images_directory is None:
            raise Exception("Background 'crop' need background_images_path")

        if background == 'crop':
            self.background_image_paths = glob.glob(
                            background_images_directory + '*.png')
            if len(self.background_image_paths) == 0:
                raise Exception(
                        "There are no files with '.png' prefix in directory",
                        self.background_image_paths)

        self.blender_save_path = '../data/cache/current_scene.blend'
        self.obj_models_directory = obj_models_directory
        self.save_path = save_path
        if class_names == 'all':
            self.class_names = get_class_names(obj_models_directory)
        else:
            self.class_names = class_names
        self.resolution = resolution
        self.resolution_percentage = resolution_percentage
        self.num_images = num_images
        self.background = background
        self.lamp_type = lamp_type
        self.max_num_lamps = max_num_lamps
        self.lamp_location_range = lamp_location_range
        self.lamp_energy_range = lamp_energy_range
        self.rotation_range = rotation_range
        self.translation_range = translation_range
        self.zoom_range = zoom_range
        self.max_num_objects_in_scene = max_num_objects_in_scene

        if not os.path.exists(self.save_path + 'annotations/'):
            os.makedirs(self.save_path + 'annotations/')

    def set_render_properties(self):
        """ sets the render properties regarding resolution and resolution
        percentage.
        args:
            None
        returns:
            None
        """
        set_render_properties(self.resolution, self.resolution_percentage)

    def render(self):
        self.set_render_properties()
        path_to_class = load_data(self.obj_models_directory, self.class_names)
        data = list(path_to_class.items())
        for image_arg in range(self.num_images):
            self.set_lights()
            num_objects = random.randint(1, self.max_num_objects_in_scene)
            objects, class_names, boxes_coordinates = [], [], []
            for object_arg in range(num_objects):
                filepath, class_name = random.sample(data, 1)[0]
                obj = self.set_object(filepath, class_name)
                box_coordinates = get_image_bounding_box(obj)
                objects.append(obj)
                class_names.append(class_name)
                boxes_coordinates.append(box_coordinates)
            image_name = self.make_image_name(image_arg)
            for obj in objects:
                obj.select = True
            view_selected_object()
            render_image(image_name)
            boxes_coordinates = np.asarray(boxes_coordinates)
            write_xml(
                self.save_path + 'annotations/xml' + str(image_arg) + '.xml',
                'CLARA2017', image_name,
                (self.resolution[0], self.resolution[1], 3),
                boxes_coordinates, class_names)
            delete_scene(self.blender_save_path)

    def make_image_name(self, image_arg, prefix='detection_data'):
        """ construct the image name using the given labels
        args:
            class_name: str containing the class name
            arg: int for differentiating between images of the same class
            box_coordinates: list of float coordinates
        returns:
            image_name: str with the complete (full path) image name
        """
        image_name = self.save_path + prefix + '/' + str(image_arg)
        return image_name

    def set_lights(self):
        change_light_conditions(self.max_num_lamps, self.lamp_location_range,
                                self.lamp_energy_range, self.lamp_type)

    def set_object(self, filepath, class_name):
        """ constructs blender scene with the object in the file path given
        args:
            filepath: file path containing the .obj file
            class_name: the class name to name it inside blender
        returns:
            obj: blender object file
        """
        obj = load_obj(filepath, class_name)

        if self.rotation_range is not None:
            rotation = uniform(*self.rotation_range, size=3)
            rotate_object(obj, rotation.tolist())

        if self.translation_range is not None:
            translation = uniform(*self.translation_range, size=3)
            translate_object(obj, translation.tolist())

        if self.zoom_range is not None:
            zoom = uniform(*self.zoom_range)
            zoom_camera(zoom)

        if self.background == 'plain':
            RGB_values = randint(0, 256, 3).tolist()
            add_plain_background(RGB_values)
        else:
            image = random.choice(self.background_image_paths)
            add_random_patch_background(image)

        change_color(obj)

        update_scene()
        return obj
