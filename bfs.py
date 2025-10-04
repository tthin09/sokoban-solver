import pandas as pd
import numpy as np

file_name = "map_18"
df = pd.read_csv(f'tile_maps/{file_name}.csv',header=None, index_col=None )
nf = df.to_numpy()

des_pos = np.argwhere((nf == 4) | (nf == 5))
ruby_pos = np.argwhere((nf == 3) | (nf == 5))
player_pos = np.argwhere(nf == 2)

print(des_pos)
print(ruby_pos)

nf = np.where((nf != 0)&(nf != 1), 0, nf)
df = pd.DataFrame(nf)

des_ = []
for des in des_pos:
    des_.append([des[0],des[1]])

def can_move(matrix, x, y):
    vertical = matrix[x - 1][y] == matrix[x + 1][ y] == 0
    horizontal = matrix[x][y-1] == matrix[x][y+1] == 0
    return vertical, horizontal

def bfs(queue, road, visited):
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
        if any(np.array_equal(row, [x,y]) for row in des_):
            break
        if len(queue) == 0:
            return []
    return road



for ruby in ruby_pos:
    x,y = ruby
    queue = [[x,y]]
    par = {}
    par[x,y] = []
    visited = [[x,y]]
    par = bfs(queue,par,visited)
    
    road = []
    for des in des_:
        if par.get((des[0],des[1])) is not None:
            des_.remove([des[0],des[1]])
            
            road.append([des[0],des[1]])
            prev = par[des[0],des[1]]
            while prev != []:
                road.append(prev)
                prev = par[prev[0],prev[1]]
            break
    
    road = road[::-1]
    print(f'road from {road[0]} to {road[-1]}: {road}' )