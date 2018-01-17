import bpy
import numpy as np
from mathutils import Vector
from PIL import Image


def load_obj(filepath, obj_name='mesh'):
    """ load .obj file in blender
    args:
        filepath: str filepath to the .obj filename.
        obj_name: string for object name in blender.
    returns:
        obj_object: loaded object in blender.
    """
    bpy.ops.import_scene.obj(filepath=filepath)
    obj_object = bpy.context.selected_objects[0]
    bpy.context.scene.objects.active = obj_object
    bpy.ops.object.join()
    obj_object.name = obj_name
    location = get_object_lowest_point(obj_object)
    move_origin(location, axis='z')
    obj_object.location = (0., 0., 0.)
    return obj_object


def get_object_lowest_point(obj):
    """ returns lowest location of the object:
    args:
        obj: blender object:
    returns:
        vector: vector with x,y,z coordinates
    """
    matrix_w = obj.matrix_world
    vectors = [matrix_w * vertex.co for vertex in obj.data.vertices]
    return min(vectors, key=lambda item: item.z)


def move_origin(location, axis='z'):
    """ move object origin
    args:
        location: vector of new object position.
        axis: that you want to move (only z supported).
    returns:
        None
    """
    saved_location = bpy.context.scene.cursor_location.copy()
    if axis == 'z':
        location = saved_location.x, saved_location.y, location.z
    bpy.context.scene.cursor_location = location
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.context.scene.cursor_location = saved_location


def set_render_properties(resolution=(500, 500), resolution_percentage=100):
    """
    args:
        resolution: list of int indicating the height and width of the
        image to be rendered.
        resolution_percentage: int between [1, 100]
    returns:
        None
    """
    bpy.context.scene.render.resolution_x = resolution[0]
    bpy.context.scene.render.resolution_y = resolution[1]
    bpy.context.scene.render.resolution_percentage = resolution_percentage


def update_scene():
    """ blender needs to the be explicitly told to re-calculate world matrices
    args:
        None
    returns:
        None
    """
    bpy.context.scene.update()


def render_image(filepath, camera_name='Camera'):
    """ Render image and saves it
    args:
        filepath: string for filepath where the rendered
        image will get saves.
    returns: None
    """
    objects = bpy.data.objects
    bpy.context.scene.render.filepath = filepath
    camera = objects[camera_name]
    bpy.context.scene.camera = camera
    bpy.ops.render.render(write_still=True)


def get_camera():
    """ returns blender camera objects
    returns:
        camera blender object
    """
    return bpy.data.objects['Camera']


def zoom_camera(zoom_scale):
    """ zooms in or out depending on the 'zoom_scale'
    args:
        zoom_scale: int
    returns:
        None
    """
    camera = get_camera()
    location = np.asarray(camera.location)
    direction = camera.matrix_world.to_quaternion() * Vector((0.0, 0.0, -1.0))
    direction = np.asarray(direction)
    new_camera_location = location + (zoom_scale * direction)
    camera.location = new_camera_location.tolist()


def point_camera(camera, point=(0., 0., 0.)):
    """ point camera to 'location' looking directly at origin
    args:
        location: list of 3 representing the location to point at
        origin: list of floats that represent where the camera
        will be looking at
    returns:
        None
    """
    point = Vector(point)
    camera_location = camera.location
    direction = point - camera_location
    quaternion_rotation = direction.to_track_quat('-Z', 'Y')
    euler_rotation = quaternion_rotation.to_euler()
    camera.rotation_euler = euler_rotation


def move_camera_randomly(camera, min_radius=1, max_radius=4,
                         min_theta=15, max_theta=90):
    """ randomly moves camera to a constrained location given by
    a radius and height.1
    args:
        max_radius: float
        max_height: float
    returns:
        None
    """
    radius = np.random.uniform(min_radius, max_radius)
    theta = np.random.uniform(np.deg2rad(min_theta), np.deg2rad(max_theta))
    phi = np.random.uniform(0, 2. * np.pi)
    x = radius * np.cos(phi) * np.sin(theta)
    y = radius * np.sin(phi) * np.sin(theta)
    z = radius * np.cos(theta)
    camera.location = (x, y, z)


def delete_all_lamps():
    """ deletes all blender objects that are lamps
    args:
        None
    returns:
        None
    """
    for lamp_structure in bpy.data.lamps:
        lamp_name = lamp_structure.name
        lamp = bpy.data.objects[lamp_name]
        delete_object(lamp)


def delete_object(obj):
    """
    args:
        blender object
    returns:
        None
    """
    bpy.data.objects.remove(obj, do_unlink=True)


def change_camera_perspective(camera, min_radius=1, max_radius=3,
                              min_theta=15, max_theta=90,
                              point=(0., 0., 0.)):
    """ moves camera randomly and then points to the object
    args:
        camera: bpy camera object
        min_radius: float. Minimum camera radius
        max_radius: float. Maximum camera radius
        min_theta: float. Minimum theta angle for
        spherical coordinates in degrees.
        max_theta: float. Maximum theta angle for
        spherical coordinates in degrees.
    returns:
        None
    """
    move_camera_randomly(camera, min_radius, max_radius, min_theta, max_theta)
    point_camera(camera, point)


def add_plane(radius=10, location=(0, 0, 0)):
    """ adds a plane to scene
    args:
        radius: number of squares from location to side
        location: origin of the plane
    returns:
        None
    """
    bpy.ops.mesh.primitive_plane_add(radius=radius, location=location)


def change_focal_length(focal_length=45, camera_name='Camera'):
    """ changes focal length of camera
    args:
        camera: string with the camera name
        focal_length: float
    returns:
        None
    """
    bpy.data.cameras[camera_name].lens = focal_length


def view_selected_object():
    """ points the camera towards the object
    args:
        None
    returns:
        None
    """
    bpy.ops.view3d.camera_to_view_selected()


def add_image_background(filepath):
    """ adds image background to the scene
    args:
        string, file path to background image
    returns:
        None
    """
    img = bpy.data.images.load(filepath)
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            space_data = area.spaces.active
            bg = space_data.background_images.new()
            bg.image = img
            space_data.show_background_images = True
            break

    texture = bpy.data.textures.new("Texture.001", 'IMAGE')
    texture.image = img
    bpy.data.worlds['World'].active_texture = texture
    bpy.context.scene.world.texture_slots[0].use_map_horizon = True


def add_plain_background(RGB, height=200, width=200):
    """ adds a plain rgb background to the scene
    args:
        RGB: list of ints containing the (R,G,B) values
    returns:
        None
    """
    image_array = np.zeros(shape=(height, width, 3))
    image_array[:, :, 0].fill(RGB[0])
    image_array[:, :, 1].fill(RGB[1])
    image_array[:, :, 2].fill(RGB[2])
    pil_image = Image.fromarray(image_array.astype('uint8'))
    pil_image.save('../data/cache/plain_background.png')
    add_image_background('../data/cache/plain_background.png')


def add_random_patch_background(image_path, box_size=200):
    """ performs a random crop on the loaded image and uses it as background
    args:
        image_path: string containing path the image
        box_size: length of random box
    returns:
        None
    """
    image = Image.open(image_path)
    height, width = image.size[0:2]
    if height <= box_size or width <= box_size:
        RGB_values = np.random.randint(0, 256, 3).tolist()
        add_plain_background(RGB_values)
        return
    x_min = np.random.randint(0, width - box_size)
    y_min = np.random.randint(0, height - box_size)
    x_max = int(x_min + box_size)
    y_max = int(y_min + box_size)
    cropped_image = image.crop((x_min, y_min, x_max, y_max))
    cropped_image.save('../data/cache/random_background.png')
    add_image_background('../data/cache/random_background.png')


def translate_object(obj, coordinates):
    """ moves object to a give location
    args:
        obj: blender object to be moved
        coordinates: list of floats containing the new location
    returns:
        None
    """
    obj.location = coordinates


def rotate_object(obj, angles):
    """ rotates obj with the angles given
    args:
        obj: blender obj to rotate
        angles: list of floats containing (X,Y,Z) angles in degrees
    returns:
        None
    """
    angles = np.deg2rad(angles).tolist()
    # obj.rotation_euler = angles
    obj.delta_rotation_euler = angles


def change_color2(obj, RGB):
    """ changes the color of a blender object
    args:
        obj: blender object
        RGB: list containing the RGB values
    returns:
        None
    """
    # active_obj = bpy.context.active_object
    material = bpy.data.materials.new(name='color_material')
    obj.data.materials.append(material)
    bpy.context.object.active_material.diffuse_color = RGB


def change_color(obj):
    """ changes the color of a blender object
    args:
        obj: blender object
    returns:
        None
    """
    for slot in obj.material_slots:
        normalized_RGB = np.random.randint(0, 255, 3) / 255.0
        slot.material.diffuse_color = normalized_RGB.tolist()


def change_light_conditions(max_num_lamps, location_range,
                            energy_range, lamp_type='POINT'):
    """ change light conditions
    args:
        max_num_lamps: maximum number of lamps in the scene
        location_range: list of two floats
        energy: list of two integers
        lamp_type: string specifying the blender lamp type
    returns:
        None
    """
    num_lamps = np.random.randint(1, max_num_lamps + 1)
    for lamp_arg in range(num_lamps):
        lamp = add_lamp('lamp_' + str(lamp_arg))
        lamp.location = np.random.uniform(*location_range, size=3).tolist()
        lamp.data.energy = np.random.randint(*energy_range)
        lamp.data.type = lamp_type


def set_light_conditions(num_lamps, locations,
                         energies, lamp_type='POINT'):
    """ set light conditions
    args:
        max_num_lamps: maximum number of lamps in the scene
        location_range: list containing lists of three floats
        energy: list containing lists of integers
        lamp_type: string specifying the blender lamp type
    returns:
        None
    """
    for lamp_arg in range(num_lamps):
        lamp = add_lamp('lamp_' + str(lamp_arg))
        lamp.location = locations[lamp_arg]
        lamp.data.energy = energies[lamp_arg]
        lamp.data.type = lamp_type


def add_lamp(name):
    """ add a new lamp to the scene
    args:
        name: string containing the name used internally by blender
        location: list of floats containing the x,y,z coordinates
        engery: integer specifying the blender enery
        lamp_type: string with a blender lamp type
    returns:
        lamp: blender object
    """
    scene = bpy.context.scene
    lamp_data = bpy.data.lamps.new(name=name, type='POINT')
    lamp = bpy.data.objects.new(name=name, object_data=lamp_data)
    scene.objects.link(lamp)
    lamp.location = (0., 0., 0.)
    return lamp


def change_lamp(lamp, location, energy=5, lamp_type='POINT'):
    """ change light conditions
    args:
        lamp: blender lamp object
        location: list of floats containing new coordinates for the lamp
        energy: int lamp blender energy
        lamp_type: string specifying the blender lamp type
    returns:
        None
    """
    # check bpy.data.lamps['Lamp']
    # lamp = bpy.data.objects['Lamp']
    lamp.location = location
    lamp.type = lamp_type
    lamp.energy = energy


def delete_scene(filename):
    # select objects by type
    for o in bpy.data.objects:
        if o.type == 'MESH' or o.type == 'LAMP':
            o.select = True
        else:
            o.select = False

    # call the operator once
    bpy.ops.object.delete()
    bpy.ops.wm.save_as_mainfile(filepath=filename)
    bpy.ops.wm.open_mainfile(filepath=filename)


def clamp(x, minimum=0., maximum=1.):
    """
    args:
        x: float
        minimum: float
        maximum: float
    returns: float between [minimum, maximum]
    """
    return max(minimum, min(x, maximum))


def get_image_bounding_box(obj):
    """ projects all vertices from the blender obj
    into the image coordinates to obtain a bounding box
    args:
        obj: blender object
    returns: a list of floats containing the bounding box
    coordinates: [x_min, y_min, x_max, y_max]
    """
    scene = bpy.context.scene
    camera = bpy.data.objects['Camera']
    x_image_projections = []
    y_image_projections = []
    for obj_vertix in obj.data.vertices:
        vertix = obj.matrix_world * obj_vertix.co
        normalized_image_corner = to_camera_view(scene, camera, vertix)
        x_image_projections.append(normalized_image_corner.x)
        y_image_projections.append(normalized_image_corner.y)

    x_image_projections = np.asarray(x_image_projections)
    y_image_projections = np.asarray(y_image_projections)

    x_min = np.min(x_image_projections)
    x_max = np.max(x_image_projections)

    y_min = np.min(y_image_projections)
    y_max = np.max(y_image_projections)

    coordinates = (x_min, y_min, x_max, y_max)
    coordinates = [clamp(coordinate) for coordinate in coordinates]
    return coordinates


def to_camera_view(scene, obj, coord):
    """ projects 3D coord into the image coordinates of the camera obj
    args:
        scene: blender scene
        obj: camera blender object
        coord: 3D coordinates in blender vector form
    returns:
        3D vector in image coordiantes.
    """
    co_local = obj.matrix_world.normalized().inverted() * coord
    z = -co_local.z

    camera = obj.data
    frame = [-v for v in camera.view_frame(scene=scene)[:3]]
    if camera.type != 'ORTHO':
        if z == 0.0:
            return Vector((0.5, 0.5, 0.0))
        else:
            frame = [(v / (v.z / z)) for v in frame]

    min_x, max_x = frame[1].x, frame[2].x
    min_y, max_y = frame[0].y, frame[1].y

    x = (co_local.x - min_x) / (max_x - min_x)
    y = (co_local.y - min_y) / (max_y - min_y)

    return Vector((x, y, z))
