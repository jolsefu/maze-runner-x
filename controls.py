import pygame
from collections import deque


class InputController:
    """Handle keyboard and mouse input for player movement"""

    def __init__(self, tile_size):
        self.tile_size = tile_size
        self.mouse_held = False
        self.current_path = []
        self.path_index = 0

    def handle_keyboard_input(self, event, player, maze):
        """Handle keyboard movement (WASD or Arrow keys)"""
        if event.type != pygame.KEYDOWN:
            return 0

        move_cost = 0

        # Movement with WASD or Arrow keys
        if event.key in (pygame.K_w, pygame.K_UP):
            move_cost = player.move(0, -1, maze)
        elif event.key in (pygame.K_s, pygame.K_DOWN):
            move_cost = player.move(0, 1, maze)
        elif event.key in (pygame.K_a, pygame.K_LEFT):
            move_cost = player.move(-1, 0, maze)
        elif event.key in (pygame.K_d, pygame.K_RIGHT):
            move_cost = player.move(1, 0, maze)

        return move_cost

    def handle_mouse_input(self, event, player, maze):
        """Handle mouse click and drag for pathfinding movement"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            self.mouse_held = True
            # Calculate path to clicked position
            mouse_x, mouse_y = pygame.mouse.get_pos()
            target_tile_x = mouse_x // self.tile_size
            target_tile_y = mouse_y // self.tile_size

            # Find path from player to target
            self.current_path = self._find_path(
                player.tile_x, player.tile_y,
                target_tile_x, target_tile_y,
                maze
            )
            self.path_index = 0

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # Release left click
            self.mouse_held = False
            self.current_path = []
            self.path_index = 0

        elif event.type == pygame.MOUSEMOTION and self.mouse_held:
            # Update path if mouse moves while held
            mouse_x, mouse_y = pygame.mouse.get_pos()
            target_tile_x = mouse_x // self.tile_size
            target_tile_y = mouse_y // self.tile_size

            # Recalculate path from current position
            self.current_path = self._find_path(
                player.tile_x, player.tile_y,
                target_tile_x, target_tile_y,
                maze
            )
            self.path_index = 0

    def update_mouse_movement(self, player, maze, delay_frames=10):
        """Update player position along the path (called every frame)

        Args:
            delay_frames: Number of frames to wait between moves (lower = faster)
        """
        if not self.mouse_held or not self.current_path:
            return 0

        # Move along the path at a controlled speed
        if self.path_index < len(self.current_path):
            if pygame.time.get_ticks() % delay_frames == 0:  # Control movement speed
                next_x, next_y = self.current_path[self.path_index]

                # Calculate direction to next tile
                dx = next_x - player.tile_x
                dy = next_y - player.tile_y

                # Move player
                move_cost = player.move(dx, dy, maze)

                if move_cost > 0:
                    self.path_index += 1
                    return move_cost
                else:
                    # If move failed, clear path
                    self.current_path = []
                    self.path_index = 0

        return 0

    def _find_path(self, start_x, start_y, target_x, target_y, maze):
        """Find the shortest path using A* algorithm

        Returns a list of (x, y) tuples representing the path (excluding start position)
        """
        # Check if target is valid
        if not (0 <= target_y < len(maze) and 0 <= target_x < len(maze[0])):
            return []

        # Import terrain checking functions
        from maze_generation import is_passable

        # Check if target is passable
        if not is_passable(maze[target_y][target_x]):
            return []

        # A* pathfinding
        from heapq import heappush, heappop

        start = (start_x, start_y)
        goal = (target_x, target_y)

        # Priority queue: (f_score, counter, position, path)
        counter = 0
        open_set = []
        heappush(open_set, (0, counter, start, []))

        # Track visited nodes and their costs
        visited = {start: 0}

        while open_set:
            f_score, _, current, path = heappop(open_set)
            current_x, current_y = current

            # Check if we reached the goal
            if current == goal:
                return path

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
                from maze_generation import get_terrain_cost
                move_cost = get_terrain_cost(maze[next_y][next_x])
                new_cost = visited[current] + move_cost

                # If we found a better path to this node
                if next_pos not in visited or new_cost < visited[next_pos]:
                    visited[next_pos] = new_cost

                    # Heuristic (h_score): Manhattan distance
                    h_score = abs(next_x - target_x) + abs(next_y - target_y)
                    f_score = new_cost + h_score

                    # Add to open set
                    new_path = path + [next_pos]
                    counter += 1
                    heappush(open_set, (f_score, counter, next_pos, new_path))

        # No path found
        return []

    def draw_path(self, screen, tile_size):
        """Draw the current path on screen (for debugging/visualization)"""
        if not self.current_path:
            return

        # Draw path as semi-transparent lines
        if len(self.current_path) > 0:
            points = []
            for x, y in self.current_path:
                center_x = x * tile_size + tile_size // 2
                center_y = y * tile_size + tile_size // 2
                points.append((center_x, center_y))

            if len(points) > 1:
                # Draw line showing the path
                pygame.draw.lines(screen, (255, 255, 100), False, points, 3)

                # Draw circles at each waypoint
                for point in points:
                    pygame.draw.circle(screen, (255, 255, 100), point, 4)
