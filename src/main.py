import pygame
from anastruct import SystemElements  # pyright: reportMissingTypeStubs=false
from anastruct import Vertex
import numpy as np
from scipy import ndimage

from src.FlexiblePlatform import FlexiblePlatform
from src.PlatformTile import PlatformTile
from src.assets.tile_map import tile_map
from src.Player import Player

pygame.init()
font = pygame.font.SysFont(None, 24)


def update_fps():
    fps = str(int(clock.get_fps()))
    fps_text = font.render(fps, 1, pygame.Color("coral"))
    return fps_text


display_surface = pygame.display.set_mode([960 + 8 * 32, 640 + 128])

# Set FPS and clock
FPS = 60
clock = pygame.time.Clock()

# Create player group and object
my_player_group = pygame.sprite.Group()  # type: ignore


# Create sprite groups
main_tile_group = pygame.sprite.Group()  # type: ignore
# platform_tile_group = pygame.sprite.Group()
flexible_platform_group = pygame.sprite.Group()  # type: ignore

# Create individual tile objects from the tile map
# Loop through the 20 lists in tile_map (i moves down the map)
for i in range(len(tile_map)):
    for j in range(len(tile_map[i])):
        match tile_map[i][j]:
            case 5:
                PlatformTile(j * 32, i * 32, 1, main_tile_group)
            case _:
                pass


# Identify connected components in horizontal axis only (platforms)

# Scipy Footprint
# https://docs.scipy.org/doc/scipy/tutorial/ndimage.html#filter-functions
structuring_element = np.array([[0, 0, 0], [1, 1, 1], [0, 0, 0]])

# Label each block of connected components with a different digit (same shape as original array)
x_components, _ = ndimage.label(
    np.array(tile_map),
    structure=structuring_element,
)
# returns slices with the bounding boxes
platforms = ndimage.find_objects(x_components)

# fills a new array with 1 on those slices. python <class 'slice'>

# This returns a tuple of slices with the (y,xß) bounds.
# e.g. (slice(3, 4, None), slice(0, 11, None))
#      (row_ind = 3 up to but not including 4, col_ind = 0 up to but not including 11)
for idx, platform in enumerate(platforms):
    y_index: int = platform[0].start
    x_start_index: int = platform[1].start
    x_stop_index: int = platform[1].stop - 1
    # Find Player
    if x_start_index == x_stop_index and tile_map[y_index][x_start_index] == 4:
        my_player = Player(
            x_start_index * 32 + 32,
            y_index * 32,
            main_tile_group,
            flexible_platform_group=flexible_platform_group,
        )
        my_player_group.add(my_player)  # type: ignore
    elif tile_map[y_index][x_start_index] == 5:
        # This is a rigid platform, so has been created elsewhere
        pass
    else:
        platform_arr: list[int] = tile_map[y_index][x_start_index : x_stop_index + 1]
        my_platform = FlexiblePlatform(
            y_index, x_start_index, x_stop_index, platform_arr
        )
        flexible_platform_group.add(my_platform)  # type: ignore
    print(
        f"Platform {idx}: on row idx: {y_index} and col range: {x_start_index}, {x_stop_index}"
    )


running = True
while running == True:
    clock.tick(FPS)
    for event in pygame.event.get():
        pygame.key.start_text_input()
        if event.type == pygame.QUIT:
            running = False

    display_surface.fill("white")

    # update and draw sprite groups
    my_player_group.draw(display_surface)
    my_player_group.update(display_surface)
    main_tile_group.draw(display_surface)
    flexible_platform_group.draw(display_surface)
    display_surface.blit(update_fps(), (10, 0))
    pygame.display.update()
pygame.quit()
