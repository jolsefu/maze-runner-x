"""AI Agent for competitive maze navigation"""

import pygame
from heapq import heappush, heappop
from maze_generation import get_terrain_cost, is_passable, TERRAIN_GOAL, TERRAIN_CHECKPOINT, TERRAIN_GRASS


class AIAgent:
    """AI agent that competes with the player"""

    def __init__(self, x, y, tile_size, name, color, energy_limit=None):
        self.tile_x = x
        self.tile_y = y
        self.tile_size = tile_size
        self.name = name
        self.color = color
        self.total_cost = 0
        self.path = []  # Current path to goal
        self.finished = False
        self.moves = 0
        self.explored_tiles = set()  # Tiles the AI has seen (for fog of war)
        self.known_maze = {}  # Stores terrain info for explored tiles (x, y) -> terrain_type
        self.energy_limit = energy_limit  # Maximum energy allowed (None = unlimited)
        self.out_of_energy = False  # Flag for energy depletion
        self.checkpoints_collected = 0  # Number of checkpoints collected (for multi-goal mode)
        self.remaining_checkpoints = []  # List of checkpoint positions to visit
        self.exploration_cost = 0  # Total exploration cost (for multi-goal mode)

    def update_vision(self, maze, vision_range=5, fog_of_war=False):
        """Update AI's knowledge of the maze based on current position

        Args:
            maze: The full maze
            vision_range: How far the AI can see
            fog_of_war: Whether fog of war is enabled
        """
        if not fog_of_war:
            # If no fog of war, AI knows everything
            return

        # Update explored tiles and known maze within vision range
        for dy in range(-vision_range, vision_range + 1):
            for dx in range(-vision_range, vision_range + 1):
                tile_x = self.tile_x + dx
                tile_y = self.tile_y + dy

                # Check bounds
                if 0 <= tile_x < len(maze[0]) and 0 <= tile_y < len(maze):
                    # Use Manhattan distance for vision
                    if abs(dx) + abs(dy) <= vision_range:
                        self.explored_tiles.add((tile_x, tile_y))
                        self.known_maze[(tile_x, tile_y)] = maze[tile_y][tile_x]

    def calculate_path(self, maze, fog_of_war=False):
        """Calculate path to goal using A* algorithm

        Args:
            maze: The full maze
            fog_of_war: If True, AI can only pathfind through explored tiles
        """
        # Update AI's vision first
        self.update_vision(maze, fog_of_war=fog_of_war)

        # Determine target based on remaining checkpoints
        target_x, target_y = None, None

        # If there are checkpoints remaining, target the nearest one
        if self.remaining_checkpoints:
            # Find nearest checkpoint
            nearest_checkpoint = min(self.remaining_checkpoints,
                                    key=lambda pos: abs(pos[0] - self.tile_x) + abs(pos[1] - self.tile_y))
            target_x, target_y = nearest_checkpoint
        else:
            # All checkpoints collected, now go to goal
            if fog_of_war:
                # AI can only know about goal if it has explored that tile
                for (x, y), terrain in self.known_maze.items():
                    if terrain == TERRAIN_GOAL:
                        target_x, target_y = x, y
                        break
            else:
                # No fog of war - AI can see the entire maze
                for y in range(len(maze)):
                    for x in range(len(maze[0])):
                        if maze[y][x] == TERRAIN_GOAL:
                            target_x, target_y = x, y
                            break
                    if target_x is not None:
                        break

        # If target not found, explore blindly
        if target_x is None:
            self._explore_blindly(maze, fog_of_war)
            return

        # Use A* pathfinding to target
        start = (self.tile_x, self.tile_y)
        goal = (target_x, target_y)

        # Priority queue: (f_score, counter, position, path, cost)
        counter = 0
        open_set = []
        heappush(open_set, (0, counter, start, [], 0))

        # Track visited nodes and their costs
        visited = {start: 0}

        while open_set:
            f_score, _, current, path, current_cost = heappop(open_set)
            current_x, current_y = current

            # Check if we reached the target
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

                # In fog of war mode, only consider explored tiles
                if fog_of_war and next_pos not in self.known_maze:
                    continue

                # Check if passable
                terrain = self.known_maze.get(next_pos, maze[next_y][next_x]) if fog_of_war else maze[next_y][next_x]
                if not is_passable(terrain):
                    continue

                # Calculate cost (g_score)
                move_cost = get_terrain_cost(terrain)
                new_cost = current_cost + move_cost

                # If we found a better path to this node
                if next_pos not in visited or new_cost < visited[next_pos]:
                    visited[next_pos] = new_cost

                    # Heuristic (h_score): Manhattan distance to target
                    h_score = abs(next_x - target_x) + abs(next_y - target_y)
                    f_score = new_cost + h_score

                    # Add to open set
                    new_path = path + [next_pos]
                    counter += 1
                    heappush(open_set, (f_score, counter, next_pos, new_path, new_cost))

        # No path found
        self.path = []

    def _explore_blindly(self, maze, fog_of_war):
        """When goal is not visible, move towards unexplored areas

        This makes the AI explore the maze when it doesn't know where the goal is
        """
        if not fog_of_war:
            return

        # Find the nearest unexplored passable tile within or adjacent to explored area
        import random

        candidates = []
        explored_neighbors = set()

        # Check tiles adjacent to explored area
        for (ex, ey) in self.explored_tiles:
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = ex + dx, ey + dy
                if (nx, ny) not in self.explored_tiles:
                    if 0 <= nx < len(maze[0]) and 0 <= ny < len(maze):
                        explored_neighbors.add((nx, ny))

        # From current position, try to reach the nearest unexplored border
        if explored_neighbors:
            target = min(explored_neighbors,
                        key=lambda pos: abs(pos[0] - self.tile_x) + abs(pos[1] - self.tile_y))

            # Try to pathfind to just before the unexplored area
            for (ex, ey) in self.explored_tiles:
                if abs(ex - target[0]) + abs(ey - target[1]) == 1:  # Adjacent to target
                    # Try to path to this explored tile
                    self._pathfind_in_known_area((ex, ey))
                    if self.path:
                        return

        # Fallback: move to any adjacent explored passable tile
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = self.tile_x + dx, self.tile_y + dy
            if (nx, ny) in self.known_maze and is_passable(self.known_maze[(nx, ny)]):
                self.path = [(nx, ny)]
                return

        self.path = []

    def _pathfind_in_known_area(self, target):
        """Pathfind to a target within the known area"""
        start = (self.tile_x, self.tile_y)

        # Simple BFS for short paths
        from collections import deque
        queue = deque([(start, [])])
        visited = {start}

        while queue:
            current, path = queue.popleft()

            if current == target:
                self.path = path
                return

            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = current[0] + dx, current[1] + dy
                next_pos = (nx, ny)

                if next_pos in visited:
                    continue
                if next_pos not in self.known_maze:
                    continue
                if not is_passable(self.known_maze[next_pos]):
                    continue

                visited.add(next_pos)
                queue.append((next_pos, path + [next_pos]))

        self.path = []

    def make_move(self, maze):
        """Make one move along the calculated path"""
        if not self.path or self.finished or self.out_of_energy:
            return False

        # Get next position
        next_x, next_y = self.path[0]

        # Check energy before moving
        terrain = maze[next_y][next_x]
        move_cost = get_terrain_cost(terrain)

        if self.energy_limit is not None:
            if self.total_cost + move_cost > self.energy_limit:
                # Out of energy - can't make this move
                self.out_of_energy = True
                self.path = []
                return False

        # Execute move
        self.path = self.path[1:]  # Remove first element
        self.total_cost += move_cost
        self.tile_x = next_x
        self.tile_y = next_y
        self.moves += 1

        # Check if reached a checkpoint (check position, not terrain, since player might have collected it first)
        if (next_x, next_y) in self.remaining_checkpoints:
            # Collect the checkpoint (even if terrain is already grass from player collecting it)
            if terrain == TERRAIN_CHECKPOINT or terrain == TERRAIN_GRASS:
                self.checkpoints_collected += 1
                # Don't reset cost - keep accumulating
                # self.exploration_cost += self.total_cost
                # self.total_cost = 0
                self.remaining_checkpoints.remove((next_x, next_y))
                # Don't convert checkpoint to grass - let rendering handle visibility
                # maze[next_y][next_x] = TERRAIN_GRASS
                print(f"✓ {self.name} collected checkpoint! ({self.checkpoints_collected})")
            else:
                # Checkpoint position but not grass/checkpoint terrain (weird edge case)
                self.remaining_checkpoints.remove((next_x, next_y))
            # Path will be recalculated by the main game loop before next move
            return True

        # Check if reached goal
        if maze[self.tile_y][self.tile_x] == TERRAIN_GOAL:
            # Can only finish if all checkpoints collected
            if not self.remaining_checkpoints:
                self.finished = True
                return True
            # If at goal but haven't collected all checkpoints, path will be recalculated by main loop

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
