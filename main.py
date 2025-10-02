from engine import Engine
from read_map import convert_image_to_map
import numpy as np


map_image_path = "maps/map_1.png"
tile_map, destinations = convert_image_to_map(map_image_path)
game = Engine(tile_map, destinations)

game.print_map()
game.print_player_pos()

while not game.get_win_state():
    user = input("Make a move: ")
    if user == "break":
        break
    
    game.make_a_move(user)
    game.print_move_history()
    game.print_destinations()
    game.print_map()
    print()
    
print("You have won!")