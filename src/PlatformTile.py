import pygame


class PlatformTile(pygame.sprite.Sprite):
    def __init__(
        self,
        x: int,
        y: int,
        image_int: int,
        main_group: pygame.sprite.Group,  # type: ignore
    ):
        """Initialise the platform"""
        super().__init__()
        if image_int == 1:
            self.image = pygame.image.load("src/assets/grass.png")
        else:
            self.image = pygame.image.load("src/assets/dirt.png")
        main_group.add(self)  # type: ignore

        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self, *args: pygame.Surface, **kwargs: None):
        """Update the platform"""
        # surface: pygame.Surface = args[0]
        pass
