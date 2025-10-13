import pandas as pd
import numpy as np

file_name = "map_3"
df = pd.read_csv(f'tile_maps/{file_name}.csv',header=None, index_col=None )
nf = df.to_numpy()

des_pos = np.argwhere((nf == 4) | (nf == 5)).tolist()
ruby_pos = np.argwhere((nf == 3) | (nf == 5)).tolist()
player_pos = np.argwhere(nf == 2).tolist()[0]
result = ""

print(f'des:',des_pos)
print(f'ruby',ruby_pos)
print('player', player_pos)

nf = np.where((nf != 0)&(nf != 1)&(nf != 3), 0, nf)
df = pd.DataFrame(nf)

des_ = []
for des in des_pos:
    des_.append([des[0],des[1]])

def can_move(matrix, x, y):
    vertical = matrix[x - 1][y] == matrix[x + 1][ y] == 0
    horizontal = matrix[x][y-1] == matrix[x][y+1] == 0
    return vertical, horizontal

def bfs(queue, road, visited, destination):
    while True:
        x,y = queue.pop(0)
        vertical, horizontal = can_move(nf,x, y)
        left = [x,y-1]
        right = [x, y+1]
        up = [x-1, y]
        bottom = [x+1,y]
        if horizontal:
            if left not in visited:
                visited.append(left)
                road[x,y-1] = [x,y]
                queue.append(left)
            if right not in visited:
                road[x,y+1] = [x,y]
                visited.append(right)
                queue.append(right)
        if vertical:
            if up not in visited: 
                road[x-1,y] = [x,y]
                visited.append(up)
                queue.append(up)
            if bottom not in visited: 
                road[x+1,y] = [x,y]
                visited.append(bottom)
                queue.append(bottom)
        if [x,y] == destination:
            break
        if len(queue) == 0:
            return []
    return road

def player_bfs(queue, road, visited, destination):
    while True:
        x, y = queue.pop(0)
        left = [x,y-1]
        right = [x, y+1]
        up = [x-1, y]
        bottom = [x+1,y]
        
        if left not in visited and nf[x][y-1] == 0:
            visited.append(left)
            road[x,y-1] = [x,y]
            queue.append(left)
        if right not in visited and nf[x][y+1] == 0:
            road[x,y+1] = [x,y]
            visited.append(right)
            queue.append(right)
        if up not in visited and nf[x-1][y] == 0:
            road[x-1,y] = [x,y]
            visited.append(up)
            queue.append(up)
        if bottom not in visited and nf[x+1][y] == 0:
            road[x+1,y] = [x,y]
            visited.append(bottom)
            queue.append(bottom)
        if [x,y] == destination:
            break
        if len(queue) == 0:
            return []
    return road

def player_pos_to_push(move, next_move):
    a = move[0]
    b = move[1]
    x = next_move[0]
    y = next_move[1]
    if a == x:
        if b + 1 == y:
            return [a, b -1], "right"
        else:
            return [a, b+ 1], "left"
    else:
        if a + 1 == x:
            return [a-1, b], "down"
        else: 
            return [a+1, b], "up"

def update_matrix(matrix, ruby_des, act):
    x, y = ruby_des
    if act == "up":
        matrix[x-1][y] = 3
        matrix[x][y] = 0
    elif act == "down":
        matrix[x+1][y] = 3
        matrix[x][y] = 0
    elif act == "left":
        matrix[x][y-1] = 3
        matrix[x][y] = 0
    else:
        matrix[x][y+1] = 3
        matrix[x][y] = 0
    return matrix

def move_to_string(move, next_move):
    a = move[0]
    b = move[1]
    x = next_move[0]
    y = next_move[1]
    if a == x:
        if b + 1 == y:
            return "right"
        else:
            return "left"
    else:
        if a - 1 == x:
            return "up"
        else: 
            return "down"

def find_best_road(des, dic):
    if dic == []:
        return None
    road = []
    road.append([des[0],des[1]])
    prev = dic[des[0],des[1]]
    while prev != []:
        road.append(prev)
        prev = dic[prev[0],prev[1]]
    road = road[::-1]
    return road

def convert_road_to_string(road, player_p):
    s = ""
    player_input_pos = player_p
    while len(road) > 1:
        curr = road[0]
        next = road[1]
        road.pop(0)
        prev, order = player_pos_to_push(curr, next)
        x ,y = player_p
        q = [[x,y]]
        r = {}
        r[x,y] = []
        v = [[x,y]]
        dic_road = player_bfs(q, r, v, prev)
        player_road = find_best_road(prev, dic_road)
        if player_road is None:
            print("No road for player")
            return None, player_input_pos
        player_p = curr
        while len(player_road) > 1:
            curr_p = player_road[0]
            next_p = player_road[1]
            player_road.pop(0)
            order_p = move_to_string(curr_p, next_p)
            s += order_p + ","
        s += order + ","
        update_matrix(nf, curr, order)
    print(s)
    return s, player_p


for ruby in ruby_pos:
    x,y = ruby
    queue = [[x,y]]
    par = {}
    par[x,y] = []
    visited = [[x,y]]
    
    for des in des_:
        par = bfs(queue,par,visited, des)
        if par == []:
            continue
        
        if par.get((des[0],des[1])) is not None:
            des_.remove([des[0],des[1]])
            
            road = find_best_road(des,par)
            if road is not None:
                continue
            break
            
    print(f'road from {road[0]} to {road[-1]}: {road}' )
    s, player_pos = convert_road_to_string(road, player_pos)
    if s is None:
        print("No road for ruby")
        continue
    result += s
result = result[:-1]
print(result)