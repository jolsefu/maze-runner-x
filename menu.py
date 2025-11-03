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
        ("Hold Mouse Left Click", "Go to path using A* Algorithm"),
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

def draw_settings_screen(screen, goal_placement):
    """Draw the settings screen"""
    title_font = pygame.font.Font(None, 72)
    text_font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 28)

    # Title
    title = title_font.render("Settings", True, YELLOW)
    title_rect = title.get_rect(center=(MENU_WIDTH // 2, 80))
    screen.blit(title, title_rect)

    # Goal Placement Setting
    y_pos = 200
    setting_label = text_font.render("Goal Placement:", True, WHITE)
    setting_rect = setting_label.get_rect(center=(MENU_WIDTH // 2, y_pos))
    screen.blit(setting_label, setting_rect)

    y_pos += 80
    corner_text = f"Bottom-Right Corner" if goal_placement == 'center' else "* Bottom-Right Corner"
    corner_color = WHITE if goal_placement == 'center' else GREEN
    corner_label = text_font.render(corner_text, True, corner_color)
    corner_rect = corner_label.get_rect(center=(MENU_WIDTH // 2, y_pos))
    screen.blit(corner_label, corner_rect)

    y_pos += 60
    center_text = f"Center of Maze" if goal_placement == 'corner' else "* Center of Maze"
    center_color = WHITE if goal_placement == 'corner' else GREEN
    center_label = text_font.render(center_text, True, center_color)
    center_rect = center_label.get_rect(center=(MENU_WIDTH // 2, y_pos))
    screen.blit(center_label, center_rect)

    # Description
    y_pos += 100
    if goal_placement == 'corner':
        desc_text = "Maze has one optimal path from start to goal"
    else:
        desc_text = "Goal in center creates more route options"

    desc_label = small_font.render(desc_text, True, GRAY)
    desc_rect = desc_label.get_rect(center=(MENU_WIDTH // 2, y_pos))
    screen.blit(desc_label, desc_rect)

    # Instructions
    y_pos += 80
    inst_text = "Click on an option to select it"
    inst_label = text_font.render(inst_text, True, GRAY)
    inst_rect = inst_label.get_rect(center=(MENU_WIDTH // 2, y_pos))
    screen.blit(inst_label, inst_rect)

    return {
        'corner': pygame.Rect(MENU_WIDTH // 2 - 250, 280 - 30, 500, 60),
        'center': pygame.Rect(MENU_WIDTH // 2 - 250, 340 - 30, 500, 60)
    }


def draw_game_mode_screen(screen, game_mode):
    """Draw the game mode selection screen"""
    title_font = pygame.font.Font(None, 72)
    text_font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 28)

    # Title
    title = title_font.render("Select Game Mode", True, YELLOW)
    title_rect = title.get_rect(center=(MENU_WIDTH // 2, 80))
    screen.blit(title, title_rect)

    # Game Mode Options
    y_pos = 200

    # Explore Mode
    explore_text = "Explore Mode" if game_mode != 'explore' else "* Explore Mode"
    explore_color = WHITE if game_mode != 'explore' else GREEN
    explore_label = text_font.render(explore_text, True, explore_color)
    explore_rect = explore_label.get_rect(center=(MENU_WIDTH // 2, y_pos))
    screen.blit(explore_label, explore_rect)

    y_pos += 40
    explore_desc = small_font.render("Default Static Maze - Navigate through fixed obstacles", True, GRAY)
    explore_desc_rect = explore_desc.get_rect(center=(MENU_WIDTH // 2, y_pos))
    screen.blit(explore_desc, explore_desc_rect)

    # Dynamic Mode
    y_pos += 90
    dynamic_text = "Dynamic Mode" if game_mode != 'dynamic' else "* Dynamic Mode"
    dynamic_color = WHITE if game_mode != 'dynamic' else GREEN
    dynamic_label = text_font.render(dynamic_text, True, dynamic_color)
    dynamic_rect = dynamic_label.get_rect(center=(MENU_WIDTH // 2, y_pos))
    screen.blit(dynamic_label, dynamic_rect)

    y_pos += 40
    dynamic_desc = small_font.render("Obstacles Appear Randomly - The maze changes as you play", True, GRAY)
    dynamic_desc_rect = dynamic_desc.get_rect(center=(MENU_WIDTH // 2, y_pos))
    screen.blit(dynamic_desc, dynamic_desc_rect)

    # Multi-Goal Mode
    y_pos += 90
    multi_text = "Multi-Goal Mode" if game_mode != 'multi-goal' else "* Multi-Goal Mode"
    multi_color = WHITE if game_mode != 'multi-goal' else GREEN
    multi_label = text_font.render(multi_text, True, multi_color)
    multi_rect = multi_label.get_rect(center=(MENU_WIDTH // 2, y_pos))
    screen.blit(multi_label, multi_rect)

    y_pos += 40
    multi_desc = small_font.render("Collect All Checkpoints - Cost resets at each checkpoint", True, GRAY)
    multi_desc_rect = multi_desc.get_rect(center=(MENU_WIDTH // 2, y_pos))
    screen.blit(multi_desc, multi_desc_rect)

    # Instructions
    y_pos += 100
    inst_text = "Click on a game mode to select it"
    inst_label = small_font.render(inst_text, True, GRAY)
    inst_rect = inst_label.get_rect(center=(MENU_WIDTH // 2, y_pos))
    screen.blit(inst_label, inst_rect)

    return {
        'explore': pygame.Rect(MENU_WIDTH // 2 - 300, 200 - 30, 600, 80),
        'dynamic': pygame.Rect(MENU_WIDTH // 2 - 300, 330 - 30, 600, 80),
        'multi-goal': pygame.Rect(MENU_WIDTH // 2 - 300, 460 - 30, 600, 80)
    }


def show_menu():
    """Display the main menu and handle user input"""
    # Game settings
    goal_placement = 'corner'  # Default: bottom-right corner
    game_mode = 'explore'  # Default: explore mode

    # Create buttons
    button_width = 300
    button_height = 60
    button_x = (MENU_WIDTH - button_width) // 2
    start_y = 250

    start_button = Button(button_x, start_y, button_width, button_height, "Start Game", BLUE, GREEN)
    settings_button = Button(button_x, start_y + 90, button_width, button_height, "Settings", BLUE, GREEN)
    controls_button = Button(button_x, start_y + 180, button_width, button_height, "Controls", BLUE, GREEN)
    quit_button = Button(button_x, start_y + 270, button_width, button_height, "Quit", RED, YELLOW)
    back_button = Button(button_x, MENU_HEIGHT - 120, button_width, button_height, "Back", GRAY, GREEN)
    continue_button = Button(button_x, MENU_HEIGHT - 120, button_width, button_height, "Continue", GREEN, YELLOW)

    current_screen = "main"  # Can be "main", "controls", "settings", or "game_mode"
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
                    if current_screen in ["controls", "settings", "game_mode"]:
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
            settings_button.update(mouse_pos)
            controls_button.update(mouse_pos)
            quit_button.update(mouse_pos)

            start_button.draw(screen)
            settings_button.draw(screen)
            controls_button.draw(screen)
            quit_button.draw(screen)

            # Check for button clicks
            if start_button.is_clicked(mouse_pos, mouse_click):
                current_screen = "game_mode"  # Go to game mode selection

            if settings_button.is_clicked(mouse_pos, mouse_click):
                current_screen = "settings"

            if controls_button.is_clicked(mouse_pos, mouse_click):
                current_screen = "controls"

            if quit_button.is_clicked(mouse_pos, mouse_click):
                pygame.quit()
                sys.exit()

        elif current_screen == "game_mode":
            # Draw game mode selection screen
            option_rects = draw_game_mode_screen(screen, game_mode)

            # Check for clicks on game mode options
            if mouse_click:
                if option_rects['explore'].collidepoint(mouse_pos):
                    game_mode = 'explore'
                elif option_rects['dynamic'].collidepoint(mouse_pos):
                    game_mode = 'dynamic'
                elif option_rects['multi-goal'].collidepoint(mouse_pos):
                    game_mode = 'multi-goal'

            # Update and draw buttons
            back_button.update(mouse_pos)
            continue_button.update(mouse_pos)

            back_button.draw(screen)

            # Draw continue button on the right side
            continue_button_right = Button(MENU_WIDTH - button_x - button_width, MENU_HEIGHT - 120,
                                          button_width, button_height, "Continue", GREEN, YELLOW)
            continue_button_right.update(mouse_pos)
            continue_button_right.draw(screen)

            # Check for button clicks
            if back_button.is_clicked(mouse_pos, mouse_click):
                current_screen = "main"

            if continue_button_right.is_clicked(mouse_pos, mouse_click):
                return ("start", goal_placement, game_mode)  # Start the game

        elif current_screen == "settings":
            # Draw settings screen
            option_rects = draw_settings_screen(screen, goal_placement)

            # Check for clicks on settings options
            if mouse_click:
                if option_rects['corner'].collidepoint(mouse_pos):
                    goal_placement = 'corner'
                elif option_rects['center'].collidepoint(mouse_pos):
                    goal_placement = 'center'

            # Update and draw back button
            back_button.update(mouse_pos)
            back_button.draw(screen)

            # Check for back button click
            if back_button.is_clicked(mouse_pos, mouse_click):
                current_screen = "main"

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

    if result[0] == "start":
        # Close menu and start the game
        goal_placement = result[1]
        game_mode = result[2]
        pygame.quit()

        # Import and start the main game with settings
        import main
        main.start(goal_placement, game_mode)
