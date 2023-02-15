import pygame
from anastruct import SystemElements  # pyright: reportMissingTypeStubs=false
from anastruct import Vertex


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
        self.get_deflection_position(self.left + 40)

    def update(self, *args: pygame.Surface, **kwargs: None):
        """Update the platform"""
        # surface: pygame.Surface = args[0]
        self.image.fill((0, 0, 0))
        pass

    # def get_vertices(weight, position):
    """
    params: The weight of hero who is located on the platform.
    params: The position of the hero along the beam
    """

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

        # Create an element between every position
        for location, type in self.location_type:
            match type:
                case 1:
                    if location < player_position < location + 32:
                        pygame.draw.circle(
                            self.image,
                            (0, 255, 0),
                            (player_position - self.left, self.length // 10),
                            10,
                        )
                    pygame.draw.circle(
                        self.image,
                        (0, 0, 255),
                        (location - self.left, self.length // 10),
                        10,
                    )
                    pygame.draw.circle(
                        self.image,
                        (0, 0, 255),
                        (location + 32 - self.left, self.length // 10),
                        10,
                    )
                case 2:
                    triangle_base = [[10, 10], [0, 20], [20, 20]]
                    pygame.draw.polygon(
                        self.image,
                        (0, 255, 255),
                        [
                            [location - self.left, self.length // 10 + 10],
                            [location - self.left - 10, self.length // 10 + 20],
                            [location - self.left + 10, self.length // 10 + 20],
                        ],
                        2,
                    )
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
                        2,
                    )
                case _:
                    pass
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
