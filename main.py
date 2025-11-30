import pygame
import sys
import os
import random
from maze_generation import (
    generate_maze, create_simple_maze, get_terrain_cost, is_passable,
    TERRAIN_GRASS, TERRAIN_WALL, TERRAIN_START, TERRAIN_GOAL,
    TERRAIN_WATER, TERRAIN_MUD, TERRAIN_LAVA, TERRAIN_CHECKPOINT
)
from controls import InputController
from ai_agent import AIAgent

# Initialize pygame
pygame.init()

# Constants
# UI Panel Configuration (Right Side)
UI_WIDTH = 465  # Width of the right-hand UI panel
UI_HEIGHT = 830  # Height of the right-hand UI panel

# Maze Configuration (Left Side)
TILE_SIZE = 16  # 16x16 tiles to match sprite size
MAZE_WIDTH_PX = 1000  # Width in pixels for the maze area
MAZE_HEIGHT_PX = UI_HEIGHT  # Height in pixels for the maze area (matches UI height)

# Calculate maze dimensions in tiles
MAZE_WIDTH = MAZE_WIDTH_PX // TILE_SIZE  # Calculate maze width in tiles
MAZE_HEIGHT = MAZE_HEIGHT_PX // TILE_SIZE  # Calculate maze height in tiles

# Make sure dimensions are odd for better maze generation
if MAZE_WIDTH % 2 == 0:
    MAZE_WIDTH -= 1
if MAZE_HEIGHT % 2 == 0:
    MAZE_HEIGHT -= 1

# Actual maze display area (after adjusting for odd dimensions)
MAZE_DISPLAY_WIDTH = MAZE_WIDTH * TILE_SIZE
MAZE_DISPLAY_HEIGHT = MAZE_HEIGHT * TILE_SIZE

# Total window dimensions
TOTAL_WINDOW_WIDTH = MAZE_DISPLAY_WIDTH + UI_WIDTH
TOTAL_WINDOW_HEIGHT = max(MAZE_DISPLAY_HEIGHT, UI_HEIGHT)  # Use the larger of the two

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (50, 150, 255)
GREEN = (50, 255, 100)
RED = (255, 50, 50)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 100)
DARK_GREEN = (0, 100, 0)
PURPLE = (180, 50, 255)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)

# Setup screen
screen = pygame.display.set_mode((TOTAL_WINDOW_WIDTH, TOTAL_WINDOW_HEIGHT))
pygame.display.set_caption("Maze Runner - Navigate to the Goal!")
clock = pygame.time.Clock()

# Load sprites
def load_sprite(filename, size=TILE_SIZE):
    """Load and scale a sprite to the tile size"""
    path = os.path.join("sprites", filename)
    try:
        sprite = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(sprite, (size, size))
    except pygame.error as e:
        print(f"Warning: Could not load {filename}: {e}")
        # Return a colored surface as fallback
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

class Player:
    """Player that navigates the maze"""

    def __init__(self, x, y, tile_size, sprite=None, color=BLUE, energy_limit=None):
        self.tile_x = x
        self.tile_y = y
        self.tile_size = tile_size
        self.speed = 1  # Tiles per move
        self.color = color
        self.sprite = sprite
        self.total_cost = 0  # Track total movement cost
        self.exploration_cost = 0  # Total exploration cost (for multi-goal mode)
        self.checkpoints_collected = 0  # Number of checkpoints collected
        self.energy_limit = energy_limit  # Maximum energy allowed (None = unlimited)
        self.out_of_energy = False  # Flag for energy depletion

    def move(self, dx, dy, maze):
        """Move player if the destination is passable, return cost of move"""
        # Check if out of energy
        if self.out_of_energy:
            return 0

        new_x = self.tile_x + dx
        new_y = self.tile_y + dy

        # Check bounds
        if not (0 <= new_y < len(maze) and 0 <= new_x < len(maze[0])):
            return 0

        terrain = maze[new_y][new_x]

        # Check if terrain is passable
        if is_passable(terrain):
            move_cost = get_terrain_cost(terrain)

            # Check energy constraint
            if self.energy_limit is not None:
                if self.total_cost + move_cost > self.energy_limit:
                    # Not enough energy for this move
                    self.out_of_energy = True
                    return 0

            # Execute move
            self.tile_x = new_x
            self.tile_y = new_y
            self.total_cost += move_cost
            return move_cost
        return 0

    def draw(self, screen):
        """Draw the player"""
        if self.sprite:
            # Draw sprite
            x = self.tile_x * self.tile_size
            y = self.tile_y * self.tile_size
            screen.blit(self.sprite, (x, y))
        else:
            # Draw circle as fallback
            padding = 4
            rect = pygame.Rect(
                self.tile_x * self.tile_size + padding,
                self.tile_y * self.tile_size + padding,
                self.tile_size - padding * 2,
                self.tile_size - padding * 2
            )
            pygame.draw.circle(screen, self.color, rect.center, rect.width // 2)

    def is_at_goal(self, maze):
        """Check if player reached the goal"""
        return maze[self.tile_y][self.tile_x] == TERRAIN_GOAL


def draw_maze_with_fog(screen, maze, tile_size, player, explored_tiles, vision_range=5, all_checkpoints=None, collected_checkpoints=None):
    """Draw the maze with fog of war - only showing tiles within vision range or previously explored

    Args:
        all_checkpoints: Set of all checkpoint positions (x, y)
        collected_checkpoints: Set of collected checkpoint positions (x, y)
    """
    if all_checkpoints is None:
        all_checkpoints = set()
    if collected_checkpoints is None:
        collected_checkpoints = set()

    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)

            # Calculate distance from player (Manhattan distance)
            distance = abs(x - player.tile_x) + abs(y - player.tile_y)
            is_visible = distance <= vision_range
            is_explored = (x, y) in explored_tiles

            if is_visible or is_explored:
                # Check if this position should show a checkpoint
                should_show_checkpoint = (x, y) in all_checkpoints and (x, y) not in collected_checkpoints

                # Draw the tile normally
                if cell == TERRAIN_GRASS or cell == TERRAIN_CHECKPOINT:  # Grass - cost 1
                    screen.blit(grass_sprite, rect)
                    # Draw checkpoint if it should be shown
                    if should_show_checkpoint:
                        # Draw checkpoint marker (yellow star)
                        overlay = pygame.Surface((tile_size, tile_size))
                        overlay.fill(YELLOW)
                        overlay.set_alpha(100)
                        screen.blit(overlay, rect)
                        # Draw star shape
                        pygame.draw.circle(screen, YELLOW, rect.center, tile_size // 4, 3)
                elif cell == TERRAIN_WALL:  # Wall - impassable
                    screen.blit(wall_sprite, rect)
                elif cell == TERRAIN_WATER:  # Water - cost 3
                    screen.blit(water_sprite, rect)
                elif cell == TERRAIN_MUD:  # Mud - cost 5
                    screen.blit(mud_sprite, rect)
                elif cell == TERRAIN_LAVA:  # Lava - impassable
                    screen.blit(lava_sprite, rect)
                elif cell == TERRAIN_START:  # Start - use grass with green overlay
                    screen.blit(grass_sprite, rect)
                    # Add green tint for start
                    overlay = pygame.Surface((tile_size, tile_size))
                    overlay.fill(GREEN)
                    overlay.set_alpha(120)
                    screen.blit(overlay, rect)
                elif cell == TERRAIN_GOAL:  # Goal - use grass with red flag
                    screen.blit(grass_sprite, rect)
                    # Add red tint for goal
                    overlay = pygame.Surface((tile_size, tile_size))
                    overlay.fill(RED)
                    overlay.set_alpha(120)
                    screen.blit(overlay, rect)
                    # Draw a small flag marker
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
                else:  # Fallback
                    screen.blit(empty_sprite, rect)

                # Dim previously explored but not currently visible tiles
                if not is_visible and is_explored:
                    fog_overlay = pygame.Surface((tile_size, tile_size))
                    fog_overlay.fill(BLACK)
                    fog_overlay.set_alpha(120)  # Semi-transparent black
                    screen.blit(fog_overlay, rect)
            else:
                # Draw black fog for unexplored tiles
                pygame.draw.rect(screen, BLACK, rect)


def draw_maze(screen, maze, tile_size, all_checkpoints=None, collected_checkpoints=None):
    """Draw the maze on screen using sprites with different terrain types

    Args:
        all_checkpoints: Set of all checkpoint positions (x, y)
        collected_checkpoints: Set of collected checkpoint positions (x, y)
    """
    if all_checkpoints is None:
        all_checkpoints = set()
    if collected_checkpoints is None:
        collected_checkpoints = set()

    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)

            # Check if this position should show a checkpoint
            should_show_checkpoint = (x, y) in all_checkpoints and (x, y) not in collected_checkpoints

            if cell == TERRAIN_GRASS or cell == TERRAIN_CHECKPOINT:  # Grass - cost 1
                screen.blit(grass_sprite, rect)
                # Draw checkpoint if it should be shown
                if should_show_checkpoint:
                    # Draw checkpoint marker (yellow star)
                    overlay = pygame.Surface((tile_size, tile_size))
                    overlay.fill(YELLOW)
                    overlay.set_alpha(100)
                    screen.blit(overlay, rect)
                    # Draw star shape
                    pygame.draw.circle(screen, YELLOW, rect.center, tile_size // 4, 3)
            elif cell == TERRAIN_WALL:  # Wall - impassable
                screen.blit(wall_sprite, rect)
            elif cell == TERRAIN_WATER:  # Water - cost 3
                screen.blit(water_sprite, rect)
            elif cell == TERRAIN_MUD:  # Mud - cost 5
                screen.blit(mud_sprite, rect)
            elif cell == TERRAIN_LAVA:  # Lava - impassable
                screen.blit(lava_sprite, rect)
            elif cell == TERRAIN_START:  # Start - use grass with green overlay
                screen.blit(grass_sprite, rect)
                # Add green tint for start
                overlay = pygame.Surface((tile_size, tile_size))
                overlay.fill(GREEN)
                overlay.set_alpha(120)
                screen.blit(overlay, rect)
            elif cell == TERRAIN_GOAL:  # Goal - use grass with red flag
                screen.blit(grass_sprite, rect)
                # Add red tint for goal
                overlay = pygame.Surface((tile_size, tile_size))
                overlay.fill(RED)
                overlay.set_alpha(120)
                screen.blit(overlay, rect)
                # Draw a small flag marker
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
            else:  # Fallback
                screen.blit(empty_sprite, rect)


def draw_ui(screen, width, height, moves, total_cost, won, game_mode='explore', player=None, num_checkpoints=3, player_mode='solo', ai_agents=None, winner=None, fog_of_war=False, energy_constraint=False, fuel_limit=100, current_level=1, level_moves=0, player_collected_checkpoints=None, ai_collected_checkpoints=None, timer_enabled=False, time_remaining=0, time_limit=60, loser=None):
    """Draw the UI elements on the right side of the screen."""
    font_title = pygame.font.Font(None, 48)
    font_text = pygame.font.Font(None, 32)
    font_small = pygame.font.Font(None, 28)
    font_tiny = pygame.font.Font(None, 22)

    if ai_agents is None:
        ai_agents = []

    # UI starts after the maze display area (right side)
    ui_x_start = MAZE_DISPLAY_WIDTH
    ui_padding = 40

    # Background for UI (right side panel)
    ui_rect = pygame.Rect(ui_x_start, 0, UI_WIDTH, height)
    pygame.draw.rect(screen, (30, 30, 30), ui_rect)

    # Draw a separator line
    pygame.draw.line(screen, WHITE, (ui_x_start, 0), (ui_x_start, height), 2)

    # Title
    y_pos = 50
    if game_mode == 'dynamic':
        title_text = font_title.render("PROGRESSIVE", True, YELLOW)
    else:
        title_text = font_title.render("MAZE RUNNER", True, YELLOW)
    title_rect = title_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
    screen.blit(title_text, title_rect)

    # Show level for dynamic mode
    if game_mode == 'dynamic':
        y_pos += 55
        level_text = font_title.render(f"LEVEL {current_level}", True, CYAN)
        level_rect = level_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
        screen.blit(level_text, level_rect)

    # Show fog of war indicator if active
    if fog_of_war:
        y_pos += 60
        fog_text = font_small.render("FOG OF WAR", True, CYAN)
        fog_rect = fog_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
        screen.blit(fog_text, fog_rect)
        y_pos -= 10  # Adjust spacing

    # Competitive mode UI
    if player_mode == 'competitive':
        y_pos += 70
        mode_text = font_small.render("COMPETITIVE MODE", True, RED)
        mode_rect = mode_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
        screen.blit(mode_text, mode_rect)

        # Player stats
        y_pos += 50
        player_label = font_text.render("You:", True, BLUE)
        player_label_rect = player_label.get_rect(x=ui_x_start + 30, y=y_pos)
        screen.blit(player_label, player_label_rect)

        y_pos += 35
        if energy_constraint:
            player_stats = font_small.render(f"Moves: {moves}  Energy: {total_cost}/{fuel_limit}", True, WHITE)
        else:
            player_stats = font_small.render(f"Moves: {moves}  Cost: {total_cost}", True, WHITE)
        player_stats_rect = player_stats.get_rect(x=ui_x_start + 50, y=y_pos)
        screen.blit(player_stats, player_stats_rect)

        # Checkpoint counter for player (only in multi-goal mode)
        if player_mode == "competitive" and game_mode == "multi-goal" and player_collected_checkpoints is not None:
            y_pos += 30
            player_cp_text = font_tiny.render(f"Checkpoints: {len(player_collected_checkpoints)}/{num_checkpoints}", True, BLUE)
            player_cp_rect = player_cp_text.get_rect(x=ui_x_start + 50, y=y_pos)
            screen.blit(player_cp_text, player_cp_rect)

        # AI agents stats
        y_pos += 50
        for ai in ai_agents:
            status = "FINISHED!" if ai.finished else "Running"
            ai_label = font_text.render(f"{ai.name}:", True, ai.color)
            ai_label_rect = ai_label.get_rect(x=ui_x_start + 30, y=y_pos)
            screen.blit(ai_label, ai_label_rect)

            y_pos += 30
            if energy_constraint:
                ai_stats = font_tiny.render(f"Moves: {ai.moves}  Energy: {ai.total_cost}/{fuel_limit}", True, WHITE)
            else:
                ai_stats = font_tiny.render(f"Moves: {ai.moves}  Cost: {ai.total_cost}", True, WHITE)
            ai_stats_rect = ai_stats.get_rect(x=ui_x_start + 50, y=y_pos)
            screen.blit(ai_stats, ai_stats_rect)

            # Checkpoint counter for AI (only in multi-goal mode)
            if player_mode == "competitive" and game_mode == "multi-goal" and ai_collected_checkpoints is not None:
                y_pos += 25
                ai_cp_text = font_tiny.render(f"Checkpoints: {len(ai_collected_checkpoints)}/{num_checkpoints}", True, RED)
                ai_cp_rect = ai_cp_text.get_rect(x=ui_x_start + 50, y=y_pos)
                screen.blit(ai_cp_text, ai_cp_rect)

            y_pos += 25
            ai_status = font_tiny.render(status, True, GREEN if ai.finished else GRAY)
            ai_status_rect = ai_status.get_rect(x=ui_x_start + 50, y=y_pos)
            screen.blit(ai_status, ai_status_rect)

            y_pos += 35

        # Winner announcement
        if won and winner:
            y_pos += 20
            if winner == "No one":
                # Draw or no winner
                winner_color = GRAY
                win_text = font_title.render("NO ONE WINS!", True, winner_color)
            else:
                winner_color = BLUE if winner == "Player" else RED
                win_text = font_title.render(f"{winner} WINS!", True, winner_color)
            win_rect = win_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
            screen.blit(win_text, win_rect)
            y_pos += 70

        # Timer display for competitive mode (if timer is enabled)
        if timer_enabled and not won:
            y_pos += 20
            timer_label = font_text.render("Time Remaining:", True, WHITE)
            timer_label_rect = timer_label.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
            screen.blit(timer_label, timer_label_rect)

            y_pos += 45
            # Color based on time remaining
            time_percent = (time_remaining / time_limit) * 100 if time_limit > 0 else 0
            if time_percent > 50:
                timer_color = GREEN
            elif time_percent > 25:
                timer_color = YELLOW
            else:
                timer_color = RED

            minutes = int(time_remaining // 60)
            seconds = int(time_remaining % 60)
            timer_text = font_title.render(f"{minutes}:{seconds:02d}", True, timer_color)
            timer_rect = timer_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
            screen.blit(timer_text, timer_rect)

    else:
        # Solo mode UI (original)
        # Moves counter
        y_pos += 100

        # Show different stats for dynamic mode (progressive levels)
        if game_mode == 'dynamic':
            # Total moves across all levels
            moves_label = font_text.render("Total Moves:", True, WHITE)
            moves_label_rect = moves_label.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
            screen.blit(moves_label, moves_label_rect)

            y_pos += 45
            moves_text = font_title.render(str(moves), True, GREEN)
            moves_rect = moves_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
            screen.blit(moves_text, moves_rect)

            # Current level moves
            y_pos += 60
            level_moves_label = font_small.render("Current Level:", True, WHITE)
            level_moves_label_rect = level_moves_label.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
            screen.blit(level_moves_label, level_moves_label_rect)

            y_pos += 35
            level_moves_text = font_text.render(str(level_moves), True, YELLOW)
            level_moves_rect = level_moves_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
            screen.blit(level_moves_text, level_moves_rect)
        else:
            # Normal mode - just show moves
            moves_label = font_text.render("Moves:", True, WHITE)
            moves_label_rect = moves_label.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
            screen.blit(moves_label, moves_label_rect)

            y_pos += 45
            moves_text = font_title.render(str(moves), True, GREEN)
            moves_rect = moves_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
            screen.blit(moves_text, moves_rect)

        # Total cost
        y_pos += 70
        cost_label = font_text.render("Total Cost:", True, WHITE)
        cost_label_rect = cost_label.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
        screen.blit(cost_label, cost_label_rect)

        y_pos += 45
        cost_text = font_title.render(str(total_cost), True, YELLOW)
        cost_rect = cost_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
        screen.blit(cost_text, cost_rect)

        # Energy display (if energy constraint is enabled)
        if energy_constraint and player:
            y_pos += 70
            energy_label = font_text.render("Energy Remaining:", True, WHITE)
            energy_label_rect = energy_label.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
            screen.blit(energy_label, energy_label_rect)

            y_pos += 45
            remaining_energy = max(0, fuel_limit - total_cost)
            energy_percent = (remaining_energy / fuel_limit) * 100

            # Color based on energy level
            if energy_percent > 50:
                energy_color = GREEN
            elif energy_percent > 25:
                energy_color = YELLOW
            else:
                energy_color = RED

            energy_text = font_title.render(f"{remaining_energy}/{fuel_limit}", True, energy_color)
            energy_rect = energy_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
            screen.blit(energy_text, energy_rect)

        # Timer display (if timer is enabled)
        if timer_enabled:
            y_pos += 70
            timer_label = font_text.render("Time Remaining:", True, WHITE)
            timer_label_rect = timer_label.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
            screen.blit(timer_label, timer_label_rect)

            y_pos += 45
            # Color based on time remaining
            time_percent = (time_remaining / time_limit) * 100 if time_limit > 0 else 0
            if time_percent > 50:
                timer_color = GREEN
            elif time_percent > 25:
                timer_color = YELLOW
            else:
                timer_color = RED

            minutes = int(time_remaining // 60)
            seconds = int(time_remaining % 60)
            timer_text = font_title.render(f"{minutes}:{seconds:02d}", True, timer_color)
            timer_rect = timer_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
            screen.blit(timer_text, timer_rect)

        # Multi-goal mode specific UI
        if game_mode == 'multi-goal' and player:
            # Solo mode - show checkpoints in UI panel
            if player_mode != 'competitive':
                y_pos += 70
                checkpoint_label = font_text.render("Checkpoints:", True, WHITE)
                checkpoint_label_rect = checkpoint_label.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
                screen.blit(checkpoint_label, checkpoint_label_rect)

                y_pos += 45
                checkpoint_text = font_title.render(f"{player.checkpoints_collected}/{num_checkpoints}", True, (255, 200, 0))
                checkpoint_rect = checkpoint_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
                screen.blit(checkpoint_text, checkpoint_rect)

        # Terrain legend
        y_pos += 90

    # Win message or instructions
    if won and player_mode == 'solo':
        # Check if player actually won or lost (e.g., time expired)
        if loser == "Player":
            # Player lost (time ran out, out of energy, etc.)
            lose_text = font_title.render("GAME OVER!", True, RED)
            lose_rect = lose_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
            screen.blit(lose_text, lose_rect)
        else:
            # Player actually won
            win_text = font_title.render("YOU WIN!", True, YELLOW)
            win_rect = win_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
            screen.blit(win_text, win_rect)

        y_pos += 60
        restart_text = font_text.render("Press R to restart", True, WHITE)
        restart_rect = restart_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
        screen.blit(restart_text, restart_rect)
    elif not won:
        pass
        # # Controls
        # controls_title = font_text.render("Controls:", True, WHITE)
        # controls_rect = controls_title.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
        # screen.blit(controls_title, controls_rect)

        # y_pos += 40
        # controls = [
        #     "WASD/Arrows - Move",
        #     "R - New Maze",
        #     "ESC - Return to Menu"
        # ]
        # for control in controls:
        #     control_text = font_text.render(control, True, WHITE)
        #     control_rect = control_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
        #     screen.blit(control_text, control_rect)
        #     y_pos += 40


def find_start_position(maze):
    """Find the start position (marked as TERRAIN_START) in the maze"""
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == TERRAIN_START:
                return x, y
    # Default to (1, 1) if no start found
    return 1, 1


def generate_progressive_maze(width, height, goal_placement, level):
    """Generate a maze with difficulty based on the current level

    Args:
        width: Maze width
        height: Maze height
        goal_placement: Where to place the goal
        level: Current difficulty level (1-10+)

    Returns:
        Generated maze with difficulty scaled to level
    """
    # Generate base maze
    maze = generate_maze(width, height, goal_placement, 'explore', 0)

    # Clear all terrain variety from base maze (we'll add it back based on level)
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            if maze[y][x] in [TERRAIN_WATER, TERRAIN_MUD, TERRAIN_LAVA]:
                maze[y][x] = TERRAIN_GRASS

    # Level-based terrain replacement
    # Higher levels have more dangerous terrain
    grass_tiles = []
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            if maze[y][x] == TERRAIN_GRASS:
                # Don't modify start and goal areas
                if not (x == 1 and y == 1):  # Not start
                    goal_x = width - 2 if goal_placement == 'corner' else width // 2
                    goal_y = height - 2 if goal_placement == 'corner' else height // 2
                    if not (abs(x - goal_x) <= 2 and abs(y - goal_y) <= 2):  # Not near goal
                        grass_tiles.append((x, y))

    if not grass_tiles:
        return maze

    # Determine how many tiles to convert based on level
    # Level 1: 5% of grass, Level 5: 25%, Level 10+: 40%
    conversion_rate = min(0.05 + (level - 1) * 0.035, 0.40)
    num_conversions = int(len(grass_tiles) * conversion_rate)

    # Randomly select tiles to convert
    import random
    tiles_to_convert = random.sample(grass_tiles, min(num_conversions, len(grass_tiles)))

    for x, y in tiles_to_convert:
        # Obstacle distribution based on level
        rand = random.random()

        if level == 1:
            # Level 1: Only water (cost 3)
            maze[y][x] = TERRAIN_WATER
        elif level == 2:
            # Level 2: Water and some mud
            if rand < 0.7:
                maze[y][x] = TERRAIN_WATER
            else:
                maze[y][x] = TERRAIN_MUD
        elif level == 3:
            # Level 3: More mud appears
            if rand < 0.5:
                maze[y][x] = TERRAIN_WATER
            else:
                maze[y][x] = TERRAIN_MUD
        elif level >= 4:
            # Level 4+: Lava introduced (impassable)
            lava_chance = min(0.15 + (level - 4) * 0.05, 0.30)  # 15% at level 4, up to 30% at level 7+

            if rand < lava_chance:
                maze[y][x] = TERRAIN_LAVA
            elif rand < 0.5 + lava_chance / 2:
                maze[y][x] = TERRAIN_MUD
            else:
                maze[y][x] = TERRAIN_WATER

    return maze


def start(goal_placement='corner', game_mode='explore', num_checkpoints=5, player_mode='solo', fog_of_war=False, energy_constraint=False, fuel_limit=100, ai_turn_frequency=1, timer_enabled=False, time_limit=60):
    """Start the game

    Args:
        goal_placement: Where to place the goal ('corner' or 'center')
        game_mode: Game mode ('explore', 'dynamic', or 'multi-goal')
        num_checkpoints: Number of checkpoints for multi-goal mode
        player_mode: Player mode ('solo' or 'competitive')
        fog_of_war: Enable fog of war (limited vision)
        energy_constraint: Enable energy/fuel limit
        fuel_limit: Maximum fuel/energy available
        ai_turn_frequency: AI moves after every X player moves (competitive mode only)
        timer_enabled: Enable time limit
        time_limit: Time limit in seconds
    """
    # Generate maze (use progressive generation for dynamic mode starting at level 1)
    if game_mode == 'dynamic':
        maze = generate_progressive_maze(MAZE_WIDTH, MAZE_HEIGHT, goal_placement, 1)
    else:
        maze = generate_maze(MAZE_WIDTH, MAZE_HEIGHT, goal_placement, game_mode, num_checkpoints)

    # Find start position and create player
    start_x, start_y = find_start_position(maze)

    # Create player sprite (a small character on grass)
    player_sprite = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    # Draw a simple character (circle with outline)
    pygame.draw.circle(player_sprite, BLUE, (TILE_SIZE // 2, TILE_SIZE // 2), TILE_SIZE // 3)
    pygame.draw.circle(player_sprite, WHITE, (TILE_SIZE // 2, TILE_SIZE // 2), TILE_SIZE // 3, 2)

    # Set energy limit if constraint is enabled
    energy_limit = fuel_limit if energy_constraint else None
    player = Player(start_x, start_y, TILE_SIZE, player_sprite, BLUE, energy_limit)

    # Create AI agents in competitive mode
    ai_agents = []
    if player_mode == 'competitive':
        # Create one AI opponent starting at the same position as the player
        ai_color = RED
        ai_name = "AI Opponent"

        # AI starts at the same position as the player
        ai_x = start_x
        ai_y = start_y

        ai_agent = AIAgent(ai_x, ai_y, TILE_SIZE, ai_name, ai_color, energy_limit)

        # In multi-goal mode, find all checkpoints and initialize AI's checkpoint list
        if game_mode == 'multi-goal':
            checkpoints = []
            for y in range(len(maze)):
                for x in range(len(maze[0])):
                    if maze[y][x] == TERRAIN_CHECKPOINT:
                        checkpoints.append((x, y))
            ai_agent.remaining_checkpoints = checkpoints.copy()

        ai_agent.calculate_path(maze, fog_of_war)  # Calculate initial path with fog of war awareness
        ai_agents.append(ai_agent)

    # Create input controller
    input_controller = InputController(TILE_SIZE)

    moves = 0
    won = False

    loop(maze, player, input_controller, moves, won, goal_placement, game_mode, num_checkpoints, player_mode, ai_agents, fog_of_war, energy_constraint, fuel_limit, ai_turn_frequency, timer_enabled, time_limit)
    print("=" * 50)
    print("PYGAME STOPPED".center(50))
    print("=" * 50)


def loop(maze, player, input_controller, moves, won, goal_placement, game_mode='explore', num_checkpoints=3, player_mode='solo', ai_agents=None, fog_of_war=False, energy_constraint=False, fuel_limit=100, ai_turn_frequency=1, timer_enabled=False, time_limit=60):
    """Main game loop"""
    run = True
    if ai_agents is None:
        ai_agents = []

    # Progressive levels for dynamic mode
    current_level = 1
    level_moves = 0  # Moves in current level
    total_moves = 0  # Total moves across all levels

    # Track player moves for AI turn frequency in competitive mode
    player_move_counter = 0

    # Track checkpoint collection for multi-goal mode
    all_checkpoints = set()  # All checkpoint positions
    player_collected_checkpoints = set()  # Checkpoints collected by player
    ai_collected_checkpoints = set()  # Checkpoints collected by AI
    if game_mode == 'multi-goal':
        for y in range(len(maze)):
            for x in range(len(maze[0])):
                if maze[y][x] == TERRAIN_CHECKPOINT:
                    all_checkpoints.add((x, y))

    # Track explored tiles for fog of war (stores all tiles the player has seen)
    explored_tiles = set()
    if fog_of_war:
        # Start with player's initial vision
        vision_range = 5  # Player can see 5 tiles in each direction
        for dy in range(-vision_range, vision_range + 1):
            for dx in range(-vision_range, vision_range + 1):
                tile_x = player.tile_x + dx
                tile_y = player.tile_y + dy
                if 0 <= tile_x < len(maze[0]) and 0 <= tile_y < len(maze):
                    # Use Manhattan distance for vision
                    if abs(dx) + abs(dy) <= vision_range:
                        explored_tiles.add((tile_x, tile_y))

    # For visualizing AI moves
    ai_animation_queue = []  # Queue of AI agents to animate
    ai_animation_delay = 0  # Delay counter for smoother animation
    ai_moves_remaining = 0  # Track how many moves the AI needs to make this turn
    winner = None  # Track who won in competitive mode
    loser = None  # Track who lost (ran out of energy)

    # Timer tracking
    start_time = pygame.time.get_ticks() if timer_enabled else None
    time_expired = False

    while run:
        clock.tick(60)  # 60 FPS

        # Check timer
        if timer_enabled and not won and not time_expired:
            elapsed_time = (pygame.time.get_ticks() - start_time) / 1000  # Convert to seconds
            if elapsed_time >= time_limit:
                time_expired = True
                won = True
                if player_mode == 'competitive':
                    # Check if anyone is at the goal when time expires
                    player_at_goal = player.is_at_goal(maze)
                    ai_at_goal = any(ai.finished for ai in ai_agents)

                    if player_at_goal and not ai_at_goal:
                        # Player reached goal, AI didn't
                        winner = "Player"
                        print(f"\n⏰ Time's up! ⏰")
                        print(f"Player wins!")
                    elif ai_at_goal and not player_at_goal:
                        # AI reached goal, player didn't
                        winner = "AI Opponent"
                        loser = "Player"
                        print(f"\n⏰ Time's up! ⏰")
                        print(f"AI Opponent wins!")
                    elif player_at_goal and ai_at_goal:
                        # Both at goal - it's a tie (could determine by moves/cost)
                        winner = "No one"
                        print(f"\n⏰ Time's up! ⏰")
                        print(f"It's a tie!")
                    else:
                        # Neither at goal
                        winner = "No one"
                        print(f"\n⏰ Time's up! ⏰")
                        print(f"No one wins!")
                else:
                    # Solo mode - player just loses
                    loser = "Player"
                    winner = None
                    print(f"\n⏰ Time's up! ⏰")
                    print(f"Game Over!")

        # Process AI animation queue (in competitive mode)
        if player_mode == 'competitive' and ai_animation_queue and not won:
            ai_animation_delay += 1

            # Make AI moves at a slower pace for visibility
            if ai_animation_delay >= 15:  # Delay between AI moves
                ai_animation_delay = 0

                if ai_animation_queue:
                    current_ai = ai_animation_queue[0]

                    # Only recalculate path if needed (empty, blocked, or checkpoint collected)
                    should_recalculate = False
                    if not current_ai.path:
                        should_recalculate = True
                    elif fog_of_war:
                        # Check if next tile in path is still valid (not blocked/unexplored)
                        next_tile = current_ai.path[0]
                        if next_tile not in current_ai.known_maze:
                            should_recalculate = True
                        elif not is_passable(current_ai.known_maze[next_tile]):
                            should_recalculate = True

                    if should_recalculate:
                        current_ai.calculate_path(maze, fog_of_war)

                    # Track AI position before move (for checkpoint detection)
                    ai_prev_checkpoints = current_ai.checkpoints_collected

                    # Make one move
                    moved = current_ai.make_move(maze)

                    # Update AI vision after moving (for fog of war)
                    if fog_of_war and moved:
                        current_ai.update_vision(maze, fog_of_war=fog_of_war)

                    # Check if AI collected a checkpoint this move (in multi-goal mode)
                    if game_mode == 'multi-goal' and current_ai.checkpoints_collected > ai_prev_checkpoints:
                        ai_collected_checkpoints.add((current_ai.tile_x, current_ai.tile_y))
                        # Recalculate path since target changed (new checkpoint or goal)
                        current_ai.calculate_path(maze, fog_of_war)

                    # Check if AI ran out of energy
                    if energy_constraint and current_ai.out_of_energy and loser is None:
                        loser = current_ai.name
                        winner = "Player"  # Player wins if AI runs out of energy
                        won = True
                        print(f"\n⚡ {current_ai.name} ran out of energy! ⚡")
                        print(f"Player wins!")

                    # Check if this AI won
                    if current_ai.finished and winner is None:
                        winner = current_ai.name
                        won = True
                        print(f"\n🏁 {current_ai.name} wins! 🏁")
                        print(f"Moves: {current_ai.moves}")
                        print(f"Total Cost: {current_ai.total_cost}")

                    # Decrement moves remaining for this AI turn
                    ai_moves_remaining -= 1

                    # Remove AI from queue after completing all moves for this turn
                    if ai_moves_remaining <= 0 or current_ai.finished or current_ai.out_of_energy:
                        ai_animation_queue.pop(0)
                        ai_moves_remaining = 0

        # Update mouse movement (if mouse is held)
        if not won and not ai_animation_queue:  # Don't allow player movement during AI animation
            mouse_move_cost = input_controller.update_mouse_movement(player, maze, delay_frames=5)
            if mouse_move_cost > 0:
                moves += 1
                player_move_counter += 1  # Increment turn counter

                # After player moves in competitive mode, queue AI moves based on turn frequency
                if player_mode == 'competitive' and player_move_counter >= ai_turn_frequency:
                    ai_moves_remaining = player_move_counter  # AI gets same number of moves as player made
                    player_move_counter = 0  # Reset counter
                    for ai in ai_agents:
                        if not ai.finished and ai not in ai_animation_queue:
                            # Just add to queue, path will be calculated when AI moves
                            ai_animation_queue.append(ai)

                # Track moves based on game mode
                if game_mode == 'dynamic':
                    level_moves += 1
                    total_moves += 1
                else:
                    moves += 1

                # Multi-goal mode: Check if landed on checkpoint
                if game_mode == 'multi-goal' and maze[player.tile_y][player.tile_x] == TERRAIN_CHECKPOINT:
                    player.checkpoints_collected += 1
                    # Don't reset cost - keep accumulating
                    # player.exploration_cost += player.total_cost
                    # player.total_cost = 0
                    player_collected_checkpoints.add((player.tile_x, player.tile_y))  # Track collection for rendering
                    # Don't convert checkpoint to grass - let rendering handle visibility
                    # maze[player.tile_y][player.tile_x] = TERRAIN_GRASS
                    print(f"✓ Checkpoint collected! ({player.checkpoints_collected}/{num_checkpoints})")

                # Check if player ran out of energy
                if energy_constraint and player.out_of_energy and loser is None:
                    loser = "Player"
                    won = True
                    if player_mode == 'competitive':
                        winner = "AI Opponent"  # AI wins if player runs out of energy
                        print(f"\n⚡ You ran out of energy! ⚡")
                        print(f"AI Opponent wins!")
                    else:
                        winner = None  # Solo mode - player just loses
                        print(f"\n⚡ You ran out of energy! ⚡")
                        print(f"Game Over!")

                # Check if won
                win_condition = player.is_at_goal(maze)
                if game_mode == 'multi-goal':
                    win_condition = win_condition and player.checkpoints_collected >= num_checkpoints

                if win_condition and winner is None and not player.out_of_energy:
                    # Dynamic mode: Progress to next level instead of ending
                    if game_mode == 'dynamic':
                        # In competitive mode, show winner first
                        if player_mode == 'competitive':
                            won = True
                            winner = "Player"
                            print(f"\n🎉 Level {current_level} completed! Player wins! 🎉")
                            print(f"Level Moves: {level_moves}")

                            # Display winner screen briefly
                            display_moves = total_moves if game_mode == 'dynamic' else moves
                            draw_ui(screen, TOTAL_WINDOW_WIDTH, TOTAL_WINDOW_HEIGHT, display_moves, player.total_cost, won, game_mode, player, num_checkpoints, player_mode, ai_agents, winner, fog_of_war, energy_constraint, fuel_limit, current_level, level_moves, player_collected_checkpoints, ai_collected_checkpoints, timer_enabled, time_remaining, time_limit, loser)
                            pygame.display.flip()
                            pygame.time.wait(2000)  # Show winner for 2 seconds

                            # Reset for next level
                            won = False
                            winner = None
                        else:
                            print(f"✓ Level {current_level} completed! Moves: {level_moves}")

                        current_level += 1
                        level_moves = 0

                        # Generate new progressive maze with increased difficulty
                        maze = generate_progressive_maze(MAZE_WIDTH, MAZE_HEIGHT, goal_placement, current_level)
                        start_x, start_y = find_start_position(maze)

                        # Reset player position but keep total stats
                        player.tile_x = start_x
                        player.tile_y = start_y

                        # Reset AI position and state in competitive mode
                        if player_mode == 'competitive':
                            for ai in ai_agents:
                                ai.tile_x = start_x
                                ai.tile_y = start_y
                                ai.finished = False
                                ai.path = []
                                ai.calculate_path(maze, fog_of_war)
                            # Clear AI animation queue
                            ai_animation_queue.clear()
                            ai_moves_remaining = 0
                            player_move_counter = 0

                        # Reset explored tiles for fog of war
                        if fog_of_war:
                            explored_tiles.clear()
                            vision_range = 5
                            for dy in range(-vision_range, vision_range + 1):
                                for dx in range(-vision_range, vision_range + 1):
                                    tile_x = player.tile_x + dx
                                    tile_y = player.tile_y + dy
                                    if 0 <= tile_x < len(maze[0]) and 0 <= tile_y < len(maze):
                                        if abs(dx) + abs(dy) <= vision_range:
                                            explored_tiles.add((tile_x, tile_y))

                        print(f"→ Starting Level {current_level}")
                    else:
                        # Non-dynamic modes: End the game
                        won = True
                        winner = "Player"
                        print(f"\n🎉 You won! 🎉")
                        print(f"Moves: {moves}")
                        print(f"Total Cost: {player.total_cost}\n")

        # Fill background
        screen.fill(BLACK)

        # Update explored tiles if fog of war is enabled
        if fog_of_war:
            vision_range = 5
            for dy in range(-vision_range, vision_range + 1):
                for dx in range(-vision_range, vision_range + 1):
                    tile_x = player.tile_x + dx
                    tile_y = player.tile_y + dy
                    if 0 <= tile_x < len(maze[0]) and 0 <= tile_y < len(maze):
                        # Use Manhattan distance for vision
                        if abs(dx) + abs(dy) <= vision_range:
                            explored_tiles.add((tile_x, tile_y))

        # Draw maze (with or without fog of war)
        # In competitive multi-goal mode, only hide checkpoints collected by BOTH player and AI
        if game_mode == 'multi-goal' and player_mode == 'competitive':
            # Checkpoint is hidden only if both player and AI collected it
            collected_checkpoints = player_collected_checkpoints & ai_collected_checkpoints
        elif game_mode == 'multi-goal':
            # Solo mode: hide checkpoints collected by player
            collected_checkpoints = player_collected_checkpoints
        else:
            # Non multi-goal mode
            collected_checkpoints = set()

        if fog_of_war:
            draw_maze_with_fog(screen, maze, TILE_SIZE, player, explored_tiles, all_checkpoints=all_checkpoints, collected_checkpoints=collected_checkpoints)
        else:
            draw_maze(screen, maze, TILE_SIZE, all_checkpoints=all_checkpoints, collected_checkpoints=collected_checkpoints)

        # Draw path visualization (if mouse is held)
        if fog_of_war:
            input_controller.draw_path(screen, TILE_SIZE, player, explored_tiles)
        else:
            input_controller.draw_path(screen, TILE_SIZE)

        # Draw AI agents and their paths (in competitive mode)
        if player_mode == 'competitive':
            for ai in ai_agents:
                # Don't draw the AI's path (hide their strategy)
                # if not ai.finished:
                #     ai.draw_path(screen, TILE_SIZE)
                ai.draw(screen)

        # Draw player
        player.draw(screen)

        # Calculate time remaining for display
        if timer_enabled:
            elapsed_time = (pygame.time.get_ticks() - start_time) / 1000
            time_remaining = max(0, time_limit - elapsed_time)
        else:
            time_remaining = 0

        # Draw UI (pass appropriate moves count based on game mode)
        display_moves = total_moves if game_mode == 'dynamic' else moves
        draw_ui(screen, TOTAL_WINDOW_WIDTH, TOTAL_WINDOW_HEIGHT, display_moves, player.total_cost, won, game_mode, player, num_checkpoints, player_mode, ai_agents, winner, fog_of_war, energy_constraint, fuel_limit, current_level, level_moves, player_collected_checkpoints, ai_collected_checkpoints, timer_enabled, time_remaining, time_limit, loser)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # Handle mouse input
            if not won and not ai_animation_queue:
                input_controller.handle_mouse_input(event, player, maze)

            # Handle keyboard input
            if not won and not ai_animation_queue:  # Don't allow input during AI animation
                move_cost = input_controller.handle_keyboard_input(event, player, maze)

                if move_cost > 0:
                    player_move_counter += 1  # Increment turn counter

                    # Track moves based on game mode
                    if game_mode == 'dynamic':
                        level_moves += 1
                        total_moves += 1
                    else:
                        moves += 1

                    # After player moves in competitive mode, queue AI moves based on turn frequency
                    if player_mode == 'competitive' and player_move_counter >= ai_turn_frequency:
                        ai_moves_remaining = player_move_counter  # AI gets same number of moves as player made
                        player_move_counter = 0  # Reset counter
                        for ai in ai_agents:
                            if not ai.finished and ai not in ai_animation_queue:
                                # Just add to queue, path will be calculated when AI moves
                                ai_animation_queue.append(ai)

                    # Multi-goal mode: Check if landed on checkpoint
                    if game_mode == 'multi-goal' and maze[player.tile_y][player.tile_x] == TERRAIN_CHECKPOINT:
                        player.checkpoints_collected += 1
                        # Don't reset cost - keep accumulating
                        # player.exploration_cost += player.total_cost
                        # player.total_cost = 0
                        player_collected_checkpoints.add((player.tile_x, player.tile_y))  # Track collection for rendering
                        # Don't convert checkpoint to grass - let rendering handle visibility
                        # maze[player.tile_y][player.tile_x] = TERRAIN_GRASS
                        print(f"✓ Checkpoint collected! ({player.checkpoints_collected}/{num_checkpoints})")

                    # Check if player ran out of energy
                    if energy_constraint and player.out_of_energy and loser is None:
                        loser = "Player"
                        won = True
                        if player_mode == 'competitive':
                            winner = "AI Opponent"  # AI wins if player runs out of energy
                            print(f"\n⚡ You ran out of energy! ⚡")
                            print(f"AI Opponent wins!")
                        else:
                            winner = None  # Solo mode - player just loses
                            print(f"\n⚡ You ran out of energy! ⚡")
                            if game_mode == 'dynamic':
                                print(f"Reached Level {current_level}")
                            print(f"Game Over!")

                    # Check if won
                    win_condition = player.is_at_goal(maze)
                    if game_mode == 'multi-goal':
                        win_condition = win_condition and player.checkpoints_collected >= num_checkpoints

                    if win_condition and winner is None and not player.out_of_energy:
                        # Dynamic mode: Progress to next level instead of ending
                        if game_mode == 'dynamic':
                            # In competitive mode, show winner first
                            if player_mode == 'competitive':
                                won = True
                                winner = "Player"
                                print(f"\n🎉 Level {current_level} completed! Player wins! 🎉")
                                print(f"Level Moves: {level_moves}")

                                # Display winner screen briefly
                                display_moves = total_moves if game_mode == 'dynamic' else moves
                                draw_ui(screen, TOTAL_WINDOW_WIDTH, TOTAL_WINDOW_HEIGHT, display_moves, player.total_cost, won, game_mode, player, num_checkpoints, player_mode, ai_agents, winner, fog_of_war, energy_constraint, fuel_limit, current_level, level_moves, player_collected_checkpoints, ai_collected_checkpoints, timer_enabled, time_remaining, time_limit, loser)
                                pygame.display.flip()
                                pygame.time.wait(2000)  # Show winner for 2 seconds

                                # Reset for next level
                                won = False
                                winner = None
                            else:
                                print(f"✓ Level {current_level} completed! Moves: {level_moves}")

                            current_level += 1
                            level_moves = 0

                            # Generate new progressive maze with increased difficulty
                            maze = generate_progressive_maze(MAZE_WIDTH, MAZE_HEIGHT, goal_placement, current_level)
                            start_x, start_y = find_start_position(maze)

                            # Reset player position but keep total stats
                            player.tile_x = start_x
                            player.tile_y = start_y

                            # Reset AI position and state in competitive mode
                            if player_mode == 'competitive':
                                for ai in ai_agents:
                                    ai.tile_x = start_x
                                    ai.tile_y = start_y
                                    ai.finished = False
                                    ai.path = []
                                    ai.calculate_path(maze, fog_of_war)
                                # Clear AI animation queue
                                ai_animation_queue.clear()
                                ai_moves_remaining = 0
                                player_move_counter = 0

                            # Reset explored tiles for fog of war
                            if fog_of_war:
                                explored_tiles.clear()
                                vision_range = 5
                                for dy in range(-vision_range, vision_range + 1):
                                    for dx in range(-vision_range, vision_range + 1):
                                        tile_x = player.tile_x + dx
                                        tile_y = player.tile_y + dy
                                        if 0 <= tile_x < len(maze[0]) and 0 <= tile_y < len(maze):
                                            if abs(dx) + abs(dy) <= vision_range:
                                                explored_tiles.add((tile_x, tile_y))

                            print(f"→ Starting Level {current_level}")
                        else:
                            # Non-dynamic modes: End the game
                            won = True
                            winner = "Player"
                            print(f"\n🎉 You won! 🎉")
                            print(f"Moves: {moves}")
                            print(f"Total Cost: {player.total_cost}\n")

            # Restart with new maze
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                # Generate new maze with same settings
                if game_mode == 'dynamic':
                    # Start from level 1 on restart
                    maze = generate_progressive_maze(MAZE_WIDTH, MAZE_HEIGHT, goal_placement, 1)
                else:
                    maze = generate_maze(MAZE_WIDTH, MAZE_HEIGHT, goal_placement, game_mode, num_checkpoints)
                start_x, start_y = find_start_position(maze)

                # Recreate player sprite
                player_sprite = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                pygame.draw.circle(player_sprite, BLUE, (TILE_SIZE // 2, TILE_SIZE // 2), TILE_SIZE // 3)
                pygame.draw.circle(player_sprite, WHITE, (TILE_SIZE // 2, TILE_SIZE // 2), TILE_SIZE // 3, 2)

                energy_limit = fuel_limit if energy_constraint else None
                player = Player(start_x, start_y, TILE_SIZE, player_sprite, BLUE, energy_limit)
                input_controller = InputController(TILE_SIZE)
                moves = 0
                won = False
                winner = None
                loser = None
                ai_animation_queue = []

                # Reset timer
                if timer_enabled:
                    start_time = pygame.time.get_ticks()
                    time_expired = False

                # Reset progressive level stats in dynamic mode
                if game_mode == 'dynamic':
                    current_level = 1
                    level_moves = 0
                    total_moves = 0

                # Reset checkpoint tracking for multi-goal mode
                if game_mode == 'multi-goal':
                    all_checkpoints.clear()
                    player_collected_checkpoints.clear()
                    ai_collected_checkpoints.clear()
                    # Repopulate with new checkpoints from regenerated maze
                    for y in range(len(maze)):
                        for x in range(len(maze[0])):
                            if maze[y][x] == TERRAIN_CHECKPOINT:
                                all_checkpoints.add((x, y))

                # Reset fog of war
                if fog_of_war:
                    explored_tiles.clear()
                    vision_range = 5
                    for dy in range(-vision_range, vision_range + 1):
                        for dx in range(-vision_range, vision_range + 1):
                            tile_x = start_x + dx
                            tile_y = start_y + dy
                            if 0 <= tile_x < len(maze[0]) and 0 <= tile_y < len(maze):
                                if abs(dx) + abs(dy) <= vision_range:
                                    explored_tiles.add((tile_x, tile_y))

                # Recreate AI agents in competitive mode
                if player_mode == 'competitive':
                    ai_agents = []
                    # Create one AI opponent starting at the same position
                    ai_color = RED
                    ai_name = "AI Opponent"

                    ai_x = start_x
                    ai_y = start_y

                    ai_agent = AIAgent(ai_x, ai_y, TILE_SIZE, ai_name, ai_color, energy_limit)

                    # In multi-goal mode, find all checkpoints and initialize AI's checkpoint list
                    if game_mode == 'multi-goal':
                        checkpoints = []
                        for y in range(len(maze)):
                            for x in range(len(maze[0])):
                                if maze[y][x] == TERRAIN_CHECKPOINT:
                                    checkpoints.append((x, y))
                        ai_agent.remaining_checkpoints = checkpoints.copy()

                    ai_agent.calculate_path(maze, fog_of_war)
                    ai_agents.append(ai_agent)

            # Return to menu
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                run = False  # Exit game loop to return to menu

        pygame.display.flip()


if __name__ == "__main__":
    start('corner')  # Default to corner placement when running directly
    pygame.quit()  # Only quit pygame when running standalone
