import pygame


class Player(pygame.sprite.Sprite):
    """A player class that the user control"""

    def __init__(self, x: int, y: int):
        """Init the player"""
        super().__init__()
        self.image = pygame.image.load("src/assets/green_monster.png")
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)

        self.lives = 5
        self.velocity = 8

    def update(self, *args: pygame.Surface, **kwargs: None):
        """Update the player"""
        surface: pygame.Surface = args[0]
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.velocity
        if keys[pygame.K_RIGHT] and self.rect.right < surface.get_width():
            self.rect.x += self.velocity
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.velocity
        if keys[pygame.K_DOWN] and self.rect.bottom < surface.get_height():
            self.rect.y += self.velocity
