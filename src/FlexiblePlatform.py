import pygame
from anastruct import SystemElements  # pyright: reportMissingTypeStubs=false
from anastruct import Vertex
import numpy as np


class FlexiblePlatform(pygame.sprite.Sprite):
    def __init__(
        self,
        y_index: int,
        x_start_index: int,
        x_stop_index: int,
        platform_arr: list[int],
    ):
        super().__init__()
        self.length = (
            32 * (x_stop_index - x_start_index) + 32
        )  # Additional tile width at end
        self.image = pygame.Surface((self.length, self.length // 5))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.left = x_start_index * 32
        self.rect.bottomleft = (self.left, 32 * y_index + self.length // 10)

        # Create a platform
        self.platform_arr = platform_arr

        # Generate a list of tuples with x and y positions.
        self.location_type: list[tuple[int, int]] = []
        for idx, x in enumerate(range(x_start_index, x_stop_index + 1)):
            self.location_type.append((32 * x, platform_arr[idx]))

        # Draw undeflected beam
        pygame.draw.lines(
            self.image,
            (255, 0, 0),
            False,
            [
                (location[0] - self.left, self.length // 10)
                for location in self.location_type
            ],
            width=6,
        )
        # Property initial support positions.
        # Property section properties.
        # Doesn't need to initialize anastruct just yet.

    def update(self, *args: pygame.Surface, **kwargs: None):
        """Update the platform"""
        player_position = args[0]
        self.image.fill((0, 0, 0))
        try:
            deflections = self.get_deflection_position(player_position)
            pygame.draw.lines(
                self.image,
                (255, 0, 0),
                False,
                deflections,
                width=6,
            )
        except:
            # There are no forces or there was an error calculating deflection
            # Draw undeflected beam
            pygame.draw.lines(
                self.image,
                (255, 0, 0),
                False,
                [
                    (location[0] - self.left, self.length // 10)
                    for location in self.location_type
                ],
                width=6,
            )

    def get_deflection_position(self, player_position):
        """Called when there is a collision with the hero.
        Initialize anastruct and geometry based on platform position
        Switches out the platform for the deflected shape."""

        # Initialize Anastruct
        # Create a 50x50x1.6 G350 SHS
        I_shs = 1.17e-7  # m^4
        E_steel = 2e11  # N/m2
        A_shs = 0.000303  # m^2

        # Number of elements for post-processing
        mesh = 10
        ss = SystemElements(
            mesh=mesh,
            EI=I_shs * E_steel,
            EA=E_steel * A_shs,
        )

        """Assign a point load to the extra node"""
        player_load = 981  # N ( 100 kg * 9.81 N / kg )

        # Create an element between every position
        for location, type in self.location_type:
            start_vertex = Vertex(location, 0)
            end_vertex = Vertex(location + 32, 0)
            if location < player_position < location + 32:
                player_vertex = Vertex(player_position, 0)
                pygame.draw.circle(
                    self.image,
                    (0, 255, 0),
                    (player_position - self.left, self.length // 10),
                    3,
                )
                ss.add_element(location=(start_vertex, player_vertex))
                ss.add_element(
                    location=(
                        player_vertex,
                        end_vertex,
                    )
                )
                player_node = ss.find_node_id((player_position, 0))
                ss.point_load(node_id=player_node, Fy=player_load)  # type:ignore
            else:
                ss.add_element(
                    location=(
                        Vertex(location, 0),
                        Vertex(location + 32, 0),
                    )
                )
            pygame.draw.circle(
                self.image,
                (0, 0, 255),
                (location - self.left, self.length // 10),
                3,
            )
            pygame.draw.circle(
                self.image,
                (0, 0, 255),
                (location + 32 - self.left, self.length // 10),
                3,
            )

            # Now make sure that if the man lands on a node, you just add the load there.
            if location == player_position:
                player_node = ss.find_node_id((location, 0))
                ss.point_load(node_id=player_node, Fy=player_load)  # type:ignore

            # Assign supports and draw icons
            match type:
                case 2:
                    pygame.draw.polygon(
                        self.image,
                        (0, 255, 255),
                        [
                            [location - self.left, self.length // 10 + 10],
                            [location - self.left - 10, self.length // 10 + 20],
                            [location - self.left + 10, self.length // 10 + 20],
                        ],
                        0,
                    )
                    start_node = ss.find_node_id(start_vertex)
                    ss.add_support_hinged(node_id=start_node)

                case 3:
                    pygame.draw.rect(
                        self.image,
                        (0, 255, 255),
                        (
                            location - self.left,
                            self.length // 10 - 10,
                            10,
                            20,
                        ),
                        0,
                    )
                    start_node = ss.find_node_id(start_vertex)
                    ss.add_support_fixed(node_id=start_node)
                case _:
                    pass

        ss.solve()
        # Use internal plotting method
        deflections = ss.plot_values.displacements(factor=0.005, linear=False)
        deflections_transposed = np.transpose(np.array(deflections)).tolist()
        for deflection in deflections_transposed:
            deflection[0] = deflection[0]
            deflection[1] = deflection[1] + self.length // 10
        return deflections_transposed
        # if platform_tile[1] == 1:
        #     if platform_arr[0] < man_position < platform_arr[0] + 32:
        #         add_element(from platform_arr[0] to man_position)
        #         add_element(from man_position to platform_arr[0]+32)
        #         man_node = find_node((man_position,0))
        #         add_point_load(load on man_node)
        #     else:
        #         generate a normal element.
        #
        #     # Now make sure that if the man lands on a node, you just add the load there.
        #     if platform_arr[0] == man_position:
        #         man_node = find_node((platform_arr[0],0))
        #         add_point_load(load on man_node)
        # else if platform_arr == "2":
        #     generate a normal element, but add a support to the start node.
