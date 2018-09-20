import sys
import os
beauvoir_path = os.path.dirname(os.path.realpath(__file__)) + '/'
sys.path.append(beauvoir_path)
sys.path.append('/usr/local/lib/python3.5/dist-packages/')
from utils.ycb_data_manager import YCBVideoDataManager

num_images_per_class = 5
resolution = (128, 128)
background = 'plain'
max_num_lamps = 3
zoom_range = [-.3, .3]
translation_range = [-.1, .1]

data_path, class_names = '../data/models/', 'all'
save_path = '../data/crop_data/128x128/'
background_path = '../data/backgrounds/'
data_manager = YCBVideoDataManager(data_path, class_names)
data = data_manager.load_data()
