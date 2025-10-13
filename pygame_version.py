from engine import Engine
from read_map import Map, convert_image_to_map, convert_matrix_to_map
from constants import GRAY, RED, GREEN, BLUE, WHITE, BLACK, LIGHT_GRAY
from constants import EMPTY, WALL, PLAYER, RUBY, DESTINATION, RUBY_DONE
from img_to_matrix import img2matrix
from solve import solve_and_print
import numpy as np
import pygame
import time
import sys


W, H = 1200, 750
h = H - 150
MAP_CORNER_OFFSET = 50


def draw_map(screen, map: list, destinations: list):
    # Fill color background
    screen.fill(LIGHT_GRAY)
    pygame.draw.rect(screen, GRAY, (MAP_CORNER_OFFSET, MAP_CORNER_OFFSET, BOARD_W, BOARD_H), 0)
    # Load surfaces
    path_to_image = "assets/for_drawing/"
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
        tile_corner = (MAP_CORNER_OFFSET + col*square_width, MAP_CORNER_OFFSET + row*square_width)
        destination_rect = destination_surface.get_rect()
        destination_rect.topleft = tile_corner
        screen.blit(destination_surface, destination_rect)
        
    for row in range(row_count):
        for col in range(col_count):
            tile = map[row][col]
            if tile in [EMPTY, DESTINATION]: continue
            surface = surface_map[tile]
            # Check if ruby is at destination: Use green RUBY_DONE surface
            if tile == RUBY:
                for des in destinations:
                    if des[0] == row and des[1] == col:
                        surface = surface_map[RUBY_DONE]
            tile_corner = (MAP_CORNER_OFFSET + col*square_width, MAP_CORNER_OFFSET + row*square_width)
            rect = surface.get_rect()
            rect.topleft = tile_corner
            screen.blit(surface, rect)
    # Draw grid
    for row in range(row_count + 1):
        pygame.draw.line(screen, BLACK,
                         (MAP_CORNER_OFFSET, MAP_CORNER_OFFSET + row*square_width),
                         (MAP_CORNER_OFFSET + col_count*square_width, MAP_CORNER_OFFSET + row*square_width),
                         1)
    for col in range(col_count + 1):
        pygame.draw.line(screen, BLACK,
                         (MAP_CORNER_OFFSET + col*square_width, MAP_CORNER_OFFSET),
                         (MAP_CORNER_OFFSET + col*square_width, MAP_CORNER_OFFSET + row_count*square_width),
                         1)
    # Draw border
    pygame.draw.rect(screen, BLACK, (MAP_CORNER_OFFSET, MAP_CORNER_OFFSET,
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
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pygame_version.py <map_name> [--method]")
        print("Example: python pygame_version.py map_3")
        print("Your map_name is your map's image name. Method is 'bfs' or 'A*'")
        sys.exit(1)
        
    map_name = sys.argv[1]
    if len(sys.argv) >= 3:
        search_method = sys.argv[2]
    else:
        print("No method provided in the argument, using default A* algorithm")
        search_method = "A*"
    
    move_list = list(solve_and_print(map_name, search_method, printout=False))
    
    map_matrix = img2matrix(map_name)
    tile_map, destinations = convert_matrix_to_map(map_matrix).unpack()

    game = Engine(tile_map, destinations)
    game.print_map()
    game.print_player_pos()
    game.print_destinations()
    
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption(f"Sokoban - {map_name}")

    FONT = pygame.font.Font(None, 48)

    col_count = game.tile_map.shape[0]
    row_count = game.tile_map.shape[1]
    square_width = h // row_count
    BOARD_W = row_count * square_width
    BOARD_H = col_count * square_width

        
    current_move_index = 0
    time_per_move = 0.1 * 1000
    start_time = pygame.time.get_ticks()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        if pygame.time.get_ticks() - start_time > time_per_move and current_move_index < len(move_list):
            start_time = pygame.time.get_ticks()
            game.make_a_move(move_list[current_move_index])
            current_move_index += 1
            
        draw_map(screen, game.tile_map, game.destinations)
        pygame.display.flip()
        
    pygame.quit()


