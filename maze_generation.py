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
        """Add different terrain types to path tiles"""
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.maze[y][x] == TERRAIN_GRASS:
                    # Randomly assign terrain types
                    rand = random.random()
                    if rand < 0.15:  # 15% water
                        self.maze[y][x] = TERRAIN_WATER
                    elif rand < 0.25:  # 10% mud
                        self.maze[y][x] = TERRAIN_MUD
                    elif rand < 0.28:  # 3% lava (rare, creates obstacles)
                        self.maze[y][x] = TERRAIN_LAVA
                    # else: remains grass (72%)

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
