import numpy as np
from constants import EMPTY, WALL, PLAYER, RUBY, DESTINATION

directions = {
    "left": (0, -1),
    "right": (0, 1),
    "up": (-1, 0),
    "down": (1, 0),
}

class Engine:
    def __init__(self, tile_map: np.ndarray, destinations: list):
        self.tile_map = tile_map
        self.destinations = destinations
        self.player_pos = self.get_player_pos()
        
        self.move_history = []
        
    def make_a_move(self, direction):
        if direction not in directions.keys():
            print(f"Invalid direction input, direction should be in {directions.keys()}")
            return
        if direction not in self.get_available_moves():
            return
        
        dx, dy = directions[direction]
        next_square_pos = (self.player_pos[0] + dx, self.player_pos[1] + dy)
        next_square = self.tile_map[next_square_pos[0]][next_square_pos[1]]
        if next_square == EMPTY:
            self.tile_map[next_square_pos[0]][next_square_pos[1]] = PLAYER
            self.tile_map[self.player_pos[0]][self.player_pos[1]] = EMPTY
        elif next_square == RUBY: # Push Ruby to next square
            next_2_square_pos = (self.player_pos[0] + 2*dx, self.player_pos[1] + 2*dy)
            self.tile_map[next_2_square_pos[0]][next_2_square_pos[1]] = RUBY
            self.tile_map[next_square_pos[0]][next_square_pos[1]] = PLAYER
            self.tile_map[self.player_pos[0]][self.player_pos[1]] = EMPTY
        else:
            print("Unexpected error when making a move")
        self.player_pos = next_square_pos
        self.move_history.append(direction)
            
    def get_available_moves(self) -> list:
        available_moves = []
        for direction, (dx, dy) in directions.items():
            next_square = self.tile_map[self.player_pos[0] + dx][self.player_pos[1] + dy]
            if next_square == WALL: # Next square is wall, can't move to
                continue
            if next_square == RUBY:
                next_2_square = self.tile_map[self.player_pos[0] + 2*dx][self.player_pos[1] + 2*dy]
                if next_2_square in [WALL, RUBY]: # 2 consecutive squares, can't move to
                    continue
            available_moves.append(direction)
        return available_moves
        
    def get_player_pos(self) -> tuple:
        for x in range(self.tile_map.shape[0]):
            for y in range(self.tile_map.shape[1]):
                if self.tile_map[x][y] == PLAYER:
                    return (x, y)
        return None
    
    def get_win_state(self) -> bool:
        for row in range(self.tile_map.shape[0]):
            for col in range(self.tile_map.shape[1]):
                tile = self.tile_map[row][col]
                if tile == RUBY and (row, col) not in self.destinations:
                    return False
        return True
    
    def print_player_pos(self):
        print(f"Player's pos: {self.player_pos}")
    
    def print_map(self):
        print(self.tile_map)
        
    def print_move_history(self):
        print(f"Move history: self.move_history")
    
    def print_destinations(self):
        print(f"Destinations: {[(int(x), int(y)) for x, y in self.destinations]}")

    def print_adjacent_squares(self):
        print("Printing adjacent squares:")
        for direction, (dx, dy) in directions.items():
            print(f"\tAt {direction}: {self.tile_map[self.player_pos[0] + dx][self.player_pos[1] + dy]}")
        print(f"Current available moves {self.get_available_moves()}")