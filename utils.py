import numpy as np


# Colors
RED = (255, 0, 0)
GREEN = (0, 0, 255)
YELLOW = (255, 255, 0)


def filter_minimum_distance(point_list: list, w: int, h: int, min_distance: int) -> list:
    filtered_locations = []
    # Create a list to store the (x, y) coordinates of the centers of approved matches
    approved_centers = []

    for score, pt_y, pt_x in point_list:
        current_center_x = pt_x + w // 2
        current_center_y = pt_y + h // 2
        
        is_too_close = False
        for center_x, center_y in approved_centers:
            # Calculate the Euclidean distance between the current center and an approved center
            distance = np.sqrt((current_center_x - center_x)**2 + (current_center_y - center_y)**2)
            
            if distance < min_distance:
                is_too_close = True
                break
                
        if not is_too_close:
            # This is a new, distinct match. Approve it.
            filtered_locations.append((pt_x, pt_y))
            approved_centers.append((current_center_x, current_center_y))
            
    return approved_centers