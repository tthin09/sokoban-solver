from engine import Engine
from read_map import convert_image_to_map
from constants import GRAY, RED, GREEN, BLUE, WHITE, BLACK
from constants import EMPTY, WALL, PLAYER, RUBY, DESTINATION
import numpy as np
import pygame
import time


def draw_map(screen, map: np.ndarray, destinations: list):
    screen.fill(GRAY)
    col_count = map.shape[0]
    row_count = map.shape[1]
    square_width = h // row_count
    color_map = {
        WALL: WHITE,
        RUBY: RED,
        PLAYER: BLUE,
    }
    for destination_pos in destinations:
        row, col = destination_pos
        color = GREEN
        tile_corner = (50 + col*square_width, 50 + row*square_width)
        pygame.draw.rect(screen, color, (tile_corner[0], tile_corner[1],
                                        square_width, square_width), 0)
    for row in range(row_count):
        for col in range(col_count):
            tile = map[row][col]
            if tile == EMPTY: continue
            offset = 6 if tile in [RUBY, PLAYER] else 0
            tile_width = square_width - offset
            color = color_map[tile]
            tile_corner = (50 + offset//2 + col*square_width,
                           50 + offset//2 + row*square_width)
            pygame.draw.rect(screen, color, (tile_corner[0], tile_corner[1],
                                             tile_width, tile_width), 0)
    # Draw grid
    for row in range(row_count + 1):
        pygame.draw.line(screen, BLACK,
                         (50, 50 + row*square_width),
                         (50 + col_count*square_width, 50 + row*square_width),
                         1)
    for col in range(col_count + 1):
        pygame.draw.line(screen, BLACK,
                         (50 + col*square_width, 50),
                         (50 + col*square_width, 50 + row_count*square_width),
                         1)
    # Draw border
    pygame.draw.rect(screen, BLACK, (50, 50,
                                     square_width*col_count, square_width*row_count), 4)


map_name = "map_1"
map_image_path = f"maps/{map_name}.png"
tile_map, destinations = convert_image_to_map(map_image_path, DEBUG_MODE=False)
game = Engine(tile_map, destinations)

game.print_map()
game.print_player_pos()

W, H = 1000, 750
h = H - 150

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption(f"Sokoban - {map_name}")

move_list = "up,up,left,up,up,right,left,down,down,right,right,right,up,right,up,up,left,left,up,left,left,down,down,up,left,left,down,down,right,right,left,down,down,right,right,up,up,left,up,right"

for move in move_list.split(','):
    draw_map(screen, game.tile_map, game.destinations)
    pygame.display.flip()
    game.make_a_move(move)
    time.sleep(0.15)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    draw_map(screen, game.tile_map, game.destinations)
    pygame.display.flip()
    
pygame.quit()


