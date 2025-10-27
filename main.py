import pygame
import sys
import os
from maze_generation import generate_maze, create_simple_maze

# Initialize pygame
pygame.init()

# Constants
TILE_SIZE = 16  # 16x16 tiles to match sprite size
MAZE_WIDTH = 25  # Width in tiles (use odd numbers) - increased for 16px tiles
MAZE_HEIGHT = 25  # Height in tiles (use odd numbers) - increased for 16px tiles
SCREEN_WIDTH = MAZE_WIDTH * TILE_SIZE
SCREEN_HEIGHT = MAZE_HEIGHT * TILE_SIZE + 50  # Extra space for UI

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
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
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


class Player:
    """Player that navigates the maze"""

    def __init__(self, x, y, tile_size, sprite=None):
        self.tile_x = x
        self.tile_y = y
        self.tile_size = tile_size
        self.speed = 1  # Tiles per move
        self.color = BLUE
        self.sprite = sprite

    def move(self, dx, dy, maze):
        """Move player if the destination is not a wall"""
        new_x = self.tile_x + dx
        new_y = self.tile_y + dy

        # Check bounds and walls
        if (0 <= new_y < len(maze) and
            0 <= new_x < len(maze[0]) and
            maze[new_y][new_x] != 1):  # Not a wall
            self.tile_x = new_x
            self.tile_y = new_y
            return True
        return False

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
        return maze[self.tile_y][self.tile_x] == 3


def draw_maze(screen, maze, tile_size):
    """Draw the maze on screen using sprites"""

    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)

            if cell == 1:  # Wall - use grass sprite
                screen.blit(grass_sprite, rect)
            elif cell == 2:  # Start - use empty with green overlay
                screen.blit(empty_sprite, rect)
                # Add green tint for start
                overlay = pygame.Surface((tile_size, tile_size))
                overlay.fill(GREEN)
                overlay.set_alpha(120)
                screen.blit(overlay, rect)
            elif cell == 3:  # Goal - use empty with red overlay
                screen.blit(empty_sprite, rect)
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
            else:  # Path - use empty sprite
                screen.blit(empty_sprite, rect)


def draw_ui(screen, width, height, moves, won=False):
    """Draw UI information"""

    font = pygame.font.Font(None, 36)
    ui_y = height - 45

    # Background for UI
    ui_rect = pygame.Rect(0, height - 50, width, 50)
    pygame.draw.rect(screen, (30, 30, 30), ui_rect)

    # Moves counter
    moves_text = font.render(f"Moves: {moves}", True, WHITE)
    screen.blit(moves_text, (10, ui_y))

    # Instructions or win message
    if won:
        win_text = font.render("YOU WIN! Press R to restart", True, YELLOW)
        screen.blit(win_text, (width // 2 - 200, ui_y))
    else:
        help_text = font.render("WASD/Arrows to move | R: New Maze", True, WHITE)
        text_rect = help_text.get_rect(right=width - 10, centery=ui_y + 18)
        screen.blit(help_text, text_rect)


def find_start_position(maze):
    """Find the start position (marked as 2) in the maze"""
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == 2:
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
        draw_ui(screen, SCREEN_WIDTH, SCREEN_HEIGHT, moves, won)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            elif event.type == pygame.KEYDOWN and not won:
                moved = False

                # Movement
                if event.key in (pygame.K_w, pygame.K_UP):
                    moved = player.move(0, -1, maze)
                elif event.key in (pygame.K_s, pygame.K_DOWN):
                    moved = player.move(0, 1, maze)
                elif event.key in (pygame.K_a, pygame.K_LEFT):
                    moved = player.move(-1, 0, maze)
                elif event.key in (pygame.K_d, pygame.K_RIGHT):
                    moved = player.move(1, 0, maze)

                if moved:
                    moves += 1
                    # Check if won
                    if player.is_at_goal(maze):
                        won = True
                        print(f"\n🎉 Congratulations! You won in {moves} moves! 🎉\n")

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
