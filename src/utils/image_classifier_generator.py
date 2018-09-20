import glob
import random

from numpy.random import uniform
from numpy.random import randint

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


class ImageClassifierGenerator():
    def __init__(self, data, save_path,
                 num_images_per_class=100,
                 resolution=(500, 500), resolution_percentage=100,
                 background='plain', background_images_directory=None,
                 lamp_type='POINT', max_num_lamps=4,
                 lamp_location_range=[-15, 15], lamp_energy_range=[1, 5],
                 rotation_range=[0, 360],
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

        self.data = data
        self.blender_save_path = '../data/cache/current_scene.blend'
        self.save_path = save_path
        self.resolution = resolution
        self.resolution_percentage = resolution_percentage
        self.num_images_per_class = num_images_per_class
        self.background = background
        self.lamp_type = lamp_type
        self.max_num_lamps = max_num_lamps
        self.lamp_location_range = lamp_location_range
        self.lamp_energy_range = lamp_energy_range
        self.rotation_range = rotation_range
        self.translation_range = translation_range
        self.zoom_range = zoom_range

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
        for class_name, model_path in self.data.items():
            print(class_name, model_path)
            for num_images_rendered in range(self.num_images_per_class):
                obj = self.construct_scene(model_path, class_name)
                box_coordinates = get_image_bounding_box(obj)
                image_name = self.make_image_name(
                        class_name, num_images_rendered, box_coordinates)
                render_image(image_name)
                delete_scene(self.blender_save_path)

    def make_image_name(self, class_name, arg, box_coordinates):
        """ construct the image name using the given labels
        args:
            class_name: str containing the class name
            arg: int for differentiating between images of the same class
            box_coordinates: list of float coordinates
        returns:
            image_name: str with the complete (full path) image name
        """
        base_name = (self.save_path + class_name + '/' +
                     class_name + '_' + str(arg) + '_')
        box_coordinates = ['{:.3f}'.format(x) for x in box_coordinates]
        box_coordinates = '_'.join(box_coordinates)
        image_name = base_name + box_coordinates
        return image_name

    def construct_scene(self, filepath, class_name):
        """ constructs blender scene with the object in the file path given
        args:
            filepath: file path containing the .obj file
            class_name: the class name to name it inside blender
        returns:
            obj: blender object file
        """

        obj = load_obj(filepath, class_name)

        change_light_conditions(self.max_num_lamps, self.lamp_location_range,
                                self.lamp_energy_range, self.lamp_type)

        if self.rotation_range is not None:
            rotation = uniform(*self.rotation_range, size=3)
            rotate_object(obj, rotation.tolist())

        view_selected_object()

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
