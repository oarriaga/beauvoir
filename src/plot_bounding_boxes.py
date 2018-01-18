from utils.xml_utils import XMLParser
import matplotlib.pyplot as plt
import numpy as np
import cv2


FONT = cv2.FONT_HERSHEY_SIMPLEX


def denormalize_box(box_coordinates, image_shape):
    height, width = image_shape
    x_min = int(box_coordinates[0] * width)
    y_min = int(height - int(box_coordinates[1] * height))
    x_max = int(box_coordinates[2] * width)
    y_max = int(height - int(box_coordinates[3] * height))
    return (x_min, y_min, x_max, y_max)


def get_colors(num_colors=21):
    return plt.cm.hsv(np.linspace(0, 1, num_colors)) * 255


def plot_box_data(box_data, original_image_array,
                  arg_to_class=None, class_arg=None, colors=None, font=FONT):

    np.apply_along_axis(plot_single_box_data, 1, box_data,
                        original_image_array, arg_to_class, class_arg,
                        colors, font)


def plot_single_box_data(box_data, original_image_array, arg_to_class=None,
                         class_arg=None, colors=None, font=FONT):

    image_shape = original_image_array.shape[0:2]
    class_scores = box_data[4:]
    class_arg = np.argmax(class_scores)
    class_score = class_scores[class_arg]
    coordinates = box_data[:4]
    color = colors[class_arg]
    class_name = arg_to_class[class_arg]
    display_text = '{:0.2f}, {}'.format(class_score, class_name)
    x_min, y_min, x_max, y_max = denormalize_box(coordinates, image_shape)
    cv2.putText(original_image_array, display_text, (x_min, y_min - 10),
                font, .25, color, 1, cv2.LINE_AA)
    thickness = 1
    cv2.rectangle(original_image_array, (x_min, y_min),
                  (x_max, y_max), color, thickness)


dataset_path = '../data/detection_data/'
xml_parser = XMLParser(dataset_path)
arg_to_class = xml_parser.arg_to_class
data = xml_parser.load_data()
path, box_data = list(data.items())[0]
image_array = cv2.imread(path)
colors = get_colors(55)
plot_box_data(box_data, image_array, arg_to_class, colors=colors)
plt.imshow(image_array)
plt.show()
