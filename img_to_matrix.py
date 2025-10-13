import cv2 as cv
import numpy as np
import pandas as pd

# empty = 0
# wall = 1
# human = 2
# ruby = 3
# des = 4
# ruby in des = 5

RED = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 102)
BLUE = (255,0,0)
ORANGE = (255,0,255)

def img2matrix(img_name):
    img_path = f'maps/{img_name}.png'
    img = cv.imread(img_path)
    assert img is not None, "file could not be loaded"
    img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    W, H = img_gray.shape[::-1]
    MAX_SIZE = max(W, H)

    wall = cv.imread('assets/wall.png', cv.IMREAD_GRAYSCALE)
    assert wall is not None, "file could not be loaded"
    w , h = wall.shape[::-1]

    # find the cell_size
    grid_size = 6
    max_fit = 0
    for i in range(6, 12):
        wall_resized = cv.resize(wall, (MAX_SIZE//i, MAX_SIZE//i), interpolation=cv.INTER_AREA)
        res = cv.matchTemplate(img_gray, wall_resized, cv.TM_CCOEFF_NORMED)
        threshold = 0.75
        loc = np.where(res >= threshold)
        if len(loc[0]) > max_fit:
            max_fit = len(loc[0])
            grid_size = i

    print(f"Best size: {grid_size}, with {max_fit} matches")

    matrix = np.zeros((MAX_SIZE//W * grid_size, MAX_SIZE//H * grid_size), dtype=np.uint8)

    cell_size = MAX_SIZE // grid_size

    # find the wal
    wall = cv.resize(wall, (cell_size, cell_size), interpolation=cv.INTER_AREA)
    res = cv.matchTemplate(img_gray, wall, cv.TM_CCOEFF_NORMED)
    threshold = 0.75
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):
        cv.rectangle(img, pt, (pt[0] + cell_size, pt[1] + cell_size), BLUE, 2)
        matrix[round(pt[1]/cell_size), round(pt[0]/cell_size)] = 1

    #find the human
    img_rgb = cv.imread(img_path, cv.IMREAD_COLOR)
    PATHS = {
        "ruby": "assets/ruby.png",
        "destination": "assets/destination.png",
        "player": "assets/player.png",
        "ruby_in_des": "assets/ruby_in_des.png"
    }
    for typ, path in PATHS.items():
        tile_img = cv.imread(path, cv.IMREAD_COLOR)
        tile_img = cv.resize(tile_img, (cell_size, cell_size), interpolation=cv.INTER_AREA)
        res = cv.matchTemplate(img_rgb, tile_img, cv.TM_CCOEFF_NORMED)
        new_threshold = 0.8
        loc = np.where(res >= new_threshold)
        if typ == "ruby":
            color = RED 
            layer = 3
        elif typ == "destination":
            color = GREEN
            layer = 4
        elif typ == "player":
            color = YELLOW
            layer = 2
        else: 
            color = ORANGE
            layer = 5
        
        for pt in zip(*loc[::-1]):
            cv.rectangle(img, pt, (pt[0] + cell_size, pt[1] + cell_size), color, 2)
            matrix[round(pt[1]/cell_size), round(pt[0]/cell_size)] = layer
        
    # save img
    cv.imwrite(f'results/img_to_matrix/{img_name}.png', img)
    
    # save dataframe
    df = pd.DataFrame(matrix)
    df.to_csv(f'tile_maps/{img_name}.csv', header=None, index=None)
    
    return matrix