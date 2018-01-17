import sys
import os
beauvoir_path = os.path.dirname(os.path.realpath(__file__)) + '/'
sys.path.append(beauvoir_path)
sys.path.append('/usr/local/lib/python3.5/dist-packages/')
from utils import ImageDetectorGenerator

obj_model_directory = '../data/ShapeNetCore.v2/'
save_path = '../data/detection_data/'
background_path = '../data/backgrounds/'
class_names = ['airplane', 'bench', 'bottle', 'bus', 'camera', 'can', 'car',
               'cellular_telephone', 'chair', 'computer_keyboard', 'display',
               'earphone', 'faucet', 'guitar', 'knife', 'laptop', 'motorcycle',
               'mug', 'pillow', 'pistol', 'rifle', 'rocket', 'skateboard',
               'table']

num_images = 50
resolution = (128, 128)
background = 'plain'
max_num_lamps = 3
zoom_range = [-.3, .3]
translation_range = [-1.5, 1.5]
max_num_objects_in_scene = 6

image_generator = ImageDetectorGenerator(
                        obj_model_directory, save_path,
                        class_names, num_images,
                        resolution, background=background,
                        background_images_directory=background_path,
                        max_num_lamps=max_num_lamps,
                        zoom_range=zoom_range,
                        translation_range=translation_range,
                        max_num_objects_in_scene=max_num_objects_in_scene)

image_generator.render()
