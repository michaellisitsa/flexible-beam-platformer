import pygame
from anastruct import SystemElements  # pyright: reportMissingTypeStubs=false
from anastruct import Vertex
import pint
import numpy as np
from scipy import ndimage

from src.PlatformTile import PlatformTile
from src.assets.tile_map import tile_map
from src.Player import Player

u = pint.UnitRegistry()


def get_deflection(location: float):
    """
    Extract the deflections and element locations as a nested list along the beam in a matrix.
    By default the post processing deflections do not list their locations.
    TODO: what is the object here? an element. An element has a deflection array. But what does a deflection mean?
    A deflection is an object that has a relationship to an element, and a position along that element.
    It might also have a factored position on an element, or a distance from either end.
    A deflection may belong to an ElementDeflections class, whose responsibility is to keep track of all the deflections,
    as well as have methods to return a dictionary of local (or global) positions and respective deflections.
    Another method might be to return a flattened array of global positions and respective deflections going from left-to-right or visa versa.

    Alternative way to think is about a proxy pattern.
    The element_map already exists with all its deflections. We just want to
    """

    # Set up external dimensions of structure
    # Maintain a reasonable internal dimension for members.
    # These will be transformed to pixel coordinates in pygame.
    # To avoid losing reference to the material and section constants
    # that define the deflection.
    # may also allow expanding to a structural engineer's visualisation tool in future.
    start_beam_loc = 0 * u.meter
    end_beam_loc = 2000 * u.mm
    start_vertex = Vertex(start_beam_loc.to_base_units().magnitude, 0)
    end_vertex = Vertex(end_beam_loc.to_base_units().magnitude, 0)

    # Create a 50x50x1.6 G350 SHS
    I_shs = 117000 * u.mm**4
    E_steel = 200e3 * u.N / u.mm**2
    A_shs = 303 * u.mm**2

    # Number of elements for post-processing
    mesh = 10
    ss = SystemElements(
        mesh=mesh,
        EI=I_shs.to_base_units().magnitude * E_steel.to_base_units().magnitude,
        EA=E_steel.to_base_units().magnitude * A_shs.to_base_units().magnitude,
    )

    """
    Set up location of point load and add cantilever
    Ideally cantilever should be defined before
    """

    # Heavy man at location
    # Point loads need a node to be created first.
    intermediate_loc = location * u.mm
    intermediate_vertex = Vertex(intermediate_loc.to_base_units().magnitude, 0)

    # Add a cantilever
    cant_beam_loc = 3000 * u.mm
    cant_vertex = Vertex(cant_beam_loc.to_base_units().magnitude, 0)

    """Redefine all geometry to include the extra node"""
    if intermediate_vertex.x < end_vertex.x:
        ss.add_element(location=(start_vertex, intermediate_vertex))
        ss.add_element(location=(intermediate_vertex, end_vertex))

        ss.add_element(location=(end_vertex, cant_vertex))

        intermediate_node = ss.find_node_id(intermediate_vertex)
    elif intermediate_vertex.x > end_vertex.x:
        ss.add_element(location=(start_vertex, end_vertex))
        ss.add_element(location=(end_vertex, intermediate_vertex))
        ss.add_element(location=(intermediate_vertex, cant_vertex))
        intermediate_node = ss.find_node_id(intermediate_vertex)
    else:
        return None

    """Assign a point load to the extra node"""
    man = 100 * u.kg * 9.81 * u.N / u.kg

    ss.point_load(node_id=intermediate_node, Fy=man.to_base_units().magnitude)

    # Get the assigned nodes and assign supports
    start_node = ss.find_node_id(start_vertex)
    end_node = ss.find_node_id(end_vertex)
    cant_node = ss.find_node_id(cant_vertex)

    if start_node and end_node:
        ss.add_support_hinged(node_id=start_node)
        ss.add_support_roll(node_id=end_node)

    ss.solve()

    # Use internal plotting method
    deflections = ss.plot_values.displacements(factor=1000, linear=False)
    deflections_transposed = np.transpose(np.array(deflections)).tolist()

    for deflection in deflections_transposed:
        deflection[0] = 80 + deflection[0] * 60
        deflection[1] = 100 + deflection[1]
    return deflections_transposed


pygame.init()
font = pygame.font.SysFont(None, 24)


def update_fps():
    fps = str(int(clock.get_fps()))
    fps_text = font.render(fps, 1, pygame.Color("coral"))
    return fps_text


display_surface = pygame.display.set_mode([960, 640])

# Set FPS and clock
FPS = 60
clock = pygame.time.Clock()

man_location = 500

# Create player group and object
my_player_group = pygame.sprite.Group()  # type: ignore


# Create sprite groups
main_tile_group = pygame.sprite.Group()  # type: ignore
# platform_tile_group = pygame.sprite.Group()

# Create individual tile objects from the tile map
# Loop through the 20 lists in tile_map (i moves down the map)
for i in range(len(tile_map)):
    for j in range(len(tile_map[i])):
        match tile_map[i][j]:
            case 1:
                PlatformTile(j * 32, i * 32, 1, main_tile_group)
            case 2:
                PlatformTile(j * 32, i * 32, 1, main_tile_group)
            case _:
                pass


# Identify connected components in horizontal axis only (platforms)

# Scipy Footprint
# https://docs.scipy.org/doc/scipy/tutorial/ndimage.html#filter-functions
structuring_element = np.array([[0, 0, 0], [1, 1, 1], [0, 0, 0]])

# Label each block of connected components with a different digit (same shape as original array)
x_components, _ = ndimage.label(
    np.array(tile_map),
    structure=structuring_element,
)
# returns slices with the bounding boxes
platforms = ndimage.find_objects(x_components)
# fills a new array with 1 on those slices. python <class 'slice'>

# This returns a tuple of slices with the (y,xß) bounds.
# e.g. (slice(3, 4, None), slice(0, 11, None))
#      (row_ind = 3 up to but not including 4, col_ind = 0 up to but not including 11)
for idx, platform in enumerate(platforms):
    y_index = platform[0].start
    x_start_index = platform[1].start
    x_stop_index = platform[1].stop - 1
    # Find Player
    if x_start_index == x_stop_index and tile_map[y_index][x_start_index] == 4:
        my_player = Player(y_index * 32, x_start_index * 32 + 32, main_tile_group)
        my_player_group.add(my_player)  # type: ignore
    else:
        # TODO: Create FlexiblePlatformSprite
        pass
    print(
        f"Platform {idx}: on row idx: {y_index} and col range: {x_start_index}, {x_stop_index}"
    )


running = True
while running == True:
    clock.tick(FPS)
    for event in pygame.event.get():
        pygame.key.start_text_input()
        if event.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        man_location -= 10
    if keys[pygame.K_RIGHT]:
        man_location += 10

    display_surface.fill("white")
    positions = get_deflection(man_location)
    man_width = 20
    pygame.draw.rect(
        display_surface,
        (255, 0, 0),
        (-man_width // 2 + man_location / 1000 * 100, 50, man_width, man_width),
    )
    if positions:
        pygame.draw.lines(display_surface, (0, 0, 0), False, positions, width=10)

    # update and draw sprite groups
    my_player_group.update(display_surface)
    my_player_group.draw(display_surface)
    main_tile_group.draw(display_surface)
    display_surface.blit(update_fps(), (10, 0))
    pygame.display.update()
pygame.quit()
