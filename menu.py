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
        ("Left Click", "Toggle pathfinding (A* Algorithm)"),
        ("", ""),
        ("ESC", "Return to Menu"),
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


def draw_guide_screen(screen):
    """Draw the guide screen with terrain legend and game info side-by-side"""
    title_font = pygame.font.Font(None, 72)
    text_font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 28)
    tiny_font = pygame.font.Font(None, 24)

    # Title
    title = title_font.render("Guide", True, YELLOW)
    title_rect = title.get_rect(center=(MENU_WIDTH // 2, 80))
    screen.blit(title, title_rect)

    # Calculate three column positions
    left_col_x = MENU_WIDTH // 6
    middle_col_x = MENU_WIDTH // 2
    right_col_x = 5 * MENU_WIDTH // 6

    # LEFT COLUMN: Terrain Legend
    y_pos = 180
    legend_title = text_font.render("Terrain Costs", True, YELLOW)
    legend_rect = legend_title.get_rect(center=(left_col_x, y_pos))
    screen.blit(legend_title, legend_rect)

    y_pos += 60
    terrain_info = [
        ("Grass: 1", (50, 255, 100), "Easy to traverse"),
        ("Water: 3", (50, 150, 255), "Slows you down"),
        ("Mud: 5", (139, 69, 19), "Difficult to cross"),
        ("Lava: Block", (255, 50, 50), "Cannot be crossed")
    ]

    for terrain, color, description in terrain_info:
        terrain_text = small_font.render(terrain, True, color)
        terrain_rect = terrain_text.get_rect(center=(left_col_x, y_pos))
        screen.blit(terrain_text, terrain_rect)

        y_pos += 35
        desc_text = tiny_font.render(description, True, GRAY)
        desc_rect = desc_text.get_rect(center=(left_col_x, y_pos))
        screen.blit(desc_text, desc_rect)

        y_pos += 55

    # MIDDLE COLUMN: Maze Modes
    middle_y = 180
    modes_title = text_font.render("Maze Modes", True, YELLOW)
    modes_rect = modes_title.get_rect(center=(middle_col_x, middle_y))
    screen.blit(modes_title, modes_rect)

    middle_y += 60
    modes_info = [
        ("Explore", "Static maze with", "fixed obstacles"),
        ("Dynamic", "Obstacles appear", "as you play"),
        ("Multi-Goal", "Collect checkpoints", "before goal")
    ]

    for mode_name, desc_line1, desc_line2 in modes_info:
        mode_text = small_font.render(mode_name, True, GREEN)
        mode_text_rect = mode_text.get_rect(center=(middle_col_x, middle_y))
        screen.blit(mode_text, mode_text_rect)

        middle_y += 35
        desc_text1 = tiny_font.render(desc_line1, True, WHITE)
        desc_rect1 = desc_text1.get_rect(center=(middle_col_x, middle_y))
        screen.blit(desc_text1, desc_rect1)

        middle_y += 25
        desc_text2 = tiny_font.render(desc_line2, True, WHITE)
        desc_rect2 = desc_text2.get_rect(center=(middle_col_x, middle_y))
        screen.blit(desc_text2, desc_rect2)

        middle_y += 60

    # RIGHT COLUMN: Player Modes
    right_y = 180
    player_modes_title = text_font.render("Player Modes", True, YELLOW)
    player_modes_rect = player_modes_title.get_rect(center=(right_col_x, right_y))
    screen.blit(player_modes_title, player_modes_rect)

    right_y += 60
    player_modes_info = [
        ("Solo", "Play alone and", "solve the maze"),
        ("Competitive", "Race against", "AI opponent")
    ]

    for mode_name, desc_line1, desc_line2 in player_modes_info:
        mode_text = small_font.render(mode_name, True, GREEN)
        mode_text_rect = mode_text.get_rect(center=(right_col_x, right_y))
        screen.blit(mode_text, mode_text_rect)

        right_y += 35
        desc_text1 = tiny_font.render(desc_line1, True, WHITE)
        desc_rect1 = desc_text1.get_rect(center=(right_col_x, right_y))
        screen.blit(desc_text1, desc_rect1)

        right_y += 25
        desc_text2 = tiny_font.render(desc_line2, True, WHITE)
        desc_rect2 = desc_text2.get_rect(center=(right_col_x, right_y))
        screen.blit(desc_text2, desc_rect2)

        right_y += 60

    # Vertical separator lines
    separator1_x = (left_col_x + middle_col_x) // 2
    separator2_x = (middle_col_x + right_col_x) // 2
    pygame.draw.line(screen, GRAY, (separator1_x, 170), (separator1_x, 550), 2)
    pygame.draw.line(screen, GRAY, (separator2_x, 170), (separator2_x, 550), 2)

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
    center_x = MENU_WIDTH // 2
    clickable_rects = {}

    # Goal Mode Section (Collapsible)
    goal_mode_expanded = settings_state.get('goal_mode_expanded', False)
    goal_icon = "v" if goal_mode_expanded else ">"
    goal_header = text_font.render(f"{goal_icon} Goal Mode", True, YELLOW)
    goal_header_rect = goal_header.get_rect(center=(center_x, y_pos))
    screen.blit(goal_header, goal_header_rect)
    clickable_rects['goal_mode_toggle'] = pygame.Rect(center_x - 200, y_pos - 20, 400, 40)

    y_pos += 50

    # Show goal mode options if expanded
    if goal_mode_expanded:
        goal_placement = settings_state.get('goal_placement', 'corner')

        # Corner option
        corner_text = "* Bottom-Right Corner" if goal_placement == 'corner' else "Bottom-Right Corner"
        corner_color = GREEN if goal_placement == 'corner' else WHITE
        corner_label = small_font.render(corner_text, True, corner_color)
        corner_rect = corner_label.get_rect(center=(center_x, y_pos))
        screen.blit(corner_label, corner_rect)
        clickable_rects['corner'] = pygame.Rect(center_x - 150, y_pos - 15, 300, 35)
        y_pos += 40

        # Center option
        center_text = "* Center of Maze" if goal_placement == 'center' else "Center of Maze"
        center_color = GREEN if goal_placement == 'center' else WHITE
        center_label = small_font.render(center_text, True, center_color)
        center_rect = center_label.get_rect(center=(center_x, y_pos))
        screen.blit(center_label, center_rect)
        clickable_rects['center'] = pygame.Rect(center_x - 150, y_pos - 15, 300, 35)
        y_pos += 50
    else:
        y_pos += 10

    # Fog of War Toggle
    fog_enabled = settings_state.get('fog_of_war', False)
    fog_status = "[ON]" if fog_enabled else "[OFF]"
    fog_color = GREEN if fog_enabled else GRAY
    fog_text = text_font.render(f"Fog of War {fog_status}", True, fog_color)
    fog_rect = fog_text.get_rect(center=(center_x, y_pos))
    screen.blit(fog_text, fog_rect)
    clickable_rects['fog_of_war'] = pygame.Rect(center_x - 200, y_pos - 20, 400, 40)

    y_pos += 35
    fog_desc = tiny_font.render("Limited vision - only see nearby tiles", True, GRAY)
    fog_desc_rect = fog_desc.get_rect(center=(center_x, y_pos))
    screen.blit(fog_desc, fog_desc_rect)
    y_pos += 50

    # Energy Constraint Toggle
    energy_enabled = settings_state.get('energy_constraint', False)
    energy_status = "[ON]" if energy_enabled else "[OFF]"
    energy_color = GREEN if energy_enabled else GRAY
    energy_text = text_font.render(f"Energy Constraint {energy_status}", True, energy_color)
    energy_rect = energy_text.get_rect(center=(center_x, y_pos))
    screen.blit(energy_text, energy_rect)
    clickable_rects['energy_constraint'] = pygame.Rect(center_x - 225, y_pos - 20, 450, 40)

    y_pos += 35
    if energy_enabled:
        fuel_limit = settings_state.get('fuel_limit', 100)
        fuel_desc = tiny_font.render(f"Limited fuel: {fuel_limit} cost units (Click +/- to adjust)", True, GRAY)
        fuel_desc_rect = fuel_desc.get_rect(center=(center_x, y_pos))
        screen.blit(fuel_desc, fuel_desc_rect)

        y_pos += 30
        # Fuel adjustment buttons - centered layout
        button_spacing = 80
        minus_btn = small_font.render("[-]", True, WHITE)
        minus_rect = minus_btn.get_rect(center=(center_x - button_spacing, y_pos))
        screen.blit(minus_btn, minus_rect)
        clickable_rects['fuel_decrease'] = pygame.Rect(center_x - button_spacing - 20, y_pos - 15, 40, 30)

        fuel_value = text_font.render(str(fuel_limit), True, YELLOW)
        fuel_rect = fuel_value.get_rect(center=(center_x, y_pos))
        screen.blit(fuel_value, fuel_rect)

        plus_btn = small_font.render("[+]", True, WHITE)
        plus_rect = plus_btn.get_rect(center=(center_x + button_spacing, y_pos))
        screen.blit(plus_btn, plus_rect)
        clickable_rects['fuel_increase'] = pygame.Rect(center_x + button_spacing - 20, y_pos - 15, 40, 30)

        y_pos += 60
    else:
        energy_desc = tiny_font.render("Limited fuel cost for pathfinding", True, GRAY)
        energy_desc_rect = energy_desc.get_rect(center=(center_x, y_pos))
        screen.blit(energy_desc, energy_desc_rect)
        y_pos += 50

    # Instructions
    y_pos += 20
    inst_text = small_font.render("Click on settings to toggle them", True, GRAY)
    inst_rect = inst_text.get_rect(center=(MENU_WIDTH // 2, y_pos))
    screen.blit(inst_text, inst_rect)

    return clickable_rects
    y_pos += 50

    # Instructions
    y_pos += 20
    inst_text = small_font.render("Click on settings to toggle them", True, GRAY)
    inst_rect = inst_text.get_rect(center=(MENU_WIDTH // 2, y_pos))
    screen.blit(inst_text, inst_rect)

    return clickable_rects


def draw_game_mode_screen(screen, maze_mode, player_mode):
    """Draw the maze mode and player mode selection screen side by side"""
    title_font = pygame.font.Font(None, 72)
    text_font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 28)
    tiny_font = pygame.font.Font(None, 24)

    # Title
    title = title_font.render("Select Mode", True, YELLOW)
    title_rect = title.get_rect(center=(MENU_WIDTH // 2, 50))
    screen.blit(title, title_rect)

    # Calculate left and right column positions
    left_col_x = MENU_WIDTH // 4
    right_col_x = 3 * MENU_WIDTH // 4

    y_pos = 150

    # LEFT COLUMN: Maze Mode Section
    maze_mode_title = text_font.render("Maze Mode", True, YELLOW)
    maze_mode_title_rect = maze_mode_title.get_rect(center=(left_col_x, y_pos))
    screen.blit(maze_mode_title, maze_mode_title_rect)

    left_y = y_pos + 60

    # Explore Mode
    explore_text = "* Explore" if maze_mode == 'explore' else "Explore"
    explore_color = GREEN if maze_mode == 'explore' else WHITE
    explore_label = text_font.render(explore_text, True, explore_color)
    explore_rect = explore_label.get_rect(center=(left_col_x, left_y))
    screen.blit(explore_label, explore_rect)

    left_y += 35
    explore_desc = tiny_font.render("Static maze with", True, GRAY)
    explore_desc_rect = explore_desc.get_rect(center=(left_col_x, left_y))
    screen.blit(explore_desc, explore_desc_rect)
    left_y += 22
    explore_desc2 = tiny_font.render("fixed obstacles", True, GRAY)
    explore_desc2_rect = explore_desc2.get_rect(center=(left_col_x, left_y))
    screen.blit(explore_desc2, explore_desc2_rect)

    # Dynamic Mode
    left_y += 60
    dynamic_text = "* Dynamic" if maze_mode == 'dynamic' else "Dynamic"
    dynamic_color = GREEN if maze_mode == 'dynamic' else WHITE
    dynamic_label = text_font.render(dynamic_text, True, dynamic_color)
    dynamic_rect = dynamic_label.get_rect(center=(left_col_x, left_y))
    screen.blit(dynamic_label, dynamic_rect)

    left_y += 35
    dynamic_desc = tiny_font.render("Obstacles appear", True, GRAY)
    dynamic_desc_rect = dynamic_desc.get_rect(center=(left_col_x, left_y))
    screen.blit(dynamic_desc, dynamic_desc_rect)
    left_y += 22
    dynamic_desc2 = tiny_font.render("randomly as you play", True, GRAY)
    dynamic_desc2_rect = dynamic_desc2.get_rect(center=(left_col_x, left_y))
    screen.blit(dynamic_desc2, dynamic_desc2_rect)

    # Multi-Goal Mode
    left_y += 60
    multi_text = "* Multi-Goal" if maze_mode == 'multi-goal' else "Multi-Goal"
    multi_color = GREEN if maze_mode == 'multi-goal' else WHITE
    multi_label = text_font.render(multi_text, True, multi_color)
    multi_rect = multi_label.get_rect(center=(left_col_x, left_y))
    screen.blit(multi_label, multi_rect)

    left_y += 35
    multi_desc = tiny_font.render("Collect checkpoints,", True, GRAY)
    multi_desc_rect = multi_desc.get_rect(center=(left_col_x, left_y))
    screen.blit(multi_desc, multi_desc_rect)
    left_y += 22
    multi_desc2 = tiny_font.render("cost resets at each", True, GRAY)
    multi_desc2_rect = multi_desc2.get_rect(center=(left_col_x, left_y))
    screen.blit(multi_desc2, multi_desc2_rect)

    # RIGHT COLUMN: Game Mode Section (Solo/Competitive)
    right_y = y_pos
    player_mode_title = text_font.render("Game Mode", True, YELLOW)
    player_mode_title_rect = player_mode_title.get_rect(center=(right_col_x, right_y))
    screen.blit(player_mode_title, player_mode_title_rect)

    right_y += 60

    # Solo Mode
    solo_text = "* Solo" if player_mode == 'solo' else "Solo"
    solo_color = GREEN if player_mode == 'solo' else WHITE
    solo_label = text_font.render(solo_text, True, solo_color)
    solo_rect = solo_label.get_rect(center=(right_col_x, right_y))
    screen.blit(solo_label, solo_rect)

    right_y += 35
    solo_desc = tiny_font.render("Play alone and", True, GRAY)
    solo_desc_rect = solo_desc.get_rect(center=(right_col_x, right_y))
    screen.blit(solo_desc, solo_desc_rect)
    right_y += 22
    solo_desc2 = tiny_font.render("solve the maze", True, GRAY)
    solo_desc2_rect = solo_desc2.get_rect(center=(right_col_x, right_y))
    screen.blit(solo_desc2, solo_desc2_rect)

    # Competitive Mode
    right_y += 60
    comp_text = "* Competitive" if player_mode == 'competitive' else "Competitive"
    comp_color = GREEN if player_mode == 'competitive' else WHITE
    comp_label = text_font.render(comp_text, True, comp_color)
    comp_rect = comp_label.get_rect(center=(right_col_x, right_y))
    screen.blit(comp_label, comp_rect)

    right_y += 35
    comp_desc = tiny_font.render("Race against", True, GRAY)
    comp_desc_rect = comp_desc.get_rect(center=(right_col_x, right_y))
    screen.blit(comp_desc, comp_desc_rect)
    right_y += 22
    comp_desc2 = tiny_font.render("AI agents", True, GRAY)
    comp_desc2_rect = comp_desc2.get_rect(center=(right_col_x, right_y))
    screen.blit(comp_desc2, comp_desc2_rect)

    # Multi-Agent Mode
    right_y += 60
    multi_agent_text = "* Multi-Agent" if player_mode == 'multi-agent' else "Multi-Agent"
    multi_agent_color = GREEN if player_mode == 'multi-agent' else WHITE
    multi_agent_label = text_font.render(multi_agent_text, True, multi_agent_color)
    multi_agent_rect = multi_agent_label.get_rect(center=(right_col_x, right_y))
    screen.blit(multi_agent_label, multi_agent_rect)

    right_y += 35
    multi_agent_desc = tiny_font.render("Multiple AIs compete", True, GRAY)
    multi_agent_desc_rect = multi_agent_desc.get_rect(center=(right_col_x, right_y))
    screen.blit(multi_agent_desc, multi_agent_desc_rect)
    right_y += 22
    multi_agent_desc2 = tiny_font.render("for the same goal", True, GRAY)
    multi_agent_desc2_rect = multi_agent_desc2.get_rect(center=(right_col_x, right_y))
    screen.blit(multi_agent_desc2, multi_agent_desc2_rect)

    # Algorithm Comparison Mode
    right_y += 60
    algo_text = "* Algo Compare" if player_mode == 'algo-compare' else "Algo Compare"
    algo_color = GREEN if player_mode == 'algo-compare' else WHITE
    algo_label = small_font.render(algo_text, True, algo_color)
    algo_rect = algo_label.get_rect(center=(right_col_x, right_y))
    screen.blit(algo_label, algo_rect)

    right_y += 30
    algo_desc = tiny_font.render("Compare BFS, Dijkstra", True, GRAY)
    algo_desc_rect = algo_desc.get_rect(center=(right_col_x, right_y))
    screen.blit(algo_desc, algo_desc_rect)
    right_y += 22
    algo_desc2 = tiny_font.render("and A* algorithms", True, GRAY)
    algo_desc2_rect = algo_desc2.get_rect(center=(right_col_x, right_y))
    screen.blit(algo_desc2, algo_desc2_rect)

    # Vertical separator line
    separator_x = MENU_WIDTH // 2
    pygame.draw.line(screen, GRAY, (separator_x, 140), (separator_x, 650), 2)

    # Instructions
    inst_y = 720
    inst_text = "Click on options to select them"
    inst_label = small_font.render(inst_text, True, GRAY)
    inst_rect = inst_label.get_rect(center=(MENU_WIDTH // 2, inst_y))
    screen.blit(inst_label, inst_rect)

    return {
        'explore': pygame.Rect(left_col_x - 100, 210 - 20, 200, 77),
        'dynamic': pygame.Rect(left_col_x - 100, 327 - 20, 200, 77),
        'multi-goal': pygame.Rect(left_col_x - 100, 444 - 20, 200, 77),
        'solo': pygame.Rect(right_col_x - 100, 210 - 20, 200, 77),
        'competitive': pygame.Rect(right_col_x - 100, 327 - 20, 200, 77),
        'multi-agent': pygame.Rect(right_col_x - 100, 444 - 20, 200, 77),
        'algo-compare': pygame.Rect(right_col_x - 100, 561 - 20, 200, 70)
    }


def show_menu():
    """Display the main menu and handle user input"""
    # Game settings
    goal_placement = 'corner'  # Default: bottom-right corner
    maze_mode = 'explore'  # Default: explore mode (renamed from game_mode)
    player_mode = 'solo'  # Default: solo mode

    # Settings state dictionary
    settings_state = {
        'goal_placement': 'corner',
        'goal_mode_expanded': False,
        'fog_of_war': False,
        'energy_constraint': False,
        'fuel_limit': 100
    }

    # Create buttons
    button_width = 300
    button_height = 60
    button_x = (MENU_WIDTH - button_width) // 2
    start_y = 250

    start_button = Button(button_x, start_y, button_width, button_height, "Start Game", BLUE, GREEN)
    settings_button = Button(button_x, start_y + 90, button_width, button_height, "Settings", BLUE, GREEN)
    controls_button = Button(button_x, start_y + 180, button_width, button_height, "Controls", BLUE, GREEN)
    guide_button = Button(button_x, start_y + 270, button_width, button_height, "Guide", BLUE, GREEN)
    quit_button = Button(button_x, start_y + 360, button_width, button_height, "Quit", RED, YELLOW)
    back_button = Button(button_x, MENU_HEIGHT - 120, button_width, button_height, "Back", GRAY, GREEN)
    continue_button = Button(button_x, MENU_HEIGHT - 120, button_width, button_height, "Continue", GREEN, YELLOW)

    current_screen = "main"  # Can be "main", "controls", "settings", "guide", or "game_mode"
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
                    if current_screen in ["controls", "settings", "game_mode", "guide"]:
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
            guide_button.update(mouse_pos)
            quit_button.update(mouse_pos)

            start_button.draw(screen)
            settings_button.draw(screen)
            controls_button.draw(screen)
            guide_button.draw(screen)
            quit_button.draw(screen)

            # Check for button clicks
            if start_button.is_clicked(mouse_pos, mouse_click):
                current_screen = "game_mode"  # Go to game mode selection

            if settings_button.is_clicked(mouse_pos, mouse_click):
                current_screen = "settings"

            if controls_button.is_clicked(mouse_pos, mouse_click):
                current_screen = "controls"

            if guide_button.is_clicked(mouse_pos, mouse_click):
                current_screen = "guide"

            if quit_button.is_clicked(mouse_pos, mouse_click):
                pygame.quit()
                sys.exit()

        elif current_screen == "game_mode":
            # Draw game mode selection screen
            option_rects = draw_game_mode_screen(screen, maze_mode, player_mode)

            # Check for clicks on maze mode and player mode options
            if mouse_click:
                if option_rects['explore'].collidepoint(mouse_pos):
                    maze_mode = 'explore'
                elif option_rects['dynamic'].collidepoint(mouse_pos):
                    maze_mode = 'dynamic'
                elif option_rects['multi-goal'].collidepoint(mouse_pos):
                    maze_mode = 'multi-goal'
                elif option_rects['solo'].collidepoint(mouse_pos):
                    player_mode = 'solo'
                elif option_rects['competitive'].collidepoint(mouse_pos):
                    player_mode = 'competitive'
                elif option_rects['multi-agent'].collidepoint(mouse_pos):
                    player_mode = 'multi-agent'
                elif option_rects['algo-compare'].collidepoint(mouse_pos):
                    player_mode = 'algo-compare'

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
                # Sync settings from settings_state
                goal_placement = settings_state['goal_placement']
                fog_of_war = settings_state['fog_of_war']
                energy_constraint = settings_state['energy_constraint']
                fuel_limit = settings_state['fuel_limit']
                return ("start", goal_placement, maze_mode, player_mode, fog_of_war, energy_constraint, fuel_limit)  # Start the game with settings

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

        elif current_screen == "guide":
            # Draw guide screen
            draw_guide_screen(screen)

            # Update and draw back button
            back_button.update(mouse_pos)
            back_button.draw(screen)

            # Check for back button click
            if back_button.is_clicked(mouse_pos, mouse_click):
                current_screen = "main"

        pygame.display.flip()

    pygame.quit()
    sys.exit()


def reinitialize_pygame():
    """Reinitialize pygame after a game session"""
    global screen, clock
    pygame.init()
    screen = pygame.display.set_mode((MENU_WIDTH, MENU_HEIGHT))
    pygame.display.set_caption("Maze Runner - Main Menu")
    clock = pygame.time.Clock()


if __name__ == "__main__":
    # Import main at the start
    import main
    import multi_agent_mode

    while True:  # Loop to return to menu after game ends
        result = show_menu()

        if result[0] == "start":
            # Get settings
            goal_placement = result[1]
            maze_mode = result[2]
            player_mode = result[3]
            fog_of_war = result[4] if len(result) > 4 else False
            energy_constraint = result[5] if len(result) > 5 else False
            fuel_limit = result[6] if len(result) > 6 else 100

            # Start the appropriate game mode
            if player_mode == 'multi-agent':
                # Multi-agent mode: 4 AIs compete from corners to center
                num_agents = 4  # Fixed: 4 agents starting from each corner
                multi_agent_mode.start(goal_placement, maze_mode, num_agents, fog_of_war, energy_constraint, fuel_limit)
            elif player_mode == 'algo-compare':
                # Algorithm comparison mode (not yet implemented)
                print("Algorithm comparison mode coming soon!")
                main.start(goal_placement, maze_mode, 5, player_mode, fog_of_war, energy_constraint, fuel_limit)
            else:
                # Solo or competitive mode
                main.start(goal_placement, maze_mode, 5, player_mode, fog_of_war, energy_constraint, fuel_limit)

            # Reinitialize pygame after game ends (pygame.quit() is called in main.py)
            reinitialize_pygame()
        else:
            break  # Exit if user quits from menu
