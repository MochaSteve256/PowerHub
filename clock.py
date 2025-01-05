import math
from datetime import datetime

# Define your LED matrix control functions (replace with your library)
def draw_dot(x, y, color):
    print(f"A {color} dot at ({x}, {y})")  # Replace with actual drawing logic

def clear_matrix():
    print("Clearing matrix")  # Replace with actual clearing logic

def display():
    print("Updating display")  # Replace with actual display update logic

# Map angles to edge coordinates
def angle_to_edge_coords(angle):
    """
    Map an angle to the nearest edge coordinate on an 8x8 LED matrix.
    Top-left corner is (0,0), center is (3,3).
    """
    center_x, center_y = 3, 3  # Center of 8x8 matrix (integer coordinates)

    # Calculate raw coordinates
    x = center_x + 5 * math.cos(math.radians(angle))
    y = center_y - 5 * math.sin(math.radians(angle))  # Y-axis inverted

    # Clamp to nearest edge pixel
    edge_x = max(0, min(7, round(x)))
    edge_y = max(0, min(7, round(y)))

    return edge_x, edge_y

# Calculate positions for hour and minute hands
def update_clock(hour, minute):
    # Calculate angles (0° points right, 90° up, 180° left, 270° down)
    hour_angle = 90 - (hour % 12 * 30 + minute * 0.5)  # 30° per hour, 0.5° per minute
    minute_angle = 90 - (minute * 6)  # 6° per minute

    # Calculate LED edge positions
    hour_x, hour_y = angle_to_edge_coords(hour_angle)
    minute_x, minute_y = angle_to_edge_coords(minute_angle)

    # Clear matrix
    clear_matrix()

    # Draw hour and minute dots at the edge
    draw_dot(hour_x, hour_y, color='red')
    draw_dot(minute_x, minute_y, color='blue')

    # Update display
    display()

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
