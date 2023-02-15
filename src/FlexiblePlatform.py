import pygame


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
        self.locations: list[tuple[int, int]] = []
        for idx, x in enumerate(range(x_start_index, x_stop_index + 1)):
            self.locations.append((32 * x, platform_arr[idx]))

        # Draw undeflected beam
        pygame.draw.lines(
            self.image,
            (255, 0, 0),
            False,
            [
                (location[0] - self.left, self.length // 10)
                for location in self.locations
            ],
            width=6,
        )
        # Property initial support positions.
        # Property section properties.
        # Doesn't need to initialize anastruct just yet.

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

    # def get_deflection_position():
    # Called when their is a collision with the hero.
    # Initialize anastruct and geometry based on platform position
    # Switches out the platform for the deflected shape.

    #
