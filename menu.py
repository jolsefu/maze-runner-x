import pygame
import sys
import os

# Initialize pygame
pygame.init()

# Constants
MENU_WIDTH = 1465
MENU_HEIGHT = 830

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
GREEN = (50, 255, 100)
BLUE = (50, 150, 255)
YELLOW = (255, 255, 100)
RED = (255, 50, 50)

# Setup screen
screen = pygame.display.set_mode((MENU_WIDTH, MENU_HEIGHT))
pygame.display.set_caption("Maze Runner - Main Menu")
clock = pygame.time.Clock()


class Button:
    """A clickable button for the menu"""

    def __init__(self, x, y, width, height, text, color=BLUE, hover_color=GREEN):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.font = pygame.font.Font(None, 48)

    def draw(self, screen):
        """Draw the button"""
        # Draw button background
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, self.rect, 3, border_radius=10)

        # Draw text
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_hovered(self, mouse_pos):
        """Check if mouse is hovering over button"""
        return self.rect.collidepoint(mouse_pos)

    def update(self, mouse_pos):
        """Update button state based on mouse position"""
        if self.is_hovered(mouse_pos):
            self.current_color = self.hover_color
        else:
            self.current_color = self.color

    def is_clicked(self, mouse_pos, mouse_click):
        """Check if button was clicked"""
        return self.is_hovered(mouse_pos) and mouse_click


def draw_title(screen):
    """Draw the game title"""
    title_font = pygame.font.Font(None, 96)
    subtitle_font = pygame.font.Font(None, 36)

    # Main title
    title_text = title_font.render("MAZE RUNNER", True, YELLOW)
    title_rect = title_text.get_rect(center=(MENU_WIDTH // 2, 100))

    # Shadow effect
    shadow_text = title_font.render("MAZE RUNNER", True, DARK_GRAY)
    shadow_rect = shadow_text.get_rect(center=(MENU_WIDTH // 2 + 3, 103))

    screen.blit(shadow_text, shadow_rect)
    screen.blit(title_text, title_rect)

    # Subtitle
    subtitle_text = subtitle_font.render("Navigate the Labyrinth", True, WHITE)
    subtitle_rect = subtitle_text.get_rect(center=(MENU_WIDTH // 2, 160))
    screen.blit(subtitle_text, subtitle_rect)


def draw_controls_screen(screen):
    """Draw the controls/help screen"""
    title_font = pygame.font.Font(None, 72)
    text_font = pygame.font.Font(None, 36)

    # Title
    title = title_font.render("Controls", True, YELLOW)
    title_rect = title.get_rect(center=(MENU_WIDTH // 2, 80))
    screen.blit(title, title_rect)

    # Controls list
    controls = [
        ("Movement:", ""),
        ("  W / Up Arrow", "Move Up"),
        ("  S / Down Arrow", "Move Down"),
        ("  A / Left Arrow", "Move Left"),
        ("  D / Right Arrow", "Move Right"),
        ("", ""),
        ("R", "Generate New Maze"),
        ("", ""),
        ("Objective:", ""),
        ("  Navigate from the green start", ""),
        ("  to the red goal flag!", "")
    ]

    y_pos = 160
    for key, description in controls:
        if key and description:
            key_text = text_font.render(key, True, GREEN)
            desc_text = text_font.render(description, True, WHITE)
            screen.blit(key_text, (100, y_pos))
            screen.blit(desc_text, (400, y_pos))
            y_pos += 40
        elif key:
            key_text = text_font.render(key, True, YELLOW if ":" in key else WHITE)
            screen.blit(key_text, (100, y_pos))
            y_pos += 40
        else:
            y_pos += 20

def show_menu():
    """Display the main menu and handle user input"""
    # Create buttons
    button_width = 300
    button_height = 60
    button_x = (MENU_WIDTH - button_width) // 2
    start_y = 250

    start_button = Button(button_x, start_y, button_width, button_height, "Start Game", BLUE, GREEN)
    controls_button = Button(button_x, start_y + 90, button_width, button_height, "Controls", BLUE, GREEN)
    quit_button = Button(button_x, start_y + 180, button_width, button_height, "Quit", RED, YELLOW)
    back_button = Button(button_x, MENU_HEIGHT - 120, button_width, button_height, "Back", GRAY, GREEN)

    current_screen = "main"  # Can be "main" or "controls"
    running = True

    while running:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_click = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if current_screen == "controls":
                        current_screen = "main"
                    else:
                        pygame.quit()
                        sys.exit()

        # Clear screen
        screen.fill(BLACK)

        if current_screen == "main":
            # Draw main menu
            draw_title(screen)

            # Update and draw buttons
            start_button.update(mouse_pos)
            controls_button.update(mouse_pos)
            quit_button.update(mouse_pos)

            start_button.draw(screen)
            controls_button.draw(screen)
            quit_button.draw(screen)

            # Check for button clicks
            if start_button.is_clicked(mouse_pos, mouse_click):
                return "start"  # Signal to start the game

            if controls_button.is_clicked(mouse_pos, mouse_click):
                current_screen = "controls"

            if quit_button.is_clicked(mouse_pos, mouse_click):
                pygame.quit()
                sys.exit()

        elif current_screen == "controls":
            # Draw controls screen
            draw_controls_screen(screen)

            # Update and draw back button
            back_button.update(mouse_pos)
            back_button.draw(screen)

            # Check for back button click
            if back_button.is_clicked(mouse_pos, mouse_click):
                current_screen = "main"

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    result = show_menu()

    if result == "start":
        # Close menu and start the game
        pygame.quit()

        # Import and start the main game
        import main
        main.start()
