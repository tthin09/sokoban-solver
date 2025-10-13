#!/usr/bin/env python3
"""
solve.py

Usage:
    python solve.py map_3          # runs A* on tile_maps/map_3.csv (default)
    python solve.py map_3 --bfs    # runs BFS instead of A*

Input CSV format (same as your loader):
    0 = empty
    1 = wall
    2 = player
    3 = box (ruby)
    4 = destination (goal)
    5 = box on destination

Output:
    Prints the final move string (sequence of characters U,D,L,R).
    Also prints some stats (nodes expanded, time).
"""

import sys
import time
import pandas as pd
import numpy as np
from collections import deque
import heapq
import itertools
from img_to_matrix import img2matrix

# Directions: Up, Down, Left, Right
MOVES = {
    'U': (-1, 0),
    'D': (1, 0),
    'L': (0, -1),
    'R': (0, 1)
}

def load_map(file_name):
    df = pd.read_csv(f'tile_maps/{file_name}.csv', header=None, index_col=None)
    nf = df.to_numpy()
    rows, cols = nf.shape

    walls = set()
    goals = set()
    boxes = set()
    player = None

    for r in range(rows):
        for c in range(cols):
            val = int(nf[r, c])
            if val == 1:
                walls.add((r, c))
            elif val == 2:
                player = (r, c)
            elif val == 3:
                boxes.add((r, c))
            elif val == 4:
                goals.add((r, c))
            elif val == 5:
                # box on destination and also a goal cell
                boxes.add((r, c))
                goals.add((r, c))
            # 0 is empty -> ignore

    if player is None:
        raise ValueError("Map does not contain a player (value 2)")

    return {
        'rows': rows,
        'cols': cols,
        'walls': walls,
        'goals': goals,
        'boxes': frozenset(boxes),
        'player': player
    }

def is_goal_state(boxes, goals):
    # all boxes on goals (all box positions are subset of goals)
    return set(boxes) <= set(goals)

def neighbors(state):
    """
    Given a state (player_pos, boxes_frozenset, walls), yield (next_state, move_char).
    Note: next_state is (player_pos, boxes_frozenset)
    """
    player, boxes, walls, rows, cols = state
    boxes_set = set(boxes)
    for m, (dr, dc) in MOVES.items():
        nr = player[0] + dr
        nc = player[1] + dc
        if not (0 <= nr < rows and 0 <= nc < cols):
            continue
        if (nr, nc) in walls:
            continue
        if (nr, nc) in boxes_set:
            # trying to push box
            br = nr + dr
            bc = nc + dc
            if not (0 <= br < rows and 0 <= bc < cols):
                continue
            if (br, bc) in walls or (br, bc) in boxes_set:
                # can't push
                continue
            # push succeeds
            new_boxes = set(boxes_set)
            new_boxes.remove((nr, nc))
            new_boxes.add((br, bc))
            yield (( (nr, nc), frozenset(new_boxes), walls, rows, cols ), m)
        else:
            # simple move
            yield (( (nr, nc), boxes, walls, rows, cols ), m)

def state_key(player, boxes):
    # canonical representation for visited set
    # sort boxes to make tuple deterministic
    return (player, tuple(sorted(boxes)))

def reconstruct_path(came_from, end_key):
    # came_from: dict mapping state_key -> (prev_state_key, move)
    moves = []
    cur = end_key
    while cur in came_from and came_from[cur] is not None:
        prev, move = came_from[cur]
        moves.append(move)
        cur = prev
    return ''.join(reversed(moves))

def bfs_solve(mapdata, max_nodes=500000):
    """
    Breadth-first search that returns move string or None if unsolvable within limit.
    """
    rows = mapdata['rows']; cols = mapdata['cols']
    walls = mapdata['walls']
    goals = mapdata['goals']
    start_player = mapdata['player']
    start_boxes = mapdata['boxes']

    start_state = (start_player, start_boxes, walls, rows, cols)
    start_key = state_key(start_player, start_boxes)

    if is_goal_state(start_boxes, goals):
        return ""

    q = deque()
    q.append(start_state)
    came_from = { start_key: None }
    expanded = 0

    while q:
        cur = q.popleft()
        player, boxes, _, _, _ = cur
        cur_key = state_key(player, boxes)

        expanded += 1
        if expanded > max_nodes:
            # bail out if too many nodes
            return None

        for (nstate, move) in neighbors(cur):
            nplayer, nboxes, _, _, _ = nstate
            nkey = state_key(nplayer, nboxes)
            if nkey in came_from:
                continue
            came_from[nkey] = (cur_key, move)
            if is_goal_state(nboxes, goals):
                return reconstruct_path(came_from, nkey)
            q.append(nstate)
    return None

def manhattan(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def heuristic(boxes, goals):
    """
    Heuristic: minimal sum of Manhattan distances from boxes to goals.
    This computes optimal assignment by permutation enumeration (works fine when #boxes small).
    """
    boxes_list = list(boxes)
    goals_list = list(goals)
    nb = len(boxes_list)
    ng = len(goals_list)
    if nb == 0:
        return 0
    # If there are more goals than boxes, we pick best subset via permutations of goals of length nb
    # But typical Sokoban has #goals == #boxes
    best = float('inf')
    # if nb <= ng we consider all combinations of goals of size nb and then permutations mapping boxes->goals
    # to keep simple, if counts equal just permute goals; if not equal, we choose combinations
    if nb <= ng:
        for chosen in itertools.permutations(goals_list, nb):
            s = 0
            for i in range(nb):
                s += manhattan(boxes_list[i], chosen[i])
                if s >= best:
                    break
            if s < best:
                best = s
    else:
        # more boxes than goals (unusual) -> pair boxes to nearest goals with repeats allowed (sum of min)
        s = 0
        for b in boxes_list:
            s += min(manhattan(b, g) for g in goals_list)
        best = s
    return best

def a_star_solve(mapdata, max_nodes=500000):
    """
    A* search over step-by-step player moves.
    Returns move string or None.
    """
    rows = mapdata['rows']; cols = mapdata['cols']
    walls = mapdata['walls']
    goals = mapdata['goals']
    start_player = mapdata['player']
    start_boxes = mapdata['boxes']

    start_state = (start_player, start_boxes, walls, rows, cols)
    start_key = state_key(start_player, start_boxes)

    if is_goal_state(start_boxes, goals):
        return ""

    # priority queue: (f_score, g_score, unique_id, (player, boxes))
    open_heap = []
    g_score = { start_key: 0 }
    h0 = heuristic(start_boxes, goals)
    entry = (h0, 0, 0, start_state)
    heapq.heappush(open_heap, entry)
    came_from = { start_key: None }

    expanded = 0
    uid = 1
    visited = set()

    while open_heap:
        f, g, _, cur = heapq.heappop(open_heap)
        player, boxes, _, _, _ = cur
        cur_key = state_key(player, boxes)

        # skip if we've processed better g_score already
        if g_score.get(cur_key, float('inf')) < g:
            continue

        expanded += 1
        if expanded > max_nodes:
            return None

        if is_goal_state(boxes, goals):
            return reconstruct_path(came_from, cur_key)

        for (nstate, move) in neighbors(cur):
            nplayer, nboxes, _, _, _ = nstate
            nkey = state_key(nplayer, nboxes)
            tentative_g = g + 1
            if tentative_g < g_score.get(nkey, float('inf')):
                came_from[nkey] = (cur_key, move)
                g_score[nkey] = tentative_g
                h = heuristic(nboxes, goals)
                fscore = tentative_g + h
                heapq.heappush(open_heap, (fscore, tentative_g, uid, nstate))
                uid += 1
    return None

def solve_and_print(map_name, method='A*', printout=True) -> str:
    """Solve the map using A* or BFS method

    Args:
        map_name (_type_): Name of map only (without full path)
        method (str, optional): _description_. Defaults to 'A*'.
        printout (bool, optional): Decide if we want to printout extra information from this function

    Returns:
        str: A string of moves
    """
    matrix = img2matrix(map_name)
    mapdata = load_map(map_name)
    if printout: print(f"Loaded map '{map_name}': rows={mapdata['rows']} cols={mapdata['cols']}")
    if printout: print(f"Player at {mapdata['player']}, boxes={list(mapdata['boxes'])}, goals={list(mapdata['goals'])}")
    start_time = time.time()
    if method == 'bfs':
        result = bfs_solve(mapdata)
    else:
        result = a_star_solve(mapdata)
    elapsed = time.time() - start_time
    if result is None:
        if printout: print(f"No solution found (method={method}). Time: {elapsed:.2f}s")
    else:
        if printout: print(f"SOLUTION ({method}) move string: {result}")
        if printout: print(f"Length: {len(result)} moves. Time: {elapsed:.2f}s")
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python solve.py <map_name> [--bfs]")
        print("Example: python solve.py map_3")
        sys.exit(1)

    file_name = sys.argv[1]
    method = 'astar'
    if len(sys.argv) >= 3 and sys.argv[2].lower() == '--bfs':
        method = 'bfs'

    solve_and_print(file_name, method=method)
