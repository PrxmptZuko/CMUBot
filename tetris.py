import random
import time
import threading

# Tetris grid size
GRID_WIDTH = 10
GRID_HEIGHT = 20

# Tetromino shapes
SHAPES = [
    [(1, 1, 1, 1)],            # I shape
    [(1, 1, 1), (0, 1, 0)],   # T shape
    [(1, 1), (1, 1)],         # O shape
    [(1, 1, 0), (0, 1, 1)],   # Z shape
    [(0, 1, 1), (1, 1, 0)],   # S shape
    [(1, 1, 1), (0, 1, 0)],   # L shape
    [(1, 1, 1), (1, 0, 0)],   # J shape
]

# Initialize the grid
grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]

# Current falling tetromino
current_tetromino = None
current_position = (0, 0)

# Lock for controlling access to the grid
grid_lock = threading.Lock()

# Function to create a new random tetromino
def create_tetromino():
    shape = random.choice(SHAPES)
    return shape

# Function to draw the grid
def draw_grid():
    with grid_lock:
        for row in grid:
            print(' '.join(map(str, row)))

# Function to move the tetromino down
def move_down():
    global current_position
    new_position = (current_position[0] + 1, current_position[1])
    if check_collision(current_tetromino, new_position):
        current_position = new_position

# Function to check for collisions
def check_collision(tetromino, position):
    for y, row in enumerate(tetromino):
        for x, cell in enumerate(row):
            if cell:
                if (
                    position[0] + y >= GRID_HEIGHT or
                    position[1] + x < 0 or position[1] + x >= GRID_WIDTH or
                    grid[position[0] + y][position[1] + x]
                ):
                    return True
    return False

# Game loop
def game_loop():
    global current_tetromino, current_position

    while True:
        if not current_tetromino:
            current_tetromino = create_tetromino()
            current_position = (0, GRID_WIDTH // 2 - len(current_tetromino[0]) // 2)

        move_down()

        time.sleep(1)  # Adjust the speed of the game here

# Start the game loop in a separate thread
game_thread = threading.Thread(target=game_loop)
game_thread.start()

# Main loop for user input
while True:
    command = input("Enter a command (q to quit): ")
    if command == 'q':
        break

# Join the game thread before exiting
game_thread.join()
