import pygame
from bisect import bisect_left


class Player(pygame.sprite.Sprite):
    """A player class that the user control"""

    vector = pygame.math.Vector2

    # Kinematic constants
    HORIZONTAL_ACCELERATION = 2
    HORIZONTAL_FRICTION = 0.15
    VERTICAL_ACCELERATION = 0.5  # Gravity

    def __init__(self, x: int, y: int, platform_tile_group: pygame.sprite.Group, flexible_platform_group: pygame.sprite.Group):  # type: ignore
        """Init the player"""
        super().__init__()
        self.image = pygame.image.load("src/assets/green_monster.png")
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)

        self.lives = 5

        # Kinematics vectors (first value is the x, second value is the y)
        self.position = Player.vector(x, y)
        self.velocity = Player.vector(0, 0)
        self.acceleration = Player.vector(0, Player.VERTICAL_ACCELERATION)
        self.platform_tiles = platform_tile_group  # type: ignore
        self.flexible_platforms = flexible_platform_group  # type: ignore

    def update(self, *args: pygame.Surface, **kwargs: None):
        """Update the player"""
        surface: pygame.Surface = args[0]
        # Set the acceleration vector to zero
        self.acceleration.x = 0

        keys = pygame.key.get_pressed()
        # If the user is pressing a key,
        # set the x-component of the acceleration to a non-zero value
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.acceleration.x = -1 * Player.HORIZONTAL_ACCELERATION
        if keys[pygame.K_RIGHT] and self.rect.right < surface.get_width():
            self.acceleration.x = Player.HORIZONTAL_ACCELERATION
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.position.y = 32

        # Calculate new kinematic values
        self.acceleration.x -= self.velocity.x * Player.HORIZONTAL_FRICTION

        self.velocity += self.acceleration  # adding vectors together
        self.position += (
            self.velocity + 0.5 * self.acceleration
        )  # d = vt + 1/2*a*t^2 (assume t is unit value)
        self.rect.bottomleft = (int(self.position.x), int(self.position.y))

        # check for collisions with platform tiles
        collided_platforms = pygame.sprite.spritecollide(  # type:ignore
            self, self.platform_tiles, False  # type:ignore
        )
        if collided_platforms:
            self.position.y = collided_platforms[0].rect.top + 1  # type:ignore
            self.velocity.y = 0
        collided_flexible_platforms = pygame.sprite.spritecollide(  # type:ignore
            self, self.flexible_platforms, False  # type:ignore
        )
        if collided_flexible_platforms:
            beam_center = collided_flexible_platforms[0].rect.centery
            if beam_center <= self.position.y:
                deflections = collided_flexible_platforms[0].update(self.position.x)
                if deflections:
                    deflection_index_at_player = bisect_left(
                        [item[0] for item in deflections], self.position.x
                    )
                    # Cater for bisect_left returning index of the next empty index if it is off the list
                    # prevent list index out of range errors
                    if deflection_index_at_player == len(deflections):
                        deflection_at_player = deflections[-1][1]
                    else:
                        deflection_at_player = deflections[deflection_index_at_player][
                            1
                        ]
                    position_y = (
                        beam_center
                        + deflection_at_player
                        - collided_flexible_platforms[0].length // 10
                    )  # type:ignore
                    if (
                        deflection_at_player
                        > collided_flexible_platforms[0].rect.height
                    ):
                        self.position.y = collided_flexible_platforms[0].rect.bottom
                    else:
                        self.position.y = position_y  # type:ignore
                self.velocity.y = 0
