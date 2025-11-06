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

def draw_settings_screen(screen, settings_state):
    """Draw the settings screen

    Args:
        settings_state: Dictionary containing all setting states
    """
    title_font = pygame.font.Font(None, 72)
    text_font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 28)
    tiny_font = pygame.font.Font(None, 24)

    # Title
    title = title_font.render("Settings", True, YELLOW)
    title_rect = title.get_rect(center=(MENU_WIDTH // 2, 50))
    screen.blit(title, title_rect)

    y_pos = 120
    clickable_rects = {}

    # Goal Mode Section (Collapsible)
    goal_mode_expanded = settings_state.get('goal_mode_expanded', False)
    goal_icon = "v" if goal_mode_expanded else ">"
    goal_header = text_font.render(f"{goal_icon} Goal Mode", True, YELLOW)
    goal_header_rect = goal_header.get_rect(x=100, y=y_pos)
    screen.blit(goal_header, goal_header_rect)
    clickable_rects['goal_mode_toggle'] = pygame.Rect(100, y_pos, 400, 40)

    y_pos += 50

    # Show goal mode options if expanded
    if goal_mode_expanded:
        goal_placement = settings_state.get('goal_placement', 'corner')

        # Corner option
        corner_text = "  * Bottom-Right Corner" if goal_placement == 'corner' else "    Bottom-Right Corner"
        corner_color = GREEN if goal_placement == 'corner' else WHITE
        corner_label = small_font.render(corner_text, True, corner_color)
        screen.blit(corner_label, (120, y_pos))
        clickable_rects['corner'] = pygame.Rect(120, y_pos - 5, 400, 35)
        y_pos += 40

        # Center option
        center_text = "  * Center of Maze" if goal_placement == 'center' else "    Center of Maze"
        center_color = GREEN if goal_placement == 'center' else WHITE
        center_label = small_font.render(center_text, True, center_color)
        screen.blit(center_label, (120, y_pos))
        clickable_rects['center'] = pygame.Rect(120, y_pos - 5, 400, 35)
        y_pos += 50
    else:
        y_pos += 10

    # Fog of War Toggle
    fog_enabled = settings_state.get('fog_of_war', False)
    fog_status = "[ON]" if fog_enabled else "[OFF]"
    fog_color = GREEN if fog_enabled else GRAY
    fog_text = text_font.render(f"Fog of War {fog_status}", True, fog_color)
    screen.blit(fog_text, (100, y_pos))
    clickable_rects['fog_of_war'] = pygame.Rect(100, y_pos, 400, 40)

    y_pos += 35
    fog_desc = tiny_font.render("Limited vision - only see nearby tiles", True, GRAY)
    screen.blit(fog_desc, (120, y_pos))
    y_pos += 50

    # Energy Constraint Toggle
    energy_enabled = settings_state.get('energy_constraint', False)
    energy_status = "[ON]" if energy_enabled else "[OFF]"
    energy_color = GREEN if energy_enabled else GRAY
    energy_text = text_font.render(f"Energy Constraint {energy_status}", True, energy_color)
    screen.blit(energy_text, (100, y_pos))
    clickable_rects['energy_constraint'] = pygame.Rect(100, y_pos, 450, 40)

    y_pos += 35
    if energy_enabled:
        fuel_limit = settings_state.get('fuel_limit', 100)
        fuel_desc = tiny_font.render(f"Limited fuel: {fuel_limit} cost units (Click +/- to adjust)", True, GRAY)
        screen.blit(fuel_desc, (120, y_pos))

        # Fuel adjustment buttons
        minus_btn = small_font.render("[-]", True, WHITE)
        screen.blit(minus_btn, (120, y_pos + 25))
        clickable_rects['fuel_decrease'] = pygame.Rect(120, y_pos + 25, 35, 30)

        fuel_value = text_font.render(str(fuel_limit), True, YELLOW)
        screen.blit(fuel_value, (170, y_pos + 20))

        plus_btn = small_font.render("[+]", True, WHITE)
        screen.blit(plus_btn, (240, y_pos + 25))
        clickable_rects['fuel_increase'] = pygame.Rect(240, y_pos + 25, 35, 30)

        y_pos += 60
    else:
        energy_desc = tiny_font.render("Limited fuel cost for pathfinding", True, GRAY)
        screen.blit(energy_desc, (120, y_pos))
        y_pos += 50

    # Multi-Agent Mode Toggle
    multi_agent_enabled = settings_state.get('multi_agent', False)
    multi_status = "[ON]" if multi_agent_enabled else "[OFF]"
    multi_color = GREEN if multi_agent_enabled else GRAY
    multi_text = text_font.render(f"Multi-Agent Mode {multi_status}", True, multi_color)
    screen.blit(multi_text, (100, y_pos))
    clickable_rects['multi_agent'] = pygame.Rect(100, y_pos, 450, 40)

    y_pos += 35
    multi_desc = tiny_font.render("Several AIs compete for the same goal", True, GRAY)
    screen.blit(multi_desc, (120, y_pos))
    y_pos += 50

    # Algorithm Comparison Dashboard Toggle
    algo_enabled = settings_state.get('algo_comparison', False)
    algo_status = "[ON]" if algo_enabled else "[OFF]"
    algo_color = GREEN if algo_enabled else GRAY
    algo_text = text_font.render(f"Algorithm Comparison {algo_status}", True, algo_color)
    screen.blit(algo_text, (100, y_pos))
    clickable_rects['algo_comparison'] = pygame.Rect(100, y_pos, 500, 40)

    y_pos += 35
    algo_desc = tiny_font.render("Visualize runtime and exploration difference between BFS, Dijkstra, and A*", True, GRAY)
    screen.blit(algo_desc, (120, y_pos))
    y_pos += 50

    # Instructions
    y_pos += 20
    inst_text = small_font.render("Click on settings to toggle them", True, GRAY)
    inst_rect = inst_text.get_rect(center=(MENU_WIDTH // 2, y_pos))
    screen.blit(inst_text, inst_rect)

    return clickable_rects


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

    # Settings state dictionary
    settings_state = {
        'goal_placement': 'corner',
        'goal_mode_expanded': False,
        'fog_of_war': False,
        'energy_constraint': False,
        'fuel_limit': 100,
        'multi_agent': False,
        'algo_comparison': False
    }

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
                # Sync goal_placement from settings_state
                goal_placement = settings_state['goal_placement']
                return ("start", goal_placement, game_mode)  # Start the game

        elif current_screen == "settings":
            # Draw settings screen
            option_rects = draw_settings_screen(screen, settings_state)

            # Check for clicks on settings options
            if mouse_click:
                # Goal mode toggle
                if 'goal_mode_toggle' in option_rects and option_rects['goal_mode_toggle'].collidepoint(mouse_pos):
                    settings_state['goal_mode_expanded'] = not settings_state['goal_mode_expanded']

                # Goal placement options (only if expanded)
                if settings_state['goal_mode_expanded']:
                    if 'corner' in option_rects and option_rects['corner'].collidepoint(mouse_pos):
                        settings_state['goal_placement'] = 'corner'
                    elif 'center' in option_rects and option_rects['center'].collidepoint(mouse_pos):
                        settings_state['goal_placement'] = 'center'

                # Fog of War toggle
                if 'fog_of_war' in option_rects and option_rects['fog_of_war'].collidepoint(mouse_pos):
                    settings_state['fog_of_war'] = not settings_state['fog_of_war']

                # Energy Constraint toggle
                if 'energy_constraint' in option_rects and option_rects['energy_constraint'].collidepoint(mouse_pos):
                    settings_state['energy_constraint'] = not settings_state['energy_constraint']

                # Fuel adjustment (only if energy constraint is enabled)
                if settings_state['energy_constraint']:
                    if 'fuel_decrease' in option_rects and option_rects['fuel_decrease'].collidepoint(mouse_pos):
                        settings_state['fuel_limit'] = max(10, settings_state['fuel_limit'] - 10)
                    elif 'fuel_increase' in option_rects and option_rects['fuel_increase'].collidepoint(mouse_pos):
                        settings_state['fuel_limit'] = min(500, settings_state['fuel_limit'] + 10)

                # Multi-Agent Mode toggle
                if 'multi_agent' in option_rects and option_rects['multi_agent'].collidepoint(mouse_pos):
                    settings_state['multi_agent'] = not settings_state['multi_agent']

                # Algorithm Comparison toggle
                if 'algo_comparison' in option_rects and option_rects['algo_comparison'].collidepoint(mouse_pos):
                    settings_state['algo_comparison'] = not settings_state['algo_comparison']

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
