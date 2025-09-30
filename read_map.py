import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
from utils import filter_minimum_distance
from utils import RED, GREEN, YELLOW


EMPTY = 0
WALL = 1
PLAYER = 2
RUBY = 3
DESTINATION = 4


def convert_image_to_map(image_path: str) -> list:
    # Map tile position
    tile_loc = {
        "wall": [],
        "ruby": [],
        "destination": [],
        "player": [],
    }
    
    img = cv.imread(image_path, cv.IMREAD_GRAYSCALE)
    
    wall_template = cv.imread('assets/wall_center.png', cv.IMREAD_GRAYSCALE)
    TILE_SCALE = 1
    if img.shape[0] <= 600 or img.shape[1] <= 600:
        TILE_SCALE = 0.7
    wall_template = cv.resize(wall_template, None, fx=TILE_SCALE, fy=TILE_SCALE, interpolation=cv.INTER_AREA)
    wall_w, wall_h = wall_template.shape[::-1]

    METHOD = cv.TM_CCOEFF_NORMED
    THRESHOLD = 0.75
    MIN_DISTANCE = 10

    # Apply template Matching
    res = cv.matchTemplate(img, wall_template, METHOD)
    wall = np.where(res >= THRESHOLD)

    # Filter out duplicate point, too close to each other
    points_with_scores = []
    for pt_y, pt_x in zip(*wall):
        score = res[pt_y, pt_x]
        points_with_scores.append((score, pt_y, pt_x))
    points_with_scores.sort(key=lambda x: x[0], reverse=True)

    wall_filtered = filter_minimum_distance(points_with_scores, wall_w, wall_h, MIN_DISTANCE)
    tile_loc['wall'] = sorted(wall_filtered, key=lambda item: (item[0], item[1]))
    
    # Create a tile map
    loc_x = [p[0] for p in tile_loc['wall']]
    loc_y = [p[1] for p in tile_loc['wall']]
    unique_x = []
    for x in sorted(list(set(loc_x))):
        if not unique_x:
            unique_x.append(x)
        elif abs(x - unique_x[-1]) > 5:
            unique_x.append(x)
    unique_y = []
    for y in sorted(list(set(loc_y))):
        if not unique_y:
            unique_y.append(y)
        elif abs(y - unique_y[-1]) > 5:
            unique_y.append(y)
    map_size = (len(unique_x), len(unique_y))
    print(f'Map size: {map_size[0]}x{map_size[1]}')
    
    # Calculate coordinate of each square
    # Find square size = (right_point - left_point) // (square_count - 1)
    square_width = (max(unique_x) - min(unique_x)) // (map_size[0] - 1)
    top_corner = (min(unique_x) - square_width//2, min(unique_y) - square_width//2)
    
    # Draw result on a copied image
    img_display = cv.imread(image_path, cv.IMREAD_COLOR)
    img_display = cv.cvtColor(img_display, cv.COLOR_BGR2RGB)
    wall_count = 0
    for wall_center in tile_loc['wall']:
        top_left = (wall_center[0] - wall_w//2, wall_center[1] - wall_h//2)
        bottom_right = (wall_center[0] + wall_w//2, wall_center[1] + wall_h//2)
        cv.rectangle(img_display, top_left, bottom_right, (255, 0, 0), 2)
        cv.circle(img_display, wall_center, 1, (255, 0, 0), 2)
        wall_count += 1
    print(f'Wall count: {wall_count}')
    
    # Draw grid map
    img_grid = cv.imread(image_path, cv.IMREAD_COLOR)
    img_grid = cv.cvtColor(img_grid, cv.COLOR_BGR2RGB)
    # Draw vertical lines
    for col in range(0, map_size[0] + 1):
        top_point = (top_corner[0] + col*square_width, top_corner[1])
        bottom_point = (top_corner[0] + col*square_width, top_corner[1] + map_size[1]*square_width)
        cv.line(img_grid, top_point, bottom_point, (0, 0, 255), 1)
    # Draw horizontal lines
    for row in range(0, map_size[1] + 1):
        left_point = (top_corner[0], top_corner[1] + row*square_width)
        right_point = (top_corner[0] + map_size[0]*square_width, top_corner[1]+ row*square_width)
        cv.line(img_grid, left_point, right_point, (0, 0, 255), 1)
        
    # ====================== FIND RUBY AND DESTINATION ================
    img_rgb = cv.imread(image_path, cv.IMREAD_COLOR)
    PATHS = {
        "ruby": "assets/ruby.png",
        "destination": "assets/destination.png",
        "player": "assets/player.png"
    }
    for row in range(0, map_size[1]):
        for col in range(0, map_size[0]):
            top_left = (top_corner[0] + col*square_width, top_corner[1] + row*square_width)
            bottom_right = (top_left[0] + square_width, top_left[1] + square_width)
            current_tile = img_rgb[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
            
            for tile_type, tile_path in PATHS.items():
                tile_image = cv.imread(tile_path, cv.IMREAD_COLOR)
                tile_image = cv.resize(tile_image, None, fx=TILE_SCALE, fy=TILE_SCALE, interpolation=cv.INTER_AREA)
                print(f"current_tile size: {current_tile.shape}")
                print(f"tile_image size: {tile_image.shape}")
                result = cv.matchTemplate(current_tile, tile_image, METHOD)
                min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
                if max_val >= 0.7:
                    center = ((bottom_right[0] + top_left[0]) // 2,
                              (bottom_right[1] + top_left[1]) // 2,)
                    tile_loc[tile_type].append(center)
                    if tile_type == "ruby":
                        color = RED
                    elif tile_type == "player":
                        color = YELLOW
                    else:
                        color = GREEN
                    cv.rectangle(img_grid,
                                 (top_left[0] + 2, top_left[1] + 2),
                                 (bottom_right[0] - 2, bottom_right[1] - 2),
                                 color, 2)
                    break

    # ====================== DRAW RESULT ==============================
    # Display the results
    plt.figure(figsize=(15, 5))

    plt.subplot(131), plt.imshow(res, cmap='gray')
    plt.title('Matching Result Map'), plt.xticks([]), plt.yticks([])

    plt.subplot(132), plt.imshow(img_display, cmap='gray')
    plt.title(f'Detected Points (Threshold: {THRESHOLD})'), plt.xticks([]), plt.yticks([])
    
    plt.subplot(133), plt.imshow(img_grid, cmap='gray')
    plt.title(f'Grid Map'), plt.xticks([]), plt.yticks([])

    plt.suptitle('Finding All Matches')

    plt.savefig(f"results/{image_path.split('/')[-1]}")
    plt.show()
    
    # Get result as a 2D array
    result = np.zeros(map_size[::-1])
    for tile_name, tile_center_list in tile_loc.items():
        for tile_center in tile_center_list:
            x = (tile_center[1] - top_corner[1]) // square_width
            y = (tile_center[0] - top_corner[0]) // square_width
            print(f'Current tile: {tile_name}, center: {tile_center}')
            if tile_name == 'wall':
                result[x][y] = WALL
            elif tile_name == 'ruby':
                result[x][y] = RUBY
            elif tile_name == 'destination':
                result[x][y] = DESTINATION
            elif tile_name == 'player':
                result[x][y] = PLAYER
        
    print(result)
    return result
    

if __name__ == "__main__":
    map = convert_image_to_map('maps/map_20.png')