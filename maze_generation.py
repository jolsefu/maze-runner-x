import random
import pygame

# Terrain type constants
TERRAIN_GRASS = 0   # Cost: 1
TERRAIN_WALL = 1    # Impassable (walls)
TERRAIN_START = 2   # Start point
TERRAIN_GOAL = 3    # Goal point
TERRAIN_WATER = 4   # Cost: 3
TERRAIN_MUD = 5     # Cost: 5
TERRAIN_LAVA = 6    # Impassable

# Movement costs for each terrain type
TERRAIN_COSTS = {
    TERRAIN_GRASS: 1,
    TERRAIN_WALL: float('inf'),
    TERRAIN_START: 1,
    TERRAIN_GOAL: 1,
    TERRAIN_WATER: 3,
    TERRAIN_MUD: 5,
    TERRAIN_LAVA: float('inf')
}


class MazeGenerator:
    """Generate mazes using recursive backtracking algorithm with terrain types"""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.maze = [[TERRAIN_WALL for _ in range(width)] for _ in range(height)]

    def generate(self):
        """Generate maze using recursive backtracking"""
        # Start from position (1, 1)
        stack = [(1, 1)]
        self.maze[1][1] = TERRAIN_GRASS  # Mark as path

        while stack:
            current = stack[-1]
            x, y = current

            # Get unvisited neighbors
            neighbors = self._get_unvisited_neighbors(x, y)

            if neighbors:
                # Choose random neighbor
                next_x, next_y = random.choice(neighbors)

                # Remove wall between current and next
                wall_x = (x + next_x) // 2
                wall_y = (y + next_y) // 2
                self.maze[wall_y][wall_x] = TERRAIN_GRASS
                self.maze[next_y][next_x] = TERRAIN_GRASS

                stack.append((next_x, next_y))
            else:
                stack.pop()

        # Add different terrain types to the maze paths
        self._add_terrain_variety()

        # Set start and end points
        self.maze[1][1] = TERRAIN_START  # Start
        self.maze[self.height - 2][self.width - 2] = TERRAIN_GOAL  # Goal

        return self.maze

    def _add_terrain_variety(self):
        """Add different terrain types to path tiles, ensuring goal is reachable"""
        # First pass: add water and mud (these don't block paths)
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.maze[y][x] == TERRAIN_GRASS:
                    rand = random.random()
                    if rand < 0.20:  # 20% water
                        self.maze[y][x] = TERRAIN_WATER
                    elif rand < 0.35:  # 15% mud
                        self.maze[y][x] = TERRAIN_MUD

        # Second pass: carefully add lava only where it won't block the path
        # We'll add lava to dead-end paths or where there are alternative routes
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.maze[y][x] == TERRAIN_GRASS:
                    # Only consider adding lava with low probability
                    if random.random() < 0.05:  # 5% chance
                        # Temporarily place lava
                        self.maze[y][x] = TERRAIN_LAVA
                        # Check if goal is still reachable
                        if not self._is_goal_reachable():
                            # If not reachable, revert to grass
                            self.maze[y][x] = TERRAIN_GRASS

    def _is_goal_reachable(self):
        """Check if the goal is reachable from start using BFS"""
        # Find start and goal positions
        start_pos = None
        goal_pos = None

        for y in range(self.height):
            for x in range(self.width):
                if self.maze[y][x] == TERRAIN_START or (start_pos is None and self.maze[y][x] == TERRAIN_GRASS and y == 1 and x == 1):
                    start_pos = (x, y)
                if y == self.height - 2 and x == self.width - 2:
                    goal_pos = (x, y)

        if not start_pos:
            start_pos = (1, 1)
        if not goal_pos:
            goal_pos = (self.width - 2, self.height - 2)

        # BFS to check reachability
        from collections import deque
        queue = deque([start_pos])
        visited = set([start_pos])

        while queue:
            x, y = queue.popleft()

            if (x, y) == goal_pos:
                return True

            # Check all 4 directions
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy

                if (0 <= nx < self.width and
                    0 <= ny < self.height and
                    (nx, ny) not in visited):

                    terrain = self.maze[ny][nx]
                    # Can move through any terrain except walls and lava
                    if terrain != TERRAIN_WALL and terrain != TERRAIN_LAVA:
                        visited.add((nx, ny))
                        queue.append((nx, ny))

        return False

    def _get_unvisited_neighbors(self, x, y):
        """Get unvisited neighbors 2 steps away"""
        neighbors = []
        directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]  # Up, Right, Down, Left

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (0 < nx < self.width - 1 and
                0 < ny < self.height - 1 and
                self.maze[ny][nx] == TERRAIN_WALL):
                neighbors.append((nx, ny))

        return neighbors


def get_terrain_cost(terrain_type):
    """Get the movement cost for a terrain type"""
    return TERRAIN_COSTS.get(terrain_type, 1)


def is_passable(terrain_type):
    """Check if a terrain type is passable"""
    return TERRAIN_COSTS.get(terrain_type, float('inf')) < float('inf')


def generate_maze(width=25, height=25):
    """Generate a new random maze with terrain variety

    Args:
        width: Width of maze (should be odd number for best results)
        height: Height of maze (should be odd number for best results)

    Returns:
        2D list representing the maze where:
        0 = grass (cost 1)
        1 = wall (impassable)
        2 = start point
        3 = goal/finish point
        4 = water (cost 3)
        5 = mud (cost 5)
        6 = lava (impassable)
    """
    generator = MazeGenerator(width, height)
    return generator.generate()


def create_simple_maze():
    """Create a simple predefined maze for testing"""
    maze = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 0, 0, 1, 0, 0, 0, 0, 1],
        [1, 1, 1, 0, 1, 4, 1, 1, 0, 1],
        [1, 0, 0, 4, 0, 0, 1, 0, 0, 1],
        [1, 0, 1, 1, 1, 5, 1, 1, 0, 1],
        [1, 0, 5, 0, 1, 0, 0, 0, 0, 1],
        [1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 6, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 1, 3, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
    return maze


if __name__ == "__main__":
    # Test maze generation
    maze = generate_maze(15, 15)
    terrain_symbols = {
        0: '·',  # Grass
        1: '█',  # Wall
        2: 'S',  # Start
        3: 'E',  # Goal
        4: '≈',  # Water
        5: '~',  # Mud
        6: '♨',  # Lava
    }
    for row in maze:
        print(''.join([terrain_symbols.get(cell, '?') for cell in row]))
    print("\nMaze generated successfully!")
    print("\nLegend:")
    print("  · = Grass (cost 1)")
    print("  ≈ = Water (cost 3)")
    print("  ~ = Mud (cost 5)")
    print("  ♨ = Lava (impassable)")
    print("  █ = Wall (impassable)")
    print("  S = Start")
    print("  E = Goal")
