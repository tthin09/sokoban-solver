from engine import Engine
from read_map import convert_image_to_map
import numpy as np
import pandas as pd

i = 3
map_image_path = f"maps/map_{i}.png"
tile_map, destinations = convert_image_to_map(map_image_path)
df_tm = pd.DataFrame(tile_map)
df_des = pd.DataFrame(destinations)

df_tm.to_csv(f"tile_map/map_{i}.csv", index=False, header=False)
df_des.to_csv(f"tile_map/map_{i}_des.csv", index=False, header=False)

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