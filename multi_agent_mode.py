"""Multi-Agent Mode - Several AIs compete for the same goal"""

import pygame
import sys
from maze_generation import (
    generate_maze, get_terrain_cost, is_passable,
    TERRAIN_GRASS, TERRAIN_WALL, TERRAIN_START, TERRAIN_GOAL,
    TERRAIN_WATER, TERRAIN_MUD, TERRAIN_LAVA
)
from ai_agent import AIAgent

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
LIME = (50, 205, 50)

# AI Colors (for 4 corner agents)
AI_COLORS = [RED, BLUE, GREEN, YELLOW]
AI_NAMES = ["AI-NW", "AI-NE", "AI-SW", "AI-SE"]  # Northwest, Northeast, Southwest, Southeast

# Path visibility setting
SHOW_AI_PATHS = True  # Set to False to hide AI path lines

# Setup screen
screen = pygame.display.set_mode((TOTAL_WINDOW_WIDTH, TOTAL_WINDOW_HEIGHT))
pygame.display.set_caption("Maze Runner - Multi-Agent Mode")
clock = pygame.time.Clock()

# Load sprites (same as main.py)
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


def draw_ui(screen, width, height, ai_agents, winner, game_over):
    """Draw the UI elements for multi-agent mode"""
    font_title = pygame.font.Font(None, 48)
    font_text = pygame.font.Font(None, 32)
    font_small = pygame.font.Font(None, 28)
    font_tiny = pygame.font.Font(None, 22)

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
    title_text = font_title.render("MULTI-AGENT", True, YELLOW)
    title_rect = title_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
    screen.blit(title_text, title_rect)

    y_pos += 50
    subtitle_text = font_small.render("Corner to Center Race", True, WHITE)
    subtitle_rect = subtitle_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
    screen.blit(subtitle_text, subtitle_rect)

    # AI Agents Status
    y_pos += 50

    # Sort agents by ranking (finished first, then by cost)
    sorted_agents = sorted(ai_agents, key=lambda a: (not a.finished, a.total_cost if a.finished else float('inf'), a.moves))

    for i, ai in enumerate(sorted_agents):
        # Agent name with rank if finished
        if ai.finished:
            rank_text = f"#{i+1} - {ai.name}"
            name_color = ai.color
        else:
            rank_text = f"{ai.name}"
            name_color = ai.color if not ai.out_of_energy else GRAY

        name_label = font_text.render(rank_text, True, name_color)
        name_rect = name_label.get_rect(x=ui_x_start + 30, y=y_pos)
        screen.blit(name_label, name_rect)

        y_pos += 30

        # Stats
        stats_text = f"Moves: {ai.moves}  Cost: {ai.total_cost}"
        stats_label = font_tiny.render(stats_text, True, WHITE)
        stats_rect = stats_label.get_rect(x=ui_x_start + 50, y=y_pos)
        screen.blit(stats_label, stats_rect)

        y_pos += 20

        # Status
        if ai.finished:
            status = "FINISHED!"
            status_color = GREEN
        elif ai.out_of_energy:
            status = "Out of Energy"
            status_color = RED
        else:
            status = "Running..."
            status_color = CYAN

        status_label = font_tiny.render(status, True, status_color)
        status_rect = status_label.get_rect(x=ui_x_start + 50, y=y_pos)
        screen.blit(status_label, status_rect)

        y_pos += 35

    # Winner announcement
    if game_over and winner:
        y_pos += 20
        win_text = font_title.render(f"{winner} WINS!", True, GREEN)
        win_rect = win_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
        screen.blit(win_text, win_rect)
        y_pos += 60

    # Controls
    if not game_over:
        y_pos = height - 180
        controls_title = font_text.render("Controls:", True, WHITE)
        controls_rect = controls_title.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
        screen.blit(controls_title, controls_rect)

        y_pos += 40
        controls = [
            "R - New Maze",
            "ESC - Return to Menu"
        ]
        for control in controls:
            control_text = font_small.render(control, True, WHITE)
            control_rect = control_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
            screen.blit(control_text, control_rect)
            y_pos += 35
    else:
        y_pos = height - 140
        restart_text = font_text.render("Press R to restart", True, WHITE)
        restart_rect = restart_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
        screen.blit(restart_text, restart_rect)

        y_pos += 40
        menu_text = font_text.render("Press ESC for menu", True, WHITE)
        menu_rect = menu_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
        screen.blit(menu_text, menu_rect)


def find_start_position(maze):
    """Find the start position in the maze"""
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == TERRAIN_START:
                return x, y
    return 1, 1


def verify_all_corners_reachable(maze, corners, goal_pos):
    """Verify that all corner positions have a valid path to the goal

    Args:
        maze: The maze grid
        corners: List of (x, y) corner positions
        goal_pos: (x, y) position of the goal

    Returns:
        True if all corners can reach the goal, False otherwise
    """
    from collections import deque

    for corner_x, corner_y in corners:
        # BFS from this corner to goal
        queue = deque([(corner_x, corner_y)])
        visited = {(corner_x, corner_y)}
        found_goal = False

        while queue:
            x, y = queue.popleft()

            if (x, y) == goal_pos:
                found_goal = True
                break

            # Check all 4 directions
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy

                if (0 <= nx < len(maze[0]) and
                    0 <= ny < len(maze) and
                    (nx, ny) not in visited):

                    terrain = maze[ny][nx]
                    # Can move through any terrain except walls and lava
                    if is_passable(terrain):
                        visited.add((nx, ny))
                        queue.append((nx, ny))

        if not found_goal:
            return False  # This corner can't reach the goal

    return True  # All corners can reach the goal


def generate_multi_agent_maze(width, height, game_mode='explore'):
    """Generate a maze specifically for multi-agent mode with center goal and corner starts

    This ensures:
    - Goal is in the center
    - All 4 corners have the AI starting positions
    - All corners start with the same terrain type (grass) for fairness
    - All 4 corners have a valid path to the center goal
    """
    from maze_generation import MazeGenerator, TERRAIN_GRASS

    max_attempts = 50  # Maximum attempts to generate a valid maze
    attempt = 0

    while attempt < max_attempts:
        attempt += 1

        # Generate base maze with center goal
        generator = MazeGenerator(width, height, 'center', game_mode, 0)
        maze = generator.generate()

        # Ensure all corner positions are GRASS (same starting terrain for all AIs)
        corners = [
            (1, 1),  # Top-left (NW)
            (width - 2, 1),  # Top-right (NE)
            (1, height - 2),  # Bottom-left (SW)
            (width - 2, height - 2),  # Bottom-right (SE)
        ]

        for cx, cy in corners:
            # Set all corner tiles to GRASS for fair starting conditions
            maze[cy][cx] = TERRAIN_GRASS

        # Find goal position
        goal_pos = None
        for y in range(len(maze)):
            for x in range(len(maze[0])):
                if maze[y][x] == TERRAIN_GOAL:
                    goal_pos = (x, y)
                    break
            if goal_pos:
                break

        if not goal_pos:
            # Default to center if not found
            goal_pos = (width // 2, height // 2)

        # Verify all corners can reach the goal
        if verify_all_corners_reachable(maze, corners, goal_pos):
            if attempt > 1:
                print(f"Generated valid multi-agent maze after {attempt} attempts")
            return maze

    # If we couldn't generate a valid maze after max_attempts, return the last one
    # and warn the user
    print(f"Warning: Could not generate maze with all corners reachable after {max_attempts} attempts")
    print("Using last generated maze - some agents may not have valid paths")
    return maze


def get_corner_starts(width, height):
    """Get the four corner starting positions"""
    return [
        (1, 1),  # Top-left (NW)
        (width - 2, 1),  # Top-right (NE)
        (1, height - 2),  # Bottom-left (SW)
        (width - 2, height - 2),  # Bottom-right (SE)
    ]


def start(goal_placement='corner', game_mode='explore', num_agents=4, fog_of_war=False, energy_constraint=False, fuel_limit=100):
    """Start multi-agent mode

    Args:
        goal_placement: Where to place the goal (ignored - always uses center for multi-agent)
        game_mode: Maze generation mode
        num_agents: Number of AI agents (fixed at 4 for corner starts)
        fog_of_war: Enable fog of war
        energy_constraint: Enable energy limit
        fuel_limit: Maximum energy for each agent
    """
    # Generate maze with center goal and clear corners
    maze = generate_multi_agent_maze(MAZE_WIDTH, MAZE_HEIGHT, game_mode)

    # Get corner starting positions
    corner_starts = get_corner_starts(MAZE_WIDTH, MAZE_HEIGHT)

    # Create 4 AI agents, one for each corner
    ai_agents = []
    energy_limit = fuel_limit if energy_constraint else None

    for i in range(4):  # Always 4 agents for the 4 corners
        start_x, start_y = corner_starts[i]
        color = AI_COLORS[i]
        name = AI_NAMES[i]

        ai_agent = AIAgent(start_x, start_y, TILE_SIZE, name, color, energy_limit)
        ai_agent.calculate_path(maze, fog_of_war)
        ai_agents.append(ai_agent)

    loop(maze, ai_agents, goal_placement, game_mode, 4, fog_of_war, energy_constraint, fuel_limit)
    print("=" * 50)
    print("MULTI-AGENT MODE ENDED".center(50))
    print("=" * 50)


def loop(maze, ai_agents, goal_placement, game_mode, num_agents, fog_of_war, energy_constraint, fuel_limit):
    """Main game loop for multi-agent mode"""
    run = True
    game_over = False
    winner = None

    # Animation control
    ai_animation_delay = 0
    active_agents = list(ai_agents)  # Agents still moving

    while run:
        clock.tick(60)

        # Process AI movements
        if not game_over and active_agents:
            ai_animation_delay += 1

            # Move AIs at a controlled pace
            if ai_animation_delay >= 8:  # Faster than competitive mode
                ai_animation_delay = 0

                # Move all active agents simultaneously
                for ai in active_agents[:]:  # Create copy to safely modify list
                    # Recalculate path
                    ai.calculate_path(maze, fog_of_war)

                    # Make move
                    moved = ai.make_move(maze)

                    # Check if this AI finished
                    if ai.finished and winner is None:
                        winner = ai.name
                        game_over = True
                        print(f"\n🏆 {ai.name} wins the race! 🏆")
                        print(f"Moves: {ai.moves}")
                        print(f"Total Cost: {ai.total_cost}")

                    # Remove from active if finished or out of energy
                    if ai.finished or ai.out_of_energy:
                        if ai in active_agents:
                            active_agents.remove(ai)
                            if ai.out_of_energy:
                                print(f"⚡ {ai.name} ran out of energy!")

                # If all agents are done but no winner, game over
                if not active_agents and not game_over:
                    game_over = True
                    print("\n❌ All agents failed to reach the goal!")

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # Restart with new maze
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                # Generate new maze with center goal
                maze = generate_multi_agent_maze(MAZE_WIDTH, MAZE_HEIGHT, game_mode)
                corner_starts = get_corner_starts(MAZE_WIDTH, MAZE_HEIGHT)

                # Recreate AI agents at corner positions
                ai_agents = []
                energy_limit = fuel_limit if energy_constraint else None

                for i in range(4):  # Always 4 agents for the 4 corners
                    start_x, start_y = corner_starts[i]
                    color = AI_COLORS[i]
                    name = AI_NAMES[i]

                    ai_agent = AIAgent(start_x, start_y, TILE_SIZE, name, color, energy_limit)
                    ai_agent.calculate_path(maze, fog_of_war)
                    ai_agents.append(ai_agent)

                active_agents = list(ai_agents)
                game_over = False
                winner = None
                ai_animation_delay = 0

            # Return to menu
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                run = False

        # Draw everything
        screen.fill(BLACK)

        # Draw maze
        draw_maze(screen, maze, TILE_SIZE)

        # Draw AI paths (if enabled)
        if SHOW_AI_PATHS:
            for ai in ai_agents:
                ai.draw_path(screen, TILE_SIZE)

        # Draw AI agents
        for ai in ai_agents:
            ai.draw(screen)

        # Draw UI
        draw_ui(screen, TOTAL_WINDOW_WIDTH, TOTAL_WINDOW_HEIGHT, ai_agents, winner, game_over)

        pygame.display.flip()

    # Don't call pygame.quit() - let menu handle it


if __name__ == "__main__":
    start('center', 'explore', 4)  # 4 agents from corners to center
    pygame.quit()
