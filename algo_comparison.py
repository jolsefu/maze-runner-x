"""Algorithm Comparison Dashboard - Visualize BFS, Dijkstra, and A* exploration"""

import pygame
import sys
import time
from collections import deque
import heapq
from maze_generation import (
    generate_maze, get_terrain_cost, is_passable,
    TERRAIN_GRASS, TERRAIN_WALL, TERRAIN_START, TERRAIN_GOAL,
    TERRAIN_WATER, TERRAIN_MUD, TERRAIN_LAVA
)

# Initialize pygame
pygame.init()

# Constants
# UI Panel Configuration (Right Side)
UI_WIDTH = 465
UI_HEIGHT = 830

# Maze Configuration (Left Side)
TILE_SIZE = 16
MAZE_WIDTH_PX = 1000
MAZE_HEIGHT_PX = UI_HEIGHT

# Calculate maze dimensions in tiles
MAZE_WIDTH = MAZE_WIDTH_PX // TILE_SIZE
MAZE_HEIGHT = MAZE_HEIGHT_PX // TILE_SIZE

# Make sure dimensions are odd for better maze generation
if MAZE_WIDTH % 2 == 0:
    MAZE_WIDTH -= 1
if MAZE_HEIGHT % 2 == 0:
    MAZE_HEIGHT -= 1

# Actual maze display area
MAZE_DISPLAY_WIDTH = MAZE_WIDTH * TILE_SIZE
MAZE_DISPLAY_HEIGHT = MAZE_HEIGHT * TILE_SIZE

# Total window dimensions
TOTAL_WINDOW_WIDTH = MAZE_DISPLAY_WIDTH + UI_WIDTH
TOTAL_WINDOW_HEIGHT = max(MAZE_DISPLAY_HEIGHT, UI_HEIGHT)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (50, 150, 255)
GREEN = (50, 255, 100)
RED = (255, 50, 50)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 100)
PURPLE = (180, 50, 255)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
PINK = (255, 105, 180)

# Algorithm colors
BFS_COLOR = (0, 150, 255)      # Blue
DIJKSTRA_COLOR = (255, 165, 0)  # Orange
ASTAR_COLOR = (50, 255, 100)    # Green

# Setup screen
screen = pygame.display.set_mode((TOTAL_WINDOW_WIDTH, TOTAL_WINDOW_HEIGHT))
pygame.display.set_caption("Maze Runner - Algorithm Comparison")
clock = pygame.time.Clock()

# Load sprites
import os

def load_sprite(filename, size=TILE_SIZE):
    """Load and scale a sprite to the tile size"""
    path = os.path.join("sprites", filename)
    try:
        sprite = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(sprite, (size, size))
    except pygame.error as e:
        print(f"Warning: Could not load {filename}: {e}")
        surf = pygame.Surface((size, size))
        surf.fill((100, 100, 100))
        return surf

# Load all sprites
grass_sprite = load_sprite("grass.png")
empty_sprite = load_sprite("empty.png")
water_sprite = load_sprite("water.png")
mud_sprite = load_sprite("mud.png")
lava_sprite = load_sprite("lava.png")
wall_sprite = load_sprite("wall.png")


def draw_maze(screen, maze, tile_size):
    """Draw the maze on screen using sprites"""
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)

            if cell == TERRAIN_GRASS:
                screen.blit(grass_sprite, rect)
            elif cell == TERRAIN_WALL:
                screen.blit(wall_sprite, rect)
            elif cell == TERRAIN_WATER:
                screen.blit(water_sprite, rect)
            elif cell == TERRAIN_MUD:
                screen.blit(mud_sprite, rect)
            elif cell == TERRAIN_LAVA:
                screen.blit(lava_sprite, rect)
            elif cell == TERRAIN_START:
                screen.blit(grass_sprite, rect)
                overlay = pygame.Surface((tile_size, tile_size))
                overlay.fill(GREEN)
                overlay.set_alpha(120)
                screen.blit(overlay, rect)
            elif cell == TERRAIN_GOAL:
                screen.blit(grass_sprite, rect)
                overlay = pygame.Surface((tile_size, tile_size))
                overlay.fill(RED)
                overlay.set_alpha(120)
                screen.blit(overlay, rect)
                # Draw flag
                flag_points = [
                    (rect.centerx, rect.top + 2),
                    (rect.centerx, rect.bottom - 2),
                ]
                pygame.draw.line(screen, RED, flag_points[0], flag_points[1], 2)
                flag_tri = [
                    (rect.centerx, rect.top + 2),
                    (rect.centerx + 6, rect.top + 5),
                    (rect.centerx, rect.top + 8),
                ]
                pygame.draw.polygon(screen, RED, flag_tri)
            else:
                screen.blit(empty_sprite, rect)


def draw_exploration_lines(screen, explored_positions, parent_dict, color, tile_size, alpha=150, offset=(0, 0)):
    """Draw lines showing exploration pattern - connects each node to its parent

    Args:
        offset: (x, y) pixel offset to prevent overlapping lines from different algorithms
    """
    if len(explored_positions) < 2:
        return

    # Create semi-transparent surface
    line_surface = pygame.Surface((MAZE_DISPLAY_WIDTH, MAZE_DISPLAY_HEIGHT), pygame.SRCALPHA)

    # Draw lines connecting each node to its parent
    for node in explored_positions:
        parent = parent_dict.get(node)
        if parent is not None:  # Don't draw for start node (has no parent)
            # Calculate center positions with offset
            node_center_x = node[0] * tile_size + tile_size // 2 + offset[0]
            node_center_y = node[1] * tile_size + tile_size // 2 + offset[1]
            parent_center_x = parent[0] * tile_size + tile_size // 2 + offset[0]
            parent_center_y = parent[1] * tile_size + tile_size // 2 + offset[1]

            # Draw line from parent to node
            pygame.draw.line(line_surface, (*color, alpha),
                           (parent_center_x, parent_center_y),
                           (node_center_x, node_center_y), 2)

    screen.blit(line_surface, (0, 0))


def draw_explored_cells(screen, explored_set, color, tile_size):
    """Draw semi-transparent overlay on explored cells"""
    surface = pygame.Surface((MAZE_DISPLAY_WIDTH, MAZE_DISPLAY_HEIGHT), pygame.SRCALPHA)

    for x, y in explored_set:
        rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
        pygame.draw.rect(surface, (*color, 40), rect)  # Very transparent

    screen.blit(surface, (0, 0))


def draw_ui(screen, width, height, stats, completed):
    """Draw the UI elements for algorithm comparison"""
    font_title = pygame.font.Font(None, 48)
    font_text = pygame.font.Font(None, 32)
    font_small = pygame.font.Font(None, 28)
    font_tiny = pygame.font.Font(None, 24)

    # UI starts after the maze display area
    ui_x_start = MAZE_DISPLAY_WIDTH
    ui_padding = 40

    # Background for UI
    ui_rect = pygame.Rect(ui_x_start, 0, UI_WIDTH, height)
    pygame.draw.rect(screen, (30, 30, 30), ui_rect)

    # Draw separator line
    pygame.draw.line(screen, WHITE, (ui_x_start, 0), (ui_x_start, height), 2)

    # Title
    y_pos = 40
    title_text = font_title.render("ALGORITHM", True, YELLOW)
    title_rect = title_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
    screen.blit(title_text, title_rect)

    y_pos += 50
    subtitle_text = font_small.render("Comparison Dashboard", True, WHITE)
    subtitle_rect = subtitle_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
    screen.blit(subtitle_text, subtitle_rect)

    # Algorithm Statistics
    y_pos += 60

    algorithms = [
        ("BFS", BFS_COLOR, stats['bfs']),
        ("Dijkstra", DIJKSTRA_COLOR, stats['dijkstra']),
        ("A*", ASTAR_COLOR, stats['astar'])
    ]

    for algo_name, color, algo_stats in algorithms:
        # Algorithm name
        name_label = font_text.render(algo_name, True, color)
        name_rect = name_label.get_rect(x=ui_x_start + 30, y=y_pos)
        screen.blit(name_label, name_rect)

        y_pos += 35

        # Nodes explored
        explored_text = f"Explored: {algo_stats['explored']}"
        explored_label = font_tiny.render(explored_text, True, WHITE)
        explored_rect = explored_label.get_rect(x=ui_x_start + 50, y=y_pos)
        screen.blit(explored_label, explored_rect)

        y_pos += 25

        # Path length
        if algo_stats['path_length'] is not None:
            path_text = f"Path: {algo_stats['path_length']} steps"
        else:
            path_text = "Path: Searching..."
        path_label = font_tiny.render(path_text, True, WHITE)
        path_rect = path_label.get_rect(x=ui_x_start + 50, y=y_pos)
        screen.blit(path_label, path_rect)

        y_pos += 25

        # Runtime
        runtime_text = f"Time: {algo_stats['runtime']:.4f}s"
        runtime_label = font_tiny.render(runtime_text, True, WHITE)
        runtime_rect = runtime_label.get_rect(x=ui_x_start + 50, y=y_pos)
        screen.blit(runtime_label, runtime_rect)

        y_pos += 25

        # Status
        if algo_stats['completed']:
            status_text = "Complete"
            status_color = GREEN
        else:
            status_text = "Running..."
            status_color = YELLOW

        status_label = font_tiny.render(status_text, True, status_color)
        status_rect = status_label.get_rect(x=ui_x_start + 50, y=y_pos)
        screen.blit(status_label, status_rect)

        y_pos += 45

    # Completion message
    if completed:
        y_pos += 20
        complete_text = font_text.render("All Complete!", True, GREEN)
        complete_rect = complete_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
        screen.blit(complete_text, complete_rect)
        y_pos += 60

    # Controls
    # y_pos = height - 180
    # controls_title = font_text.render("Controls:", True, WHITE)
    # controls_rect = controls_title.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
    # screen.blit(controls_title, controls_rect)

    # y_pos += 40
    # controls = [
    #     "R - New Maze",
    #     "ESC - Return to Menu"
    # ]
    # for control in controls:
    #     control_text = font_small.render(control, True, WHITE)
    #     control_rect = control_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
    #     screen.blit(control_text, control_rect)
    #     y_pos += 35


def find_start_and_goal(maze):
    """Find start and goal positions in the maze"""
    start = None
    goal = None
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == TERRAIN_START:
                start = (x, y)
            elif cell == TERRAIN_GOAL:
                goal = (x, y)
    return start, goal


def get_neighbors(x, y, maze):
    """Get valid neighboring cells"""
    neighbors = []
    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < len(maze[0]) and 0 <= ny < len(maze):
            if is_passable(maze[ny][nx]):
                neighbors.append((nx, ny))
    return neighbors


def heuristic(a, b):
    """Manhattan distance heuristic for A*"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


class PathfindingVisualizer:
    """Handles simultaneous visualization of multiple pathfinding algorithms"""

    def __init__(self, maze, start, goal):
        self.maze = maze
        self.start = start
        self.goal = goal

        # BFS state
        self.bfs_queue = deque([start])
        self.bfs_visited = {start}
        self.bfs_parent = {start: None}
        self.bfs_exploration_order = [start]
        self.bfs_completed = False
        self.bfs_path = None
        self.bfs_start_time = time.time()
        self.bfs_end_time = None

        # Dijkstra state
        self.dijkstra_heap = [(0, start)]
        self.dijkstra_visited = set()
        self.dijkstra_cost = {start: 0}
        self.dijkstra_parent = {start: None}
        self.dijkstra_exploration_order = []
        self.dijkstra_completed = False
        self.dijkstra_path = None
        self.dijkstra_start_time = time.time()
        self.dijkstra_end_time = None

        # A* state
        self.astar_heap = [(heuristic(start, goal), 0, start)]
        self.astar_visited = set()
        self.astar_cost = {start: 0}
        self.astar_parent = {start: None}
        self.astar_exploration_order = []
        self.astar_completed = False
        self.astar_path = None
        self.astar_start_time = time.time()
        self.astar_end_time = None

    def step_bfs(self):
        """Execute one step of BFS"""
        if self.bfs_completed or not self.bfs_queue:
            return

        current = self.bfs_queue.popleft()

        if current == self.goal:
            self.bfs_completed = True
            self.bfs_end_time = time.time()
            # Reconstruct path
            path = []
            node = current
            while node is not None:
                path.append(node)
                node = self.bfs_parent[node]
            self.bfs_path = path[::-1]
            return

        for neighbor in get_neighbors(current[0], current[1], self.maze):
            if neighbor not in self.bfs_visited:
                self.bfs_visited.add(neighbor)
                self.bfs_parent[neighbor] = current
                self.bfs_queue.append(neighbor)
                self.bfs_exploration_order.append(neighbor)

    def step_dijkstra(self):
        """Execute one step of Dijkstra's algorithm"""
        if self.dijkstra_completed or not self.dijkstra_heap:
            return

        current_cost, current = heapq.heappop(self.dijkstra_heap)

        if current in self.dijkstra_visited:
            return

        self.dijkstra_visited.add(current)
        self.dijkstra_exploration_order.append(current)

        if current == self.goal:
            self.dijkstra_completed = True
            self.dijkstra_end_time = time.time()
            # Reconstruct path
            path = []
            node = current
            while node is not None:
                path.append(node)
                node = self.dijkstra_parent[node]
            self.dijkstra_path = path[::-1]
            return

        for neighbor in get_neighbors(current[0], current[1], self.maze):
            terrain_cost = get_terrain_cost(self.maze[neighbor[1]][neighbor[0]])
            new_cost = self.dijkstra_cost[current] + terrain_cost

            if neighbor not in self.dijkstra_cost or new_cost < self.dijkstra_cost[neighbor]:
                self.dijkstra_cost[neighbor] = new_cost
                self.dijkstra_parent[neighbor] = current
                heapq.heappush(self.dijkstra_heap, (new_cost, neighbor))

    def step_astar(self):
        """Execute one step of A* algorithm"""
        if self.astar_completed or not self.astar_heap:
            return

        _, current_cost, current = heapq.heappop(self.astar_heap)

        if current in self.astar_visited:
            return

        self.astar_visited.add(current)
        self.astar_exploration_order.append(current)

        if current == self.goal:
            self.astar_completed = True
            self.astar_end_time = time.time()
            # Reconstruct path
            path = []
            node = current
            while node is not None:
                path.append(node)
                node = self.astar_parent[node]
            self.astar_path = path[::-1]
            return

        for neighbor in get_neighbors(current[0], current[1], self.maze):
            terrain_cost = get_terrain_cost(self.maze[neighbor[1]][neighbor[0]])
            new_cost = self.astar_cost[current] + terrain_cost

            if neighbor not in self.astar_cost or new_cost < self.astar_cost[neighbor]:
                self.astar_cost[neighbor] = new_cost
                self.astar_parent[neighbor] = current
                f_score = new_cost + heuristic(neighbor, self.goal)
                heapq.heappush(self.astar_heap, (f_score, new_cost, neighbor))

    def get_stats(self):
        """Get current statistics for all algorithms"""
        return {
            'bfs': {
                'explored': len(self.bfs_visited),
                'path_length': len(self.bfs_path) if self.bfs_path else None,
                'runtime': (self.bfs_end_time if self.bfs_end_time else time.time()) - self.bfs_start_time,
                'completed': self.bfs_completed
            },
            'dijkstra': {
                'explored': len(self.dijkstra_visited),
                'path_length': len(self.dijkstra_path) if self.dijkstra_path else None,
                'runtime': (self.dijkstra_end_time if self.dijkstra_end_time else time.time()) - self.dijkstra_start_time,
                'completed': self.dijkstra_completed
            },
            'astar': {
                'explored': len(self.astar_visited),
                'path_length': len(self.astar_path) if self.astar_path else None,
                'runtime': (self.astar_end_time if self.astar_end_time else time.time()) - self.astar_start_time,
                'completed': self.astar_completed
            }
        }

    def all_completed(self):
        """Check if all algorithms have completed"""
        return self.bfs_completed and self.dijkstra_completed and self.astar_completed


def start(goal_placement='corner', game_mode='explore', fog_of_war=False, energy_constraint=False, fuel_limit=100):
    """Start algorithm comparison mode

    Args:
        goal_placement: Where to place the goal
        game_mode: Maze generation mode
        fog_of_war: Not used in this mode
        energy_constraint: Not used in this mode
        fuel_limit: Not used in this mode
    """
    # Generate maze
    maze = generate_maze(MAZE_WIDTH, MAZE_HEIGHT, goal_placement, game_mode, 0)

    # Find start and goal
    start_pos, goal_pos = find_start_and_goal(maze)

    # Create visualizer
    visualizer = PathfindingVisualizer(maze, start_pos, goal_pos)

    loop(maze, visualizer, goal_placement, game_mode)
    print("=" * 50)
    print("ALGORITHM COMPARISON ENDED".center(50))
    print("=" * 50)


def loop(maze, visualizer, goal_placement, game_mode):
    """Main loop for algorithm comparison"""
    run = True
    steps_per_frame = 3  # Number of algorithm steps per frame

    while run:
        clock.tick(60)

        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # Restart with new maze
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                maze = generate_maze(MAZE_WIDTH, MAZE_HEIGHT, goal_placement, game_mode, 0)
                start_pos, goal_pos = find_start_and_goal(maze)
                visualizer = PathfindingVisualizer(maze, start_pos, goal_pos)

            # Return to menu
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                run = False

        # Step algorithms if not all completed
        if not visualizer.all_completed():
            for _ in range(steps_per_frame):
                if not visualizer.bfs_completed:
                    visualizer.step_bfs()
                if not visualizer.dijkstra_completed:
                    visualizer.step_dijkstra()
                if not visualizer.astar_completed:
                    visualizer.step_astar()

        # Draw everything
        screen.fill(BLACK)

        # Draw maze
        draw_maze(screen, maze, TILE_SIZE)

        # Draw explored cells (very transparent)
        draw_explored_cells(screen, visualizer.bfs_visited, BFS_COLOR, TILE_SIZE)
        draw_explored_cells(screen, visualizer.dijkstra_visited, DIJKSTRA_COLOR, TILE_SIZE)
        draw_explored_cells(screen, visualizer.astar_visited, ASTAR_COLOR, TILE_SIZE)

        # Draw exploration lines with offsets to prevent overlapping
        # BFS - slightly left
        draw_exploration_lines(screen, visualizer.bfs_exploration_order, visualizer.bfs_parent, BFS_COLOR, TILE_SIZE, offset=(-2, -2))
        # Dijkstra - center (no offset)
        draw_exploration_lines(screen, visualizer.dijkstra_exploration_order, visualizer.dijkstra_parent, DIJKSTRA_COLOR, TILE_SIZE, offset=(0, 0))
        # A* - slightly right
        draw_exploration_lines(screen, visualizer.astar_exploration_order, visualizer.astar_parent, ASTAR_COLOR, TILE_SIZE, offset=(2, 2))

        # Draw final paths if completed (thicker lines with offsets)
        if visualizer.bfs_path:
            points = [(x * TILE_SIZE + TILE_SIZE // 2 - 2, y * TILE_SIZE + TILE_SIZE // 2 - 2)
                     for x, y in visualizer.bfs_path]
            if len(points) > 1:
                pygame.draw.lines(screen, BFS_COLOR, False, points, 4)

        if visualizer.dijkstra_path:
            points = [(x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2)
                     for x, y in visualizer.dijkstra_path]
            if len(points) > 1:
                pygame.draw.lines(screen, DIJKSTRA_COLOR, False, points, 4)

        if visualizer.astar_path:
            points = [(x * TILE_SIZE + TILE_SIZE // 2 + 2, y * TILE_SIZE + TILE_SIZE // 2 + 2)
                     for x, y in visualizer.astar_path]
            if len(points) > 1:
                pygame.draw.lines(screen, ASTAR_COLOR, False, points, 4)

        # Draw UI
        stats = visualizer.get_stats()
        draw_ui(screen, TOTAL_WINDOW_WIDTH, TOTAL_WINDOW_HEIGHT, stats, visualizer.all_completed())

        pygame.display.flip()

    # Don't call pygame.quit() - let menu handle it


if __name__ == "__main__":
    start('corner', 'explore')
    pygame.quit()
