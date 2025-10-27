import random
import pygame


class MazeGenerator:
    """Generate mazes using recursive backtracking algorithm"""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.maze = [[1 for _ in range(width)] for _ in range(height)]

    def generate(self):
        """Generate maze using recursive backtracking"""
        # Start from position (1, 1)
        stack = [(1, 1)]
        self.maze[1][1] = 0  # Mark as path

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
                self.maze[wall_y][wall_x] = 0
                self.maze[next_y][next_x] = 0

                stack.append((next_x, next_y))
            else:
                stack.pop()

        # Set start and end points
        self.maze[1][1] = 2  # Start (green)
        self.maze[self.height - 2][self.width - 2] = 3  # End (goal - red)

        return self.maze

    def _get_unvisited_neighbors(self, x, y):
        """Get unvisited neighbors 2 steps away"""
        neighbors = []
        directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]  # Up, Right, Down, Left

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (0 < nx < self.width - 1 and
                0 < ny < self.height - 1 and
                self.maze[ny][nx] == 1):
                neighbors.append((nx, ny))

        return neighbors


def generate_maze(width=25, height=25):
    """Generate a new random maze

    Args:
        width: Width of maze (should be odd number for best results)
        height: Height of maze (should be odd number for best results)

    Returns:
        2D list representing the maze where:
        0 = path
        1 = wall
        2 = start point
        3 = goal/finish point
    """
    generator = MazeGenerator(width, height)
    return generator.generate()


def create_simple_maze():
    """Create a simple predefined maze for testing"""
    maze = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 0, 0, 1, 0, 0, 0, 0, 1],
        [1, 1, 1, 0, 1, 0, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 1],
        [1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
        [1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 1, 3, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
    return maze


if __name__ == "__main__":
    # Test maze generation
    maze = generate_maze(15, 15)
    for row in maze:
        print(''.join(['█' if cell == 1 else '·' if cell == 0 else 'S' if cell == 2 else 'E' for cell in row]))
    print("\nMaze generated successfully!")
