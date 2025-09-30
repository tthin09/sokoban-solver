import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
from utils import filter_minimum_distance
from utils import RED, GREEN, BLACK, YELLOW, HSV_RANGE


def convert_image_to_map(image_path: str, tile_method="") -> list:
    img = cv.imread(image_path, cv.IMREAD_GRAYSCALE)
    wall_template = cv.imread('assets/wall_center.png', cv.IMREAD_GRAYSCALE)
    w, h = wall_template.shape[::-1]

    TEMPLATE = 'TM_CCOEFF_NORMED'
    METHOD = getattr(cv, TEMPLATE)
    THRESHOLD = 0.85
    MIN_DISTANCE = 40

    # Apply template Matching
    res = cv.matchTemplate(img, wall_template, METHOD)
    loc = np.where(res >= THRESHOLD)

    # Filter out duplicate point, too close to each other
    points_with_scores = []
    for pt_y, pt_x in zip(*loc):
        score = res[pt_y, pt_x]
        points_with_scores.append((score, pt_y, pt_x))
    points_with_scores.sort(key=lambda x: x[0], reverse=True)

    loc_filtered = filter_minimum_distance(points_with_scores, w, h, MIN_DISTANCE)
    loc_filtered = sorted(loc_filtered, key=lambda item: (item[0], item[1]))
    
    # Create a tile map
    loc_x = [p[0] for p in loc_filtered]
    loc_y = [p[1] for p in loc_filtered]
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
    for center in loc_filtered: # The loc is in (y, x) format, we need (x, y)
        top_left = (center[0] - w//2, center[1] - h//2)
        bottom_right = (center[0] + w//2, center[1] + h//2)
        cv.rectangle(img_display, top_left, bottom_right, (255, 0, 0), 2)
        cv.circle(img_display, center, 1, (255, 0, 0), 2)
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
    img_hsv = cv.imread(image_path)
    img_hsv = cv.cvtColor(img_hsv, cv.COLOR_BGR2HSV)
    PATHS = {
        "ruby": "assets/ruby.png",
        "destination": "assets/destination.png",
        "player": "assets/player.png"
    }
    for row in range(0, map_size[1]):
        for col in range(0, map_size[0]):
            top_left = (top_corner[0] + col*square_width, top_corner[1] + row*square_width)
            bottom_right = (top_left[0] + square_width, top_left[1] + square_width)
            current_tile = img[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
            
            for tile_type, tile_path in PATHS.items():
                tile_image = cv.imread(tile_path, cv.IMREAD_GRAYSCALE)
                print(f"current_tile size: {current_tile.shape}")
                print(f"tile_image size: {tile_image.shape}")
                result = cv.matchTemplate(current_tile, tile_image, METHOD)
                min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
                if max_val >= 0.8:
                    if tile_type == "ruby":
                        color = RED
                    elif tile_type == "void":
                        color = YELLOW
                    elif tile_type == "player":
                        color = BLACK
                    else:
                        color = GREEN
                    cv.rectangle(img_grid, top_left, bottom_right, color, 4)
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

    plt.show()

    # Save all wall coordinate found in an image
    save_all_point_coordinate_in_image(loc_filtered)
    
    
def save_all_point_coordinate_in_image(loc_filtered) -> None:
    loc_x = [p[0] for p in loc_filtered]
    loc_y = [p[1] for p in loc_filtered]
    
    # Save all points coordinate
    plt.figure(figsize=(8, 6))

    plt.scatter(loc_x, loc_y, color='red', marker='o', s=100, zorder=5)

    for (x, y) in loc_filtered:
        # Format the coordinate text
        label = f'({x}, {y})'
        
        # Add annotation slightly offset from the point
        plt.annotate(
            label,              # The text to display
            (x, y),             # The point to annotate (x, y)
            textcoords="offset points", # How to position the text
            xytext=(5, -10),    # Offset in pixels (5 right, 10 down)
            ha='center',        # Horizontal alignment
            fontsize=10,
            color='blue'
        )

    # Set plot titles and labels
    plt.title('Plotting Points with Coordinates')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.grid(True, linestyle='--', alpha=0.6)

    # Ensure axes span the range of the data comfortably
    plt.xlim(min(loc_x) - 1, max(loc_x) + 1)
    plt.ylim(min(loc_y) - 1, max(loc_y) + 1)
    
    plt.gca().invert_yaxis()

    # Save the plot
    plt.savefig('results/scatter_plot_with_coordinates.png')
    plt.close()
    

if __name__ == "__main__":
    # methods = ['TM_CCOEFF', 'TM_CCOEFF_NORMED', 'TM_CCORR',
    #         'TM_CCORR_NORMED', 'TM_SQDIFF', 'TM_SQDIFF_NORMED']
    # for meth in methods:
    #     tile_method = getattr(cv, meth)
    convert_image_to_map('maps/map_3.png')