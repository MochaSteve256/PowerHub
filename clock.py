import copy
import math
from datetime import datetime

import u64images

hour_color = (128, 0, 0)
minute_color = (0, 128, 0)
both_color = (128, 128, 0)

# Define your LED matrix control functions (replace with your library)
def draw_dot(mtx,x, y, color):
    print(f"A {color} dot at ({x}, {y})")  # Replace with actual drawing logic
    mtx[y][x] = color

# Map angles to edge coordinates
def angle_to_edge_coords(angle, small_clip):
    """
    Map an angle to the nearest edge coordinate on an 8x8 LED matrix.
    Top-left corner is (0,0), center is (3,3).
    """
    center_x, center_y = 3, 3  # Center of 8x8 matrix (integer coordinates)

    # Calculate raw coordinates
    x = center_x + 5 * math.cos(math.radians(angle))
    y = center_y - 5 * math.sin(math.radians(angle))  # Y-axis inverted

    # Clamp to nearest edge pixel
    if not small_clip:
        edge_x = max(0, min(7, round(x)))
        edge_y = max(0, min(6, round(y)))
    else:
        edge_x = max(1, min(6, round(x)))
        edge_y = max(1, min(5, round(y)))

    return edge_x, edge_y

# Calculate positions for hour and minute hands
def update_clock(hour, minute):
    # Calculate angles (0° points right, 90° up, 180° left, 270° down)
    hour_angle = 90 - (hour % 12 * 30 + minute * 0.5)  # 30° per hour, 0.5° per minute
    minute_angle = 90 - (minute * 6)  # 6° per minute

    # Calculate LED edge positions
    hour_x, hour_y = angle_to_edge_coords(hour_angle, False)
    minute_x, minute_y = angle_to_edge_coords(minute_angle, False)
    s_minute_x, s_minute_y = angle_to_edge_coords(minute_angle, True)
    
    # Matrix initialization
    matrix = copy.deepcopy(u64images.clock_face)
    

    # Draw hour and minute dots at the edge
    draw_dot(matrix, minute_x, minute_y, color=minute_color)
    draw_dot(matrix, s_minute_x, s_minute_y, color=minute_color)
    if minute_x == hour_x and minute_y == hour_y:
        draw_dot(matrix, minute_x, minute_y, color=both_color)
    else:
        draw_dot(matrix, hour_x, hour_y, color=hour_color)
    
    return matrix

def gen_matrix():
    now = datetime.now()
    return update_clock(now.hour, now.minute)


if __name__ == "__main__":
    # Test the clock at various times
    test_times = [
        (3, 0),  # 3:00
        (6, 0),  # 6:00
        (9, 0),  # 9:00
        (12, 0), # 12:00
        (1, 15), # 1:15
        (4, 45), # 4:45
        (10, 30) # 10:30
    ]

    for hour, minute in test_times:
        print(f"Testing time: {hour:02d}:{minute:02d}")
        update_clock(hour, minute)
