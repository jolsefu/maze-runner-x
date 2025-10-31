import pygame
import sys
import os
from maze_generation import (
    generate_maze, create_simple_maze, get_terrain_cost, is_passable,
    TERRAIN_GRASS, TERRAIN_WALL, TERRAIN_START, TERRAIN_GOAL,
    TERRAIN_WATER, TERRAIN_MUD, TERRAIN_LAVA
)

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
wall_sprite = load_sprite("wall.png")
water_sprite = load_sprite("water.png")
mud_sprite = load_sprite("mud.png")
lava_sprite = load_sprite("lava.png")
empty_sprite = load_sprite("empty.png")


class Player:
    """Player that navigates the maze"""

    def __init__(self, x, y, tile_size, sprite=None):
        self.tile_x = x
        self.tile_y = y
        self.tile_size = tile_size
        self.speed = 1  # Tiles per move
        self.color = BLUE
        self.sprite = sprite
        self.total_cost = 0  # Track total movement cost

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


def draw_maze(screen, maze, tile_size):
    """Draw the maze on screen using sprites with different terrain types"""
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)

            if cell == TERRAIN_GRASS:  # Grass - cost 1
                screen.blit(grass_sprite, rect)
            elif cell == TERRAIN_WALL:  # Wall - impassable
                screen.blit(wall_sprite, rect)  # Use grass as wall for now
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


def draw_ui(screen, width, height, moves, total_cost, won=False):
    """Draw UI information on the right side"""
    font_title = pygame.font.Font(None, 48)
    font_text = pygame.font.Font(None, 32)
    font_small = pygame.font.Font(None, 28)

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

    # Terrain legend
    y_pos += 90
    legend_title = font_text.render("Terrain Costs:", True, WHITE)
    legend_rect = legend_title.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
    screen.blit(legend_title, legend_rect)

    y_pos += 40
    terrain_info = [
        ("Grass: 1", GREEN),
        ("Water: 3", BLUE),
        ("Mud: 5", (139, 69, 19)),
        ("Lava: ∞", RED)
    ]
    for terrain, color in terrain_info:
        terrain_text = font_small.render(terrain, True, color)
        terrain_rect = terrain_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
        screen.blit(terrain_text, terrain_rect)
        y_pos += 35

    # Win message or instructions
    y_pos += 50
    if won:
        win_text = font_title.render("YOU WIN!", True, YELLOW)
        win_rect = win_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
        screen.blit(win_text, win_rect)

        y_pos += 60
        restart_text = font_text.render("Press R to restart", True, WHITE)
        restart_rect = restart_text.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
        screen.blit(restart_text, restart_rect)
    else:
        # Controls
        controls_title = font_text.render("Controls:", True, WHITE)
        controls_rect = controls_title.get_rect(centerx=ui_x_start + UI_WIDTH // 2, y=y_pos)
        screen.blit(controls_title, controls_rect)

        y_pos += 40
        controls = [
            "WASD/Arrows - Move",
            "R - New Maze"
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


def start():
    """Start the game"""
    # Generate maze
    maze = generate_maze(MAZE_WIDTH, MAZE_HEIGHT)

    # Find start position and create player
    start_x, start_y = find_start_position(maze)

    # Create player sprite (a small character on grass)
    player_sprite = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    # Draw a simple character (circle with outline)
    pygame.draw.circle(player_sprite, BLUE, (TILE_SIZE // 2, TILE_SIZE // 2), TILE_SIZE // 3)
    pygame.draw.circle(player_sprite, WHITE, (TILE_SIZE // 2, TILE_SIZE // 2), TILE_SIZE // 3, 2)

    player = Player(start_x, start_y, TILE_SIZE, player_sprite)

    moves = 0
    won = False

    loop(maze, player, moves, won)
    print("=" * 50)
    print("PYGAME STOPPED".center(50))
    print("=" * 50)


def loop(maze, player, moves, won):
    """Main game loop"""
    run = True

    while run:
        clock.tick(60)  # 60 FPS

        # Fill background
        screen.fill(BLACK)

        # Draw maze
        draw_maze(screen, maze, TILE_SIZE)

        # Draw player
        player.draw(screen)

        # Draw UI
        draw_ui(screen, TOTAL_WINDOW_WIDTH, TOTAL_WINDOW_HEIGHT, moves, player.total_cost, won)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            elif event.type == pygame.KEYDOWN and not won:
                move_cost = 0

                # Movement
                if event.key in (pygame.K_w, pygame.K_UP):
                    move_cost = player.move(0, -1, maze)
                elif event.key in (pygame.K_s, pygame.K_DOWN):
                    move_cost = player.move(0, 1, maze)
                elif event.key in (pygame.K_a, pygame.K_LEFT):
                    move_cost = player.move(-1, 0, maze)
                elif event.key in (pygame.K_d, pygame.K_RIGHT):
                    move_cost = player.move(1, 0, maze)

                if move_cost > 0:
                    moves += 1
                    # Check if won
                    if player.is_at_goal(maze):
                        won = True
                        print(f"\n🎉 Congratulations! You won! 🎉")
                        print(f"Moves: {moves}")
                        print(f"Total Cost: {player.total_cost}\n")

            # Restart with new maze
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                # Generate new maze
                maze = generate_maze(MAZE_WIDTH, MAZE_HEIGHT)
                start_x, start_y = find_start_position(maze)

                # Recreate player sprite
                player_sprite = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                pygame.draw.circle(player_sprite, BLUE, (TILE_SIZE // 2, TILE_SIZE // 2), TILE_SIZE // 3)
                pygame.draw.circle(player_sprite, WHITE, (TILE_SIZE // 2, TILE_SIZE // 2), TILE_SIZE // 3, 2)

                player = Player(start_x, start_y, TILE_SIZE, player_sprite)
                moves = 0
                won = False

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    start()
