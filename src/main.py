import time
import pygame
from anastruct import SystemElements
from sys import exit
from anastruct import Vertex
import pint
import numpy as np
from src.Player import Player

u = pint.UnitRegistry()


def get_deflection(location):
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


display_surface = pygame.display.set_mode([400, 300])

# Set FPS and clock
FPS = 60
clock = pygame.time.Clock()

man_location = 500

# Create player group and object
my_player_group = pygame.sprite.Group()  # type: ignore
my_player = Player(display_surface.get_width() // 2, display_surface.get_height() // 2)
my_player_group.add(my_player)  # type: ignore

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
    display_surface.blit(update_fps(), (10, 0))
    pygame.display.update()
pygame.quit()
