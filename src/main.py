import time
import pygame
from anastruct import SystemElements
from sys import exit
from anastruct import Vertex
import pint
import numpy as np

u = pint.UnitRegistry()
print(dir(u.sys))


def get_deflection(location):

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
    # element_id = ss.add_element(location=(start_vertex, ))

    # Heavy man at location
    # Point loads need a node to be created first.
    intermediate_loc = location * u.mm
    intermediate_vertex = Vertex(intermediate_loc.to_base_units().magnitude, 0)
    # Add a cantilever
    cant_beam_loc = 3000 * u.mm
    cant_vertex = Vertex(cant_beam_loc.to_base_units().magnitude, 0)
    if intermediate_vertex.x < end_vertex.x:
        # print("Interior Span")
        element_id = ss.add_element(location=(start_vertex, intermediate_vertex))
        element_id2 = ss.add_element(location=(intermediate_vertex, end_vertex))

        element_id3 = ss.add_element(location=(end_vertex, cant_vertex))

        # ss.insert_node(element_id=element_id, location=intermediate_vertex)
        intermediate_node = ss.find_node_id(intermediate_vertex)
    elif intermediate_vertex.x > end_vertex.x:
        element_id = ss.add_element(location=(start_vertex, end_vertex))
        element_id2 = ss.add_element(location=(end_vertex, intermediate_vertex))
        element_id3 = ss.add_element(location=(intermediate_vertex, cant_vertex))
        intermediate_node = ss.find_node_id(intermediate_vertex)
    else:
        return None

    # 100kg man
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

    def get_element_position(
        element_id, xoffset=0, start_node_offset=None, end_node_offset=None
    ):
        element = ss.element_map[element_id]
        element_deflections = element.deflection
        element_spacing = (element.vertex_2.x - element.vertex_1.x) / mesh
        positions = []
        for idx, loc in enumerate(range(mesh)):
            if start_node_offset:
                current_y_offset = start_node_offset * (loc + 1) / mesh
                positions.append(
                    [
                        xoffset + 80 * (loc * element_spacing + element_spacing / 2),
                        100 - 5000 * (-current_y_offset + element_deflections[idx]),
                    ]
                )
            elif end_node_offset:
                current_y_offset = end_node_offset * (mesh - loc) / mesh
                positions.append(
                    [
                        xoffset + 80 * (loc * element_spacing + element_spacing / 2),
                        100 - 5000 * (-current_y_offset + element_deflections[idx]),
                    ]
                )
            else:
                positions.append(
                    [
                        xoffset + 80 * (loc * element_spacing + element_spacing / 2),
                        -5000 * (element_deflections[idx]),
                    ]
                )
        return positions

    intermediate_node_offset = ss.get_node_displacements(intermediate_node)["uy"]
    # TODO: Fix so that the node is always on the element in question.
    # Currently the intermediate node may be outside of the element 1.
    position1 = get_element_position(1, start_node_offset=intermediate_node_offset)
    position1_xoffset = position1[-1][0]
    position2 = get_element_position(
        2, xoffset=position1_xoffset, end_node_offset=intermediate_node_offset
    )
    position2_xoffset = position2[-1][0]
    # position2 = get_element_position(2, xoffset=xoffset)
    cant_node_offset = ss.get_node_displacements(cant_node)["uy"]
    return (
        position1
        + position2
        + get_element_position(
            3, xoffset=position2_xoffset, start_node_offset=cant_node_offset
        )
    )


# element_positions =
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

running = True
while running == True:
    clock.tick(FPS)
    for event in pygame.event.get():
        pygame.key.start_text_input()
        if event.type == pygame.QUIT:
            running = False
        # if event.type == pygame.KEYDOWN:
        #     if event.key == pygame.K_RIGHT:
        #         man_location += 10
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
        (-man_width // 2 + man_location / 1000 * 80, 50, man_width, man_width),
    )
    if positions:
        pygame.draw.aalines(display_surface, (0, 0, 0), False, positions)
    display_surface.blit(update_fps(), (10, 0))
    # pygame.draw.aalines(
    #     display_surface, (0, 0, 0), False, [[20, 50], [20, 100], [50, 100]]
    # )
    # pygame.draw.aaline(display_surface, (60, 179, 113), [0, 50], [50, 80], True)
    # pygame.draw.lines(
    #     display_surface, "black", False, [[0, 80], [50, 90], [200, 80], [220, 30]], 5
    # )
    pygame.display.update()
pygame.quit()
