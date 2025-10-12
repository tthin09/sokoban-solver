from engine import Engine
from read_map import convert_image_to_map
from constants import GRAY, RED, GREEN, BLUE, WHITE, BLACK
from constants import EMPTY, WALL, PLAYER, RUBY, DESTINATION, RUBY_DONE
import numpy as np
import pygame
import time

map_name = "map_1"
map_image_path = f"maps/{map_name}.png"
tile_map, destinations = convert_image_to_map(map_image_path, DEBUG_MODE=False)
game = Engine(tile_map, destinations)

game.print_map()
game.print_player_pos()

W, H = 1200, 750
h = H - 150

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption(f"Sokoban - {map_name}")

col_count = game.tile_map.shape[0]
row_count = game.tile_map.shape[1]
square_width = h // row_count
BOARD_W = row_count * square_width
BOARD_H = col_count * square_width

move_list = "up,up,left,up,up,right,left,down,down,right,right,right,up,right,up,up,left,left,up,left,left,down,down,up,left,left,down,down,right,right,left,down,down,right,right,up,up,left,up,right"

FONT = pygame.font.Font(None, 48)


def draw_map(screen, map: np.ndarray, destinations: list):
    path_to_image = "assets/for_drawing/"
    screen.fill(GRAY)
    # Load surfaces
    player_surface = pygame.image.load(path_to_image + "player.png")
    player_surface = pygame.transform.scale(player_surface, (square_width, square_width))
    destination_surface = pygame.image.load(path_to_image + "destination.png")
    destination_surface = pygame.transform.scale(destination_surface, (square_width, square_width))
    ruby_surface = pygame.image.load(path_to_image + "ruby-default.png")
    ruby_surface = pygame.transform.scale(ruby_surface, (square_width, square_width))
    wall_surface = pygame.image.load(path_to_image + "wall.png")
    wall_surface = pygame.transform.scale(wall_surface, (square_width, square_width))
    ruby_done_surface = pygame.image.load(path_to_image + "ruby-done.png")
    ruby_done_surface = pygame.transform.scale(ruby_done_surface, (square_width, square_width))
    surface_map = {
        WALL: wall_surface,
        RUBY: ruby_surface,
        PLAYER: player_surface,
        RUBY_DONE: ruby_done_surface
    }
    for destination_pos in destinations:
        row, col = destination_pos
        color = GREEN
        tile_corner = (50 + col*square_width, 50 + row*square_width)
        destination_rect = destination_surface.get_rect()
        destination_rect.topleft = tile_corner
        screen.blit(destination_surface, destination_rect)
        
    for row in range(row_count):
        for col in range(col_count):
            tile = map[row][col]
            if tile == EMPTY: continue
            surface = surface_map[tile]
            # Check if ruby is at destination: Use green RUBY_DONE surface
            if tile == RUBY:
                for des in destinations:
                    if des[0] == row and des[1] == col:
                        surface = surface_map[RUBY_DONE]
            tile_corner = (50 + col*square_width, 50 + row*square_width)
            rect = surface.get_rect()
            rect.topleft = tile_corner
            screen.blit(surface, rect)
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
    
    # Draw history stats
    draw_history_stats()

def draw_history_stats():
    history_list = game.get_move_history()
    history_string = "".join([move[0].upper() for move in history_list])
    
    TOP_Y = H // 2 - 200
    # Move count: {count}
    move_count_text_surface = FONT.render(f"Move count: {len(history_list)}", True, WHITE)
    current_text_rect = move_count_text_surface.get_rect()
    current_text_rect.left = BOARD_W + 100
    current_text_rect.centery = TOP_Y
    screen.blit(move_count_text_surface, current_text_rect)
    
    # Move:
    move_text_surface = FONT.render("Move:", True, WHITE)
    current_text_rect.centery = TOP_Y + 50
    screen.blit(move_text_surface, current_text_rect)
    
    # {move_history}
    move_shown_per_line = 15
    for i in range(len(history_string) // move_shown_per_line + 1):
        current_line = history_string[i*move_shown_per_line : (i + 1)*move_shown_per_line]
        current_text_surface = FONT.render(current_line, True, WHITE)
        current_text_rect.centery = TOP_Y + 100 + i*50
        screen.blit(current_text_surface, current_text_rect)
    


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


