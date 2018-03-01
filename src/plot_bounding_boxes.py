from utils.xml_utils import XMLParser
import matplotlib.pyplot as plt
import numpy as np
import cv2


FONT = cv2.FONT_HERSHEY_SIMPLEX


def SaveFigureAsImage(fileName, fig=None, **kwargs):
    fig_size = fig.get_size_inches()
    w, h = fig_size[0], fig_size[1]
    fig.patch.set_alpha(0)
    if kwargs in 'orig_size':
        w, h = kwargs['orig_size']
        w2 = fig_size[0]
        fig.set_size_inches([(w2/w)*w, (w2/w)*h])
        fig.set_dpi((w2/w)*fig.get_dpi())
    a = fig.gca()
    a.set_frame_on(False)
    a.set_xticks([])
    a.set_yticks([])
    plt.axis('off')
    plt.xlim(0, h)
    plt.ylim(w, 0)
    fig.savefig(fileName, transparent=True, bbox_inches='tight',
                pad_inches=0)


def denormalize_box(box_coordinates, image_shape):
    h, w = image_shape
    x_min = int(box_coordinates[0] * w)
    y_min = int(box_coordinates[1] * h)
    x_max = int(box_coordinates[2] * w)
    y_max = int(box_coordinates[3] * h)

    x_min = np.clip(x_min, 1, w - 1)
    y_min = np.clip(y_min, 1, h - 1)
    x_max = np.clip(x_max, 1, w - 1)
    y_max = np.clip(y_max, 1, h - 1)

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
    # print('y_min', y_min)
    # print('y_max', y_max)
    cv2.rectangle(original_image_array, (x_min, y_max),
                  (x_max, y_min), color, thickness)


num_images = 100
dataset_path = '../data/detection_data/'
xml_parser = XMLParser(dataset_path)
arg_to_class = xml_parser.arg_to_class
data = xml_parser.load_data()
for image_arg in range(num_images):
    path, box_data = list(data.items())[image_arg]
    image_array = cv2.imread(path)
    image_array = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
    colors = get_colors(55)
    plot_box_data(box_data, image_array, arg_to_class, colors=colors)
    plt.axis('off')
    image_name = 'gt/ground_truths_' + str(image_arg)
    plt.imshow(image_array)
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
    # plt.show()
    plt.savefig(image_name, bbox_inches='tight')
    # SaveFigureAsImage(image_name, plt.gca())
