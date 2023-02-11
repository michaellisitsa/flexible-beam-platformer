import pygame


class Player(pygame.sprite.Sprite):
    """A player class that the user control"""

    vector = pygame.math.Vector2

    # Kinematic constants
    HORIZONTAL_ACCELERATION = 2
    HORIZONTAL_FRICTION = 0.15

    def __init__(self, x: int, y: int):
        """Init the player"""
        super().__init__()
        self.image = pygame.image.load("src/assets/green_monster.png")
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)

        self.lives = 5

        # Kinematics vectors (first value is the x, second value is the y)
        self.position = Player.vector(x, y)
        self.velocity = Player.vector(0, 0)
        self.acceleration = Player.vector(0, 0)

    def update(self, *args: pygame.Surface, **kwargs: None):
        """Update the player"""
        surface: pygame.Surface = args[0]
        # Set the acceleration vector to zero
        self.acceleration = Player.vector(0, 0)

        keys = pygame.key.get_pressed()
        # If the user is pressing a key,
        # set the x-component of the acceleration to a non-zero value
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.acceleration.x = -1 * Player.HORIZONTAL_ACCELERATION
        if keys[pygame.K_RIGHT] and self.rect.right < surface.get_width():
            self.acceleration.x = Player.HORIZONTAL_ACCELERATION
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= int(self.velocity.y)
        if keys[pygame.K_DOWN] and self.rect.bottom < surface.get_height():
            self.rect.y += int(self.velocity.y)

        # Calculate new kinematic values
        self.acceleration.x -= self.velocity.x * Player.HORIZONTAL_FRICTION

        self.velocity += self.acceleration  # adding vectors together
        self.position += (
            self.velocity + 0.5 * self.acceleration
        )  # d = vt + 1/2*a*t^2 (assume t is unit value)
        self.rect.left = int(self.position.x)
