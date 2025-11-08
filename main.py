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

    def __init__(self, x, y, tile_size, sprite=None, color=BLUE):
        self.tile_x = x
        self.tile_y = y
        self.tile_size = tile_size
        self.speed = 1  # Tiles per move
        self.color = color
        self.sprite = sprite
        self.total_cost = 0  # Track total movement cost
        self.exploration_cost = 0  # Total exploration cost (for multi-goal mode)
        self.checkpoints_collected = 0  # Number of checkpoints collected

    def move(self, dx, dy, maze):
        """Move player if the destination is passable, return cost of move"""
        new_x = self.tile_x + dx
        new_y = self.tile_y + dy

        # Check bounds
        if not (0 <= new_y < len(maze) and 0 <= new_x < len(maze[0])):
            return 0

        terrain = maze[new_y][new_x]

        # Check if terrain is passable
        if is_passable(terrain):
            self.tile_x = new_x
            self.tile_y = new_y
            move_cost = get_terrain_cost(terrain)
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


def draw_maze_with_fog(screen, maze, tile_size, player, explored_tiles, vision_range=5):
    """Draw the maze with fog of war - only showing tiles within vision range or previously explored"""
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)

            # Calculate distance from player (Manhattan distance)
            distance = abs(x - player.tile_x) + abs(y - player.tile_y)
            is_visible = distance <= vision_range
            is_explored = (x, y) in explored_tiles

            if is_visible or is_explored:
                # Draw the tile normally
                if cell == TERRAIN_GRASS:  # Grass - cost 1
                    screen.blit(grass_sprite, rect)
                elif cell == TERRAIN_WALL:  # Wall - impassable
                    screen.blit(wall_sprite, rect)
                elif cell == TERRAIN_WATER:  # Water - cost 3
                    screen.blit(water_sprite, rect)
                elif cell == TERRAIN_MUD:  # Mud - cost 5
                    screen.blit(mud_sprite, rect)
                elif cell == TERRAIN_LAVA:  # Lava - impassable
                    screen.blit(lava_sprite, rect)
                elif cell == TERRAIN_CHECKPOINT:  # Checkpoint - resets cost
                    screen.blit(grass_sprite, rect)
                    # Draw checkpoint marker (yellow star)
                    overlay = pygame.Surface((tile_size, tile_size))
                    overlay.fill(YELLOW)
                    overlay.set_alpha(100)
                    screen.blit(overlay, rect)
                    # Draw star shape
                    pygame.draw.circle(screen, YELLOW, rect.center, tile_size // 4, 3)
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


def draw_maze(screen, maze, tile_size):
    """Draw the maze on screen using sprites with different terrain types"""
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)

            if cell == TERRAIN_GRASS:  # Grass - cost 1
                screen.blit(grass_sprite, rect)
            elif cell == TERRAIN_WALL:  # Wall - impassable
                screen.blit(wall_sprite, rect)
            elif cell == TERRAIN_WATER:  # Water - cost 3
                screen.blit(water_sprite, rect)
            elif cell == TERRAIN_MUD:  # Mud - cost 5
                screen.blit(mud_sprite, rect)
            elif cell == TERRAIN_LAVA:  # Lava - impassable
                screen.blit(lava_sprite, rect)
            elif cell == TERRAIN_CHECKPOINT:  # Checkpoint - resets cost
                screen.blit(grass_sprite, rect)
                # Draw checkpoint marker (yellow star)
                overlay = pygame.Surface((tile_size, tile_size))
                overlay.fill(YELLOW)
                overlay.set_alpha(100)
                screen.blit(overlay, rect)
                # Draw star shape
                pygame.draw.circle(screen, YELLOW, rect.center, tile_size // 4, 3)
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


def draw_ui(screen, width, height, moves, total_cost, won, game_mode='explore', player=None, num_checkpoints=3, player_mode='solo', ai_agents=None, winner=None, fog_of_war=False):
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
    title_text = font_title.render("MAZE RUNNER", True, YELLOW)
    title_rect = title_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
    screen.blit(title_text, title_rect)

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
        player_stats = font_small.render(f"Moves: {moves}  Cost: {total_cost}", True, WHITE)
        player_stats_rect = player_stats.get_rect(x=ui_x_start + 50, y=y_pos)
        screen.blit(player_stats, player_stats_rect)

        # AI agents stats
        y_pos += 50
        for ai in ai_agents:
            status = "FINISHED!" if ai.finished else "Running"
            ai_label = font_text.render(f"{ai.name}:", True, ai.color)
            ai_label_rect = ai_label.get_rect(x=ui_x_start + 30, y=y_pos)
            screen.blit(ai_label, ai_label_rect)

            y_pos += 30
            ai_stats = font_tiny.render(f"Moves: {ai.moves}  Cost: {ai.total_cost}", True, WHITE)
            ai_stats_rect = ai_stats.get_rect(x=ui_x_start + 50, y=y_pos)
            screen.blit(ai_stats, ai_stats_rect)

            y_pos += 25
            ai_status = font_tiny.render(status, True, GREEN if ai.finished else GRAY)
            ai_status_rect = ai_status.get_rect(x=ui_x_start + 50, y=y_pos)
            screen.blit(ai_status, ai_status_rect)

            y_pos += 35

        # Winner announcement
        if won and winner:
            y_pos += 20
            winner_color = BLUE if winner == "Player" else RED
            win_text = font_title.render(f"{winner} WINS!", True, winner_color)
            win_rect = win_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
            screen.blit(win_text, win_rect)
            y_pos += 70

    else:
        # Solo mode UI (original)
        # Moves counter
        y_pos += 100
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

        # Multi-goal mode specific UI
        if game_mode == 'multi-goal' and player:
            # Checkpoints collected
            y_pos += 70
            checkpoint_label = font_text.render("Checkpoints:", True, WHITE)
            checkpoint_label_rect = checkpoint_label.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
            screen.blit(checkpoint_label, checkpoint_label_rect)

            y_pos += 45
            checkpoint_text = font_title.render(f"{player.checkpoints_collected}/{num_checkpoints}", True, (255, 200, 0))
            checkpoint_rect = checkpoint_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
            screen.blit(checkpoint_text, checkpoint_rect)

            # Exploration cost
            y_pos += 70
            explore_label = font_text.render("Exploration Cost:", True, WHITE)
            explore_label_rect = explore_label.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
            screen.blit(explore_label, explore_label_rect)

            y_pos += 45
            explore_text = font_title.render(str(player.exploration_cost), True, (100, 200, 255))
            explore_rect = explore_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
            screen.blit(explore_text, explore_rect)

        # Terrain legend
        y_pos += 90

    # Win message or instructions
    if won and player_mode == 'solo':
        win_text = font_title.render("YOU WIN!", True, YELLOW)
        win_rect = win_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
        screen.blit(win_text, win_rect)

        y_pos += 60
        restart_text = font_text.render("Press R to restart", True, WHITE)
        restart_rect = restart_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
        screen.blit(restart_text, restart_rect)
    elif not won:
        # Controls
        controls_title = font_text.render("Controls:", True, WHITE)
        controls_rect = controls_title.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
        screen.blit(controls_title, controls_rect)

        y_pos += 40
        controls = [
            "WASD/Arrows - Move",
            "R - New Maze",
            "ESC - Return to Menu"
        ]
        for control in controls:
            control_text = font_text.render(control, True, WHITE)
            control_rect = control_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
            screen.blit(control_text, control_rect)
            y_pos += 40


def find_start_position(maze):
    """Find the start position (marked as TERRAIN_START) in the maze"""
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == TERRAIN_START:
                return x, y
    # Default to (1, 1) if no start found
    return 1, 1


def spawn_dynamic_obstacles(maze, player, moves):
    """Spawn obstacles dynamically based on player movement (for dynamic mode)

    Args:
        maze: The maze array
        player: The player object
        moves: Number of moves made
    """
    # Spawn obstacles every 4 moves
    if moves % 4 != 0:
        return

    # Calculate distance to goal
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

    player_distance_to_goal = abs(player.tile_x - goal_x) + abs(player.tile_y - goal_y)

    # Find all grass tiles that could become obstacles
    valid_positions = []
    for y in range(1, len(maze) - 1):
        for x in range(1, len(maze[0]) - 1):
            if maze[y][x] == TERRAIN_GRASS:
                # Don't place obstacles too close to player (within 3 tiles)
                if abs(x - player.tile_x) + abs(y - player.tile_y) > 3:
                    # Don't place obstacles on the goal
                    if not (x == goal_x and y == goal_y):
                        valid_positions.append((x, y))

    if not valid_positions:
        return

    # Spawn 1-2 obstacles per trigger
    num_obstacles = random.randint(1, 2)
    num_obstacles = min(num_obstacles, len(valid_positions))

    for _ in range(num_obstacles):
        x, y = random.choice(valid_positions)
        valid_positions.remove((x, y))

        # Determine obstacle type based on distance to goal
        # Closer to goal = more dangerous obstacles
        rand = random.random()

        if player_distance_to_goal < 15:  # Close to goal
            if rand < 0.3:  # 30% lava
                maze[y][x] = TERRAIN_LAVA
            elif rand < 0.6:  # 30% mud
                maze[y][x] = TERRAIN_MUD
            else:  # 40% water
                maze[y][x] = TERRAIN_WATER
        elif player_distance_to_goal < 30:  # Medium distance
            if rand < 0.15:  # 15% lava
                maze[y][x] = TERRAIN_LAVA
            elif rand < 0.45:  # 30% mud
                maze[y][x] = TERRAIN_MUD
            else:  # 55% water
                maze[y][x] = TERRAIN_WATER
        else:  # Far from goal
            if rand < 0.05:  # 5% lava
                maze[y][x] = TERRAIN_LAVA
            elif rand < 0.35:  # 30% mud
                maze[y][x] = TERRAIN_MUD
            else:  # 65% water
                maze[y][x] = TERRAIN_WATER


def start(goal_placement='corner', game_mode='explore', num_checkpoints=5, player_mode='solo', fog_of_war=False):
    """Start the game

    Args:
        goal_placement: Where to place the goal ('corner' or 'center')
        game_mode: Game mode ('explore', 'dynamic', or 'multi-goal')
        num_checkpoints: Number of checkpoints for multi-goal mode
        player_mode: Player mode ('solo' or 'competitive')
        fog_of_war: Enable fog of war (limited vision)
    """
    # Generate maze
    maze = generate_maze(MAZE_WIDTH, MAZE_HEIGHT, goal_placement, game_mode, num_checkpoints)

    # Find start position and create player
    start_x, start_y = find_start_position(maze)

    # Create player sprite (a small character on grass)
    player_sprite = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    # Draw a simple character (circle with outline)
    pygame.draw.circle(player_sprite, BLUE, (TILE_SIZE // 2, TILE_SIZE // 2), TILE_SIZE // 3)
    pygame.draw.circle(player_sprite, WHITE, (TILE_SIZE // 2, TILE_SIZE // 2), TILE_SIZE // 3, 2)

    player = Player(start_x, start_y, TILE_SIZE, player_sprite, BLUE)

    # Create AI agents in competitive mode
    ai_agents = []
    if player_mode == 'competitive':
        # Create one AI opponent starting at the same position as the player
        ai_color = RED
        ai_name = "AI Opponent"

        # AI starts at the same position as the player
        ai_x = start_x
        ai_y = start_y

        ai_agent = AIAgent(ai_x, ai_y, TILE_SIZE, ai_name, ai_color)
        ai_agent.calculate_path(maze, fog_of_war)  # Calculate initial path with fog of war awareness
        ai_agents.append(ai_agent)

    # Create input controller
    input_controller = InputController(TILE_SIZE)

    moves = 0
    won = False

    loop(maze, player, input_controller, moves, won, goal_placement, game_mode, num_checkpoints, player_mode, ai_agents, fog_of_war)
    print("=" * 50)
    print("PYGAME STOPPED".center(50))
    print("=" * 50)


def loop(maze, player, input_controller, moves, won, goal_placement, game_mode='explore', num_checkpoints=3, player_mode='solo', ai_agents=None, fog_of_war=False):
    """Main game loop"""
    run = True
    if ai_agents is None:
        ai_agents = []

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
    winner = None  # Track who won in competitive mode

    while run:
        clock.tick(60)  # 60 FPS

        # Process AI animation queue (in competitive mode)
        if player_mode == 'competitive' and ai_animation_queue and not won:
            ai_animation_delay += 1

            # Make AI moves at a slower pace for visibility
            if ai_animation_delay >= 15:  # Delay between AI moves
                ai_animation_delay = 0

                if ai_animation_queue:
                    current_ai = ai_animation_queue[0]

                    # Recalculate path before each move (works with dynamic obstacles and fog of war)
                    current_ai.calculate_path(maze, fog_of_war)

                    # Make one move
                    moved = current_ai.make_move(maze)

                    # Check if this AI won
                    if current_ai.finished and winner is None:
                        winner = current_ai.name
                        won = True
                        print(f"\n🏁 {current_ai.name} wins! 🏁")
                        print(f"Moves: {current_ai.moves}")
                        print(f"Total Cost: {current_ai.total_cost}")

                    # Always remove AI from queue after one move (turn-based)
                    ai_animation_queue.pop(0)

        # Update mouse movement (if mouse is held)
        if not won and not ai_animation_queue:  # Don't allow player movement during AI animation
            mouse_move_cost = input_controller.update_mouse_movement(player, maze, delay_frames=5)
            if mouse_move_cost > 0:
                moves += 1

                # After player moves in competitive mode, queue AI moves
                if player_mode == 'competitive':
                    for ai in ai_agents:
                        if not ai.finished and ai not in ai_animation_queue:
                            # Just add to queue, path will be calculated when AI moves
                            ai_animation_queue.append(ai)

                # Dynamic mode: Spawn obstacles as player moves
                if game_mode == 'dynamic':
                    spawn_dynamic_obstacles(maze, player, moves)

                # Multi-goal mode: Check if landed on checkpoint
                if game_mode == 'multi-goal' and maze[player.tile_y][player.tile_x] == TERRAIN_CHECKPOINT:
                    player.checkpoints_collected += 1
                    player.exploration_cost += player.total_cost
                    player.total_cost = 0
                    maze[player.tile_y][player.tile_x] = TERRAIN_GRASS  # Convert checkpoint to grass
                    print(f"✓ Checkpoint collected! ({player.checkpoints_collected}/{num_checkpoints})")

                # Check if won
                win_condition = player.is_at_goal(maze)
                if game_mode == 'multi-goal':
                    win_condition = win_condition and player.checkpoints_collected >= num_checkpoints

                if win_condition and winner is None:
                    won = True
                    winner = "Player"
                    print(f"\n🎉 You won! 🎉")
                    print(f"Moves: {moves}")
                    if game_mode == 'multi-goal':
                        print(f"Final Cost: {player.total_cost}")
                        print(f"Total Exploration Cost: {player.exploration_cost + player.total_cost}")
                    else:
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
        if fog_of_war:
            draw_maze_with_fog(screen, maze, TILE_SIZE, player, explored_tiles)
        else:
            draw_maze(screen, maze, TILE_SIZE)

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

        # Draw UI
        draw_ui(screen, TOTAL_WINDOW_WIDTH, TOTAL_WINDOW_HEIGHT, moves, player.total_cost, won, game_mode, player, num_checkpoints, player_mode, ai_agents, winner, fog_of_war)

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
                    moves += 1

                    # After player moves in competitive mode, queue AI moves
                    if player_mode == 'competitive':
                        for ai in ai_agents:
                            if not ai.finished and ai not in ai_animation_queue:
                                # Just add to queue, path will be calculated when AI moves
                                ai_animation_queue.append(ai)

                    # Dynamic mode: Spawn obstacles as player moves
                    if game_mode == 'dynamic':
                        spawn_dynamic_obstacles(maze, player, moves)

                    # Multi-goal mode: Check if landed on checkpoint
                    if game_mode == 'multi-goal' and maze[player.tile_y][player.tile_x] == TERRAIN_CHECKPOINT:
                        player.checkpoints_collected += 1
                        player.exploration_cost += player.total_cost
                        player.total_cost = 0
                        maze[player.tile_y][player.tile_x] = TERRAIN_GRASS  # Convert checkpoint to grass
                        print(f"✓ Checkpoint collected! ({player.checkpoints_collected}/{num_checkpoints})")

                    # Check if won
                    win_condition = player.is_at_goal(maze)
                    if game_mode == 'multi-goal':
                        win_condition = win_condition and player.checkpoints_collected >= num_checkpoints

                    if win_condition and winner is None:
                        won = True
                        winner = "Player"
                        print(f"\n🎉 You won! 🎉")
                        print(f"Moves: {moves}")
                        if game_mode == 'multi-goal':
                            print(f"Final Cost: {player.total_cost}")
                            print(f"Total Exploration Cost: {player.exploration_cost + player.total_cost}")
                        else:
                            print(f"Total Cost: {player.total_cost}\n")

            # Restart with new maze
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                # Generate new maze with same settings
                maze = generate_maze(MAZE_WIDTH, MAZE_HEIGHT, goal_placement, game_mode, num_checkpoints)
                start_x, start_y = find_start_position(maze)

                # Recreate player sprite
                player_sprite = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                pygame.draw.circle(player_sprite, BLUE, (TILE_SIZE // 2, TILE_SIZE // 2), TILE_SIZE // 3)
                pygame.draw.circle(player_sprite, WHITE, (TILE_SIZE // 2, TILE_SIZE // 2), TILE_SIZE // 3, 2)

                player = Player(start_x, start_y, TILE_SIZE, player_sprite, BLUE)
                input_controller = InputController(TILE_SIZE)
                moves = 0
                won = False
                winner = None
                ai_animation_queue = []

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

                    ai_agent = AIAgent(ai_x, ai_y, TILE_SIZE, ai_name, ai_color)
                    ai_agent.calculate_path(maze, fog_of_war)
                    ai_agents.append(ai_agent)

            # Return to menu
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                run = False  # Exit game loop to return to menu

        pygame.display.flip()


if __name__ == "__main__":
    start('corner')  # Default to corner placement when running directly
    pygame.quit()  # Only quit pygame when running standalone
