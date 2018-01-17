import os


def load_data(data_prefix, class_names=None):
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
    offsets = os.listdir(data_prefix)
    offset_to_name = get_offset_to_name()
    if class_names is None:
        class_names = list(offset_to_name.values())
    for offset in offsets:
        model_ids = os.listdir(data_prefix + offset)
        class_name = offset_to_name[offset]
        if class_name not in class_names:
            continue
        for model_id in model_ids:
            traversed_path = data_prefix + offset + '/' + model_id + '/models/'
            filenames = os.listdir(traversed_path)
            for filename in filenames:
                if '.obj' in filename:
                    path_to_class[traversed_path + filename] = class_name
    return path_to_class


def get_class_names():
    """ Helper function for obtaining all classes in the ShapetNet dataset.
    args:
        None
    returns:
        list with strings
    """
    return list(get_offset_to_name().values())


def get_offset_to_name():
    """ Function created to eliminate the dependency of NLP library (NLTK)
    to read wordnet.NOUN offsets of the ShapeNet dataset.
    args:
        None
    returns:
        offset_to_name: dictionary to map
        from wordnet nounrs to class names
    """

    offset_to_name = {'02691156': 'airplane',
                      '02747177': 'ashcan',
                      '02773838': 'bag',
                      '02801938': 'basket',
                      '02808440': 'bathtub',
                      '02818832': 'bed',
                      '02828884': 'bench',
                      '02843684': 'birdhouse',
                      '02871439': 'bookshelf',
                      '02876657': 'bottle',
                      '02880940': 'bowl',
                      '02924116': 'bus',
                      '02933112': 'cabinet',
                      '02942699': 'camera',
                      '02946921': 'can',
                      '02954340': 'cap',
                      '02958343': 'car',
                      '02992529': 'cellular_telephone',
                      '03001627': 'chair',
                      '03046257': 'clock',
                      '03085013': 'computer_keyboard',
                      '03207941': 'dishwasher',
                      '03211117': 'display',
                      '03261776': 'earphone',
                      '03325088': 'faucet',
                      '03337140': 'file',
                      '03467517': 'guitar',
                      '03513137': 'helmet',
                      '03593526': 'jar',
                      '03624134': 'knife',
                      '03636649': 'lamp',
                      '03642806': 'laptop',
                      '03691459': 'loudspeaker',
                      '03710193': 'mailbox',
                      '03759954': 'microphone',
                      '03761084': 'microwave',
                      '03790512': 'motorcycle',
                      '03797390': 'mug',
                      '03928116': 'piano',
                      '03938244': 'pillow',
                      '03948459': 'pistol',
                      '03991062': 'pot',
                      '04004475': 'printer',
                      '04074963': 'remote_control',
                      '04090263': 'rifle',
                      '04099429': 'rocket',
                      '04225987': 'skateboard',
                      '04256520': 'sofa',
                      '04330267': 'stove',
                      '04379243': 'table',
                      '04401088': 'telephone',
                      '04460130': 'tower',
                      '04468005': 'train',
                      '04530566': 'vessel',
                      '04554684': 'washer'}

    return offset_to_name
