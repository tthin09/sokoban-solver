#!/usr/bin/env python3
"""
Cách dùng:
    python solve.py map_3           # chạy A* trên tile_maps/map_3.csv
    python solve.py map_3 --bfs     # chạy BFS

Đầu vào: file CSV trong thư mục tile_maps
    0 = empty
    1 = wall
    2 = player
    3 = box
    4 = goal
    5 = box on goal

Output:
    In chuỗi di chuyển (U,D,L,R) nếu tìm được, đồng thời in thông tin thống kê.
"""

import sys
import time
import pandas as pd
import itertools
from collections import deque
import heapq
from img_to_matrix import img2matrix


# Các bước di chuyển của người chơi: Up, Down, Left, Right
MOVES = {
    'U': (-1, 0),
    'D': (1, 0),
    'L': (0, -1),
    'R': (0, 1)
}

# --- Hàm đọc bản đồ ---
def load_map(file_name):
    """
    Đọc CSV từ tile_maps/<file_name>.csv và trả về dict mapdata.
    Trả về:
        {
            'rows': int, 'cols': int,
            'walls': set((r,c)), 'goals': set((r,c)),
            'boxes': frozenset((r,c)), 'player': (r,c)
        }
    """
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
                boxes.add((r, c))
                goals.add((r, c))
            elif val == 7:
                goals.add((r, c))
                player = (r, c)
            # 0 -> empty

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

# --- Kiểm tra trạng thái đích ---
def is_goal_state(boxes, goals):
    """
    Kiểm tra tất cả box có nằm trên goal hay không.
    """
    return set(boxes) <= set(goals)

# --- Key canonical cho trạng thái ---
def state_key(player, boxes):
    """
    Tạo khóa (canonical) cho visited / came_from.
    Sắp thứ tự boxes để khóa ổn định (do frozenset không có thứ tự).
    Khi search theo "step-by-step player moves", trạng thái chứa vị trí player.
    """
    return (player, tuple(sorted(boxes)))

# --- Hàm dò và phát sinh neighbor ---
def neighbors(state, goals):
    """
    Dựa trên state = (player_pos, boxes_frozenset, walls, rows, cols)
    yield ((next_player, next_boxes, walls, rows, cols), move_char)
    """
    player, boxes, walls, rows, cols = state
    boxes_set = set(boxes)

    def is_deadlock(box, boxes_new, walls):
        """
        Kiểm tra deadlock cơ bản: box rơi vào góc kín (2 cạnh là tường/wall)
        và không phải là goal -> deadlock.
        Đây là dạng deadlock rất đơn giản để prune nhanh, không đầy đủ cho mọi trường hợp.
        """
        r, c = box
        if (r, c) in goals:
            return False
        # box nằm góc bởi hai wall theo hàng hoặc theo cột
        if ((r-1, c) in walls or (r+1, c) in walls) and ((r, c-1) in walls or (r, c+1) in walls):
            return True
        return False

    for m, (dr, dc) in MOVES.items():
        nr, nc = player[0] + dr, player[1] + dc
        # kiểm tra phạm vi
        if not (0 <= nr < rows and 0 <= nc < cols):
            continue
        if (nr, nc) in walls:
            continue

        if (nr, nc) in boxes_set:
            # người đẩy box; kiểm tra ô sau box có trống không
            br, bc = nr + dr, nc + dc
            if not (0 <= br < rows and 0 <= bc < cols):
                continue
            if (br, bc) in walls or (br, bc) in boxes_set:
                continue

            # thực hiện push
            new_boxes = set(boxes_set)
            new_boxes.remove((nr, nc))
            new_boxes.add((br, bc))

            # prune nếu deadlock đơn giản xảy ra
            if any(is_deadlock(b, new_boxes, walls) for b in new_boxes):
                continue

            yield (((nr, nc), frozenset(new_boxes), walls, rows, cols), m)
        else:
            # di chuyển người chơi vào ô trống
            yield (((nr, nc), boxes, walls, rows, cols), m)

# --- Thuật toán BFS ---
def bfs_solve(mapdata, max_nodes=500000):
    """
    Breadth-First Search (BFS) theo bước di chuyển người chơi.
    - Dùng queue FIFO.
    - Lưu came_from để reconstruct path (mỗi state là (player, boxes)).
    - Trả về (move_string | None, nodes_expanded).
    Phức tạp thời gian/bộ nhớ: O(b^d) (rất lớn), chỉ dùng được cho các bản đồ nhỏ.
    """
    rows = mapdata['rows']; cols = mapdata['cols']
    walls = mapdata['walls']; goals = mapdata['goals']
    start_player = mapdata['player']; start_boxes = mapdata['boxes']

    start_state = (start_player, start_boxes, walls, rows, cols)
    start_key = state_key(start_player, start_boxes)

    if is_goal_state(start_boxes, goals):
        return "" , 0

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
            # dừng sớm nếu quá nhiều node
            return None, expanded

        for (nstate, move) in neighbors(cur, goals):
            nplayer, nboxes, _, _, _ = nstate
            nkey = state_key(nplayer, nboxes)
            if nkey in came_from:
                continue
            came_from[nkey] = (cur_key, move)
            if is_goal_state(nboxes, goals):
                return reconstruct_path(came_from, nkey), expanded
            q.append(nstate)
    return None, expanded

# --- Heuristic cho A* ---
def manhattan(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def heuristic(boxes, goals):
    """
    Heuristic: minimal sum of Manhattan distances từ boxes tới một tập goals (assignment).
    - Nếu số boxes nhỏ (thường bằng), ta enumerate permutations mapping boxes->goals.
    - Đảm bảo heuristic admissible (không overestimate) -> A* tìm đường ngắn nhất theo số bước.
    Ghi chú: tính toán permutations đắt khi số box lớn; tuy nhiên Sokoban thường có số box nhỏ (<=4).
    """
    boxes_list = list(boxes)
    goals_list = list(goals)
    nb = len(boxes_list)
    ng = len(goals_list)
    if nb == 0:
        return 0

    best = float('inf')
    if nb <= ng:
        # các hoán vị các goals chọn nb vị trí (nếu ng==nb thì đơn giản là permute)
        for chosen in itertools.permutations(goals_list, nb):
            s = 0
            for i in range(nb):
                s += manhattan(boxes_list[i], chosen[i])
                if s >= best:
                    break
            if s < best:
                best = s
    else:
        # trường hợp hiếm: nhiều box hơn goals -> gán mỗi box tới goal gần nhất (admissible but weak)
        s = 0
        for b in boxes_list:
            s += min(manhattan(b, g) for g in goals_list)
        best = s
    return best

# --- Thuật toán A* ---
def a_star_solve(mapdata, max_nodes=500000):
    """
    A* search trên không gian trạng thái (player position + box positions).
    - Mỗi bước tăng g by 1 (một bước di chuyển của player).
    - f = g + h, với h từ hàm heuristic ở trên.
    - Trả về (move_string | None, nodes_expanded).
    Search theo từng bước player (không push-only) nên chi phí lớn, nhưng code đơn giản.
    """
    rows = mapdata['rows']; cols = mapdata['cols']
    walls = mapdata['walls']; goals = mapdata['goals']
    start_player = mapdata['player']; start_boxes = mapdata['boxes']

    start_state = (start_player, start_boxes, walls, rows, cols)
    start_key = state_key(start_player, start_boxes)

    if is_goal_state(start_boxes, goals):
        return "", 0

    open_heap = []
    g_score = { start_key: 0 }
    h0 = heuristic(start_boxes, goals)
    # heap entry: (f_score, g_score, uid, state)
    heapq.heappush(open_heap, (h0, 0, 0, start_state))
    came_from = { start_key: None }

    expanded = 0
    uid = 1

    while open_heap:
        f, g, _, cur = heapq.heappop(open_heap)
        player, boxes, _, _, _ = cur
        cur_key = state_key(player, boxes)

        # nếu đã có đường tốt hơn đến cur_key thì bỏ
        if g_score.get(cur_key, float('inf')) < g:
            continue

        expanded += 1
        if expanded > max_nodes:
            return None, expanded

        if is_goal_state(boxes, goals):
            return reconstruct_path(came_from, cur_key), expanded

        for (nstate, move) in neighbors(cur, goals):
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

    return None, expanded

# --- Hỗ trợ reconstruct path ---
def reconstruct_path(came_from, end_key):
    """
    Lần ngược came_from để lấy chuỗi move (U/D/L/R).
    came_from: dict state_key -> (prev_state_key, move)
    """
    moves = []
    cur = end_key
    while cur in came_from and came_from[cur] is not None:
        prev, move = came_from[cur]
        moves.append(move)
        cur = prev
    return ''.join(reversed(moves))

# --- Hàm wrapper để chạy và in thông tin ---
def solve_and_print(map_name, method='A*', printout=True):
    """
    Hàm chính gọi load_map, chạy BFS hoặc A*, in kết quả.
    Trả về (result_move_string_or_None, nodes_expanded)
    """
    # nếu bạn có img2matrix và muốn dùng, gọi nó (không bắt buộc)
    _ = img2matrix(map_name)

    mapdata = load_map(map_name)
    if printout:
        print(f"Loaded map '{map_name}': rows={mapdata['rows']} cols={mapdata['cols']}")
        print(f"Player at {mapdata['player']}, boxes={list(mapdata['boxes'])}, goals={list(mapdata['goals'])}")

    start_time = time.time()
    if method == 'bfs':
        result, expanded = bfs_solve(mapdata)
    else:
        result, expanded = a_star_solve(mapdata)
    elapsed = time.time() - start_time

    if result is None:
        if printout:
            print(f"No solution found (method={method}). Time: {elapsed:.3f}s Nodes Expanded: {expanded}")
    else:
        if printout:
            print(f"SOLUTION ({method}) move string: {result}")
            print(f"Length: {len(result)} moves. Time: {elapsed:.3f}s Nodes Expanded: {expanded}")

    return result, expanded

# --- CLI handling ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python solve.py <map_name> [--bfs]")
        print("Example: python solve.py map_3")
        sys.exit(1)

    file_name = sys.argv[1]
    method = 'A*'
    if len(sys.argv) >= 3 and sys.argv[2].lower() in ('--bfs', 'bfs'):
        method = 'bfs'

    # Gọi hàm
    solve_and_print(file_name, method=method)
