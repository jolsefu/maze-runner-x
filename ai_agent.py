"""AI Agent for competitive maze navigation"""

import pygame
from heapq import heappush, heappop
from maze_generation import get_terrain_cost, is_passable, TERRAIN_GOAL


class AIAgent:
    """AI agent that competes with the player"""

    def __init__(self, x, y, tile_size, name, color):
        self.tile_x = x
        self.tile_y = y
        self.tile_size = tile_size
        self.name = name
        self.color = color
        self.total_cost = 0
        self.path = []  # Current path to goal
        self.finished = False
        self.moves = 0

    def calculate_path(self, maze):
        """Calculate path to goal using A* algorithm"""
        # Find goal position
        goal_x, goal_y = None, None
        for y in range(len(maze)):
            for x in range(len(maze[0])):
                if maze[y][x] == TERRAIN_GOAL:
                    goal_x, goal_y = x, y
                    break
            if goal_x is not None:
                break

        if goal_x is None:
            return

        # Use A* pathfinding
        start = (self.tile_x, self.tile_y)
        goal = (goal_x, goal_y)

        # Priority queue: (f_score, counter, position, path, cost)
        counter = 0
        open_set = []
        heappush(open_set, (0, counter, start, [], 0))

        # Track visited nodes and their costs
        visited = {start: 0}

        while open_set:
            f_score, _, current, path, current_cost = heappop(open_set)
            current_x, current_y = current

            # Check if we reached the goal
            if current == goal:
                self.path = path
                return

            # Explore neighbors (4 directions)
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                next_x = current_x + dx
                next_y = current_y + dy
                next_pos = (next_x, next_y)

                # Check bounds
                if not (0 <= next_y < len(maze) and 0 <= next_x < len(maze[0])):
                    continue

                # Check if passable
                if not is_passable(maze[next_y][next_x]):
                    continue

                # Calculate cost (g_score)
                move_cost = get_terrain_cost(maze[next_y][next_x])
                new_cost = current_cost + move_cost

                # If we found a better path to this node
                if next_pos not in visited or new_cost < visited[next_pos]:
                    visited[next_pos] = new_cost

                    # Heuristic (h_score): Manhattan distance
                    h_score = abs(next_x - goal_x) + abs(next_y - goal_y)
                    f_score = new_cost + h_score

                    # Add to open set
                    new_path = path + [next_pos]
                    counter += 1
                    heappush(open_set, (f_score, counter, next_pos, new_path, new_cost))

        # No path found
        self.path = []

    def make_move(self, maze):
        """Make one move along the calculated path"""
        if not self.path or self.finished:
            return False

        # Get next position
        next_x, next_y = self.path[0]
        self.path = self.path[1:]  # Remove first element

        # Move to next position
        terrain = maze[next_y][next_x]
        move_cost = get_terrain_cost(terrain)
        self.total_cost += move_cost
        self.tile_x = next_x
        self.tile_y = next_y
        self.moves += 1

        # Check if reached goal
        if maze[self.tile_y][self.tile_x] == TERRAIN_GOAL:
            self.finished = True
            return True

        return True

    def draw(self, screen):
        """Draw the AI agent"""
        padding = 2
        rect = pygame.Rect(
            self.tile_x * self.tile_size + padding,
            self.tile_y * self.tile_size + padding,
            self.tile_size - padding * 2,
            self.tile_size - padding * 2
        )
        # Draw triangle pointing down
        center_x = rect.centerx
        center_y = rect.centery
        size = rect.width // 2
        points = [
            (center_x, center_y - size),  # Top
            (center_x - size, center_y + size),  # Bottom left
            (center_x + size, center_y + size)  # Bottom right
        ]
        pygame.draw.polygon(screen, self.color, points)
        pygame.draw.polygon(screen, (255, 255, 255), points, 2)  # White outline

    def draw_path(self, screen, tile_size):
        """Draw the AI's planned path"""
        if not self.path:
            return

        # Draw path as semi-transparent lines
        points = [(self.tile_x * tile_size + tile_size // 2,
                  self.tile_y * tile_size + tile_size // 2)]

        for x, y in self.path:
            center_x = x * tile_size + tile_size // 2
            center_y = y * tile_size + tile_size // 2
            points.append((center_x, center_y))

        if len(points) > 1:
            # Draw dashed line showing the path
            pygame.draw.lines(screen, self.color, False, points, 2)
