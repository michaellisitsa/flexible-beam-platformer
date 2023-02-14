import pygame


class FlexiblePlatform(pygame.sprite.Sprite):
    def __init__(self, y_index: int, x_start_index: int, x_stop_index: int):
        super().__init__()
        self.length = (
            32 * (x_stop_index - x_start_index) + 32
        )  # Additional tile width at end
        self.image = pygame.Surface((self.length, self.length // 5))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (32 * x_start_index, 32 * y_index + self.length // 10)
        # Draw undeflected beam
        pygame.draw.line(
            self.image,
            (255, 0, 0),
            (0, self.length // 10),
            (self.length, self.length // 10),
            width=6,
        )
        # Define a flexible platform.
        # Property initial platform position.
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
