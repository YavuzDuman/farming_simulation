"""
Main Menu UI
"""
import pygame
from typing import Callable, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GREEN, DARK_GREEN, 
    YELLOW, GRAY, LIGHT_GRAY, MENU_TITLE_SIZE, MENU_BUTTON_SIZE, FONT_NAME
)


class Button:
    """A clickable button"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 text: str, color: tuple, hover_color: tuple):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events, returns True if clicked"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        """Draw the button"""
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=10)
        
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class TextInput:
    """A text input field"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 placeholder: str = "Enter username..."):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
    
    def handle_event(self, event: pygame.event.Event):
        """Handle input events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False
            elif len(self.text) < 15:  # Limit username length
                if event.unicode.isalnum() or event.unicode in '_-':
                    self.text += event.unicode
    
    def update(self, dt: float):
        """Update cursor blink"""
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        """Draw the input field"""
        # Draw background
        color = WHITE if self.active else LIGHT_GRAY
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        
        # Draw border
        border_color = GREEN if self.active else GRAY
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=5)
        
        # Draw text or placeholder
        if self.text:
            text_surface = font.render(self.text, True, BLACK)
        else:
            text_surface = font.render(self.placeholder, True, GRAY)
        
        text_rect = text_surface.get_rect(midleft=(self.rect.left + 10, self.rect.centery))
        screen.blit(text_surface, text_rect)
        
        # Draw cursor
        if self.active and self.cursor_visible:
            cursor_x = text_rect.right + 2
            pygame.draw.line(screen, BLACK, 
                           (cursor_x, self.rect.top + 5),
                           (cursor_x, self.rect.bottom - 5), 2)
    
    def get_text(self) -> str:
        """Get the current text"""
        return self.text


class Menu:
    """Main menu screen"""
    
    def __init__(self, on_start_game: Callable[[str, tuple], None]):
        self.on_start_game = on_start_game
        
        # Fonts
        self.title_font = pygame.font.SysFont(FONT_NAME, MENU_TITLE_SIZE, bold=True)
        self.button_font = pygame.font.SysFont(FONT_NAME, MENU_BUTTON_SIZE)
        self.input_font = pygame.font.SysFont(FONT_NAME, MENU_BUTTON_SIZE)
        
        # Title
        self.title_text = "Farm Life"
        
        # Username input
        input_width = 300
        input_height = 50
        input_x = (SCREEN_WIDTH - input_width) // 2
        input_y = SCREEN_HEIGHT // 2 - 100
        self.username_input = TextInput(input_x, input_y, input_width, input_height)
        
        # Shirt color selection
        self.shirt_colors = [
            (70, 130, 180),  # Steel Blue
            (180, 70, 70),   # Red
            (70, 180, 70),   # Green
            (180, 180, 70),  # Yellow
            (180, 70, 180),  # Purple
            (70, 180, 180)   # Cyan
        ]
        self.selected_color_idx = 0
        self.color_swatches = []
        swatch_size = 40
        swatch_spacing = 15
        total_swatches_width = len(self.shirt_colors) * swatch_size + (len(self.shirt_colors) - 1) * swatch_spacing
        start_x = (SCREEN_WIDTH - total_swatches_width) // 2
        swatch_y = SCREEN_HEIGHT // 2 + 30
        
        for i, color in enumerate(self.shirt_colors):
            rect = pygame.Rect(start_x + i * (swatch_size + swatch_spacing), swatch_y, swatch_size, swatch_size)
            self.color_swatches.append(rect)

        # Start button
        button_width = 200
        button_height = 50
        button_x = (SCREEN_WIDTH - button_width) // 2
        button_y = SCREEN_HEIGHT // 2 + 120
        self.start_button = Button(
            button_x, button_y, button_width, button_height,
            "Start Game", GREEN, DARK_GREEN
        )
        
        # Instructions
        self.instructions = [
            "Use WASD keys to move your farmer",
            "Click on grid cells to select them",
            "Press ESC to pause the game"
        ]
    
    def handle_event(self, event: pygame.event.Event):
        """Handle menu events"""
        self.username_input.handle_event(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for i, rect in enumerate(self.color_swatches):
                    if rect.collidepoint(event.pos):
                        self.selected_color_idx = i
                        break

        if self.start_button.handle_event(event):
            username = self.username_input.get_text().strip()
            if username:
                self.on_start_game(username, self.shirt_colors[self.selected_color_idx])
    
    def update(self, dt: float):
        """Update menu state"""
        self.username_input.update(dt)
    
    def draw(self, screen: pygame.Surface):
        """Draw the menu"""
        # Draw background
        screen.fill(SKY_BLUE := (135, 206, 235))
        self._draw_farm_background(screen)
        
        # Draw title with shadow
        title_shadow = self.title_font.render(self.title_text, True, (0, 50, 0))
        shadow_rect = title_shadow.get_rect(center=(SCREEN_WIDTH // 2 + 3, 120 + 3))
        screen.blit(title_shadow, shadow_rect)
        
        title_surface = self.title_font.render(self.title_text, True, YELLOW)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 120))
        screen.blit(title_surface, title_rect)
        
        # Draw subtitle
        subtitle_font = pygame.font.SysFont(FONT_NAME, 28)
        subtitle = subtitle_font.render("A Grid-Based Farming Adventure", True, DARK_GREEN)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 180))
        screen.blit(subtitle, subtitle_rect)
        
        # Draw username label
        label_font = pygame.font.SysFont(FONT_NAME, 24)
        label = label_font.render("Enter your name:", True, BLACK)
        label_rect = label.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 130))
        screen.blit(label, label_rect)
        
        # Draw color selection label
        color_label = label_font.render("Select Shirt Color:", True, BLACK)
        color_label_rect = color_label.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        screen.blit(color_label, color_label_rect)

        # Draw swatches
        for i, rect in enumerate(self.color_swatches):
            pygame.draw.rect(screen, self.shirt_colors[i], rect, border_radius=5)
            if i == self.selected_color_idx:
                pygame.draw.rect(screen, WHITE, rect, 3, border_radius=5)
            else:
                pygame.draw.rect(screen, BLACK, rect, 1, border_radius=5)

        # Draw input and button
        self.username_input.draw(screen, self.input_font)
        self.start_button.draw(screen, self.button_font)
        
        # Draw instructions
        instruction_font = pygame.font.SysFont(FONT_NAME, 20)
        y_start = SCREEN_HEIGHT - 180
        for i, instruction in enumerate(self.instructions):
            inst_surface = instruction_font.render(instruction, True, BLACK)
            inst_rect = inst_surface.get_rect(center=(SCREEN_WIDTH // 2, y_start + i * 25))
            screen.blit(inst_surface, inst_rect)

    def _draw_farm_background(self, screen: pygame.Surface):
        """Draw a scenic farm background with animals and trees."""
        horizon_y = int(SCREEN_HEIGHT * 0.52)
        # Far hills
        pygame.draw.ellipse(screen, (120, 190, 120), (-120, horizon_y - 140, 520, 240))
        pygame.draw.ellipse(screen, (110, 180, 110), (260, horizon_y - 160, 620, 280))
        pygame.draw.ellipse(screen, (100, 170, 100), (760, horizon_y - 150, 620, 260))

        # Tree line
        for x in range(60, SCREEN_WIDTH, 220):
            self._draw_background_tree(screen, x, horizon_y + 20, scale=0.7)
            self._draw_background_tree(screen, x + 80, horizon_y + 10, scale=0.8)

        # Farmland bands
        pygame.draw.rect(screen, (78, 155, 78), (0, horizon_y, SCREEN_WIDTH, 120))
        pygame.draw.rect(screen, (92, 168, 92), (0, horizon_y + 110, SCREEN_WIDTH, 120))

        # Main grass foreground
        grass_rect = pygame.Rect(0, SCREEN_HEIGHT - 160, SCREEN_WIDTH, 160)
        pygame.draw.rect(screen, (34, 139, 34), grass_rect)
        pygame.draw.rect(screen, (20, 110, 20), grass_rect, 4)

        # Farm houses
        self._draw_background_house(screen, 220, horizon_y + 40)
        self._draw_background_house(screen, SCREEN_WIDTH - 320, horizon_y + 30, scale=0.9)

        # Pasture fence
        self._draw_fence_line(screen, 0, horizon_y + 140, SCREEN_WIDTH)

        # Animals
        self._draw_cow(screen, 520, horizon_y + 160)
        self._draw_cow(screen, 700, horizon_y + 170, scale=0.9)
        self._draw_chicken(screen, 980, horizon_y + 190)
        self._draw_chicken(screen, 1060, horizon_y + 200, scale=0.8)

        # Crops in foreground
        for i in range(12):
            self._draw_crop(screen, 420 + i * 60, SCREEN_HEIGHT - 120)

        # Soft haze for depth
        haze_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(haze_surface, (255, 255, 255, 25), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(haze_surface, (0, 0))

    def _draw_background_tree(self, screen: pygame.Surface, x: int, y: int, scale: float = 1.0):
        """Draw a stylized tree for background"""
        trunk_width = int(20 * scale)
        trunk_height = int(40 * scale)
        pygame.draw.rect(screen, (101, 67, 33), (x - trunk_width // 2, y, trunk_width, trunk_height))
        pygame.draw.circle(screen, (34, 139, 34), (x, y - int(10 * scale)), int(35 * scale))
        pygame.draw.circle(screen, (50, 180, 50), (x - int(15 * scale), y - int(20 * scale)), int(25 * scale))
        pygame.draw.circle(screen, (50, 180, 50), (x + int(15 * scale), y - int(20 * scale)), int(25 * scale))

    def _draw_background_house(self, screen: pygame.Surface, x: int, y: int, scale: float = 1.0):
        """Draw a simple house silhouette in the background."""
        house_width = int(160 * scale)
        house_height = int(100 * scale)
        wall_rect = pygame.Rect(x, y, house_width, house_height)
        pygame.draw.rect(screen, (220, 200, 170), wall_rect)
        pygame.draw.rect(screen, (170, 140, 110), wall_rect, 3)

        roof_points = [
            (x - int(10 * scale), y),
            (x + house_width // 2, y - int(60 * scale)),
            (x + house_width + int(10 * scale), y)
        ]
        pygame.draw.polygon(screen, (180, 90, 50), roof_points)
        pygame.draw.polygon(screen, (140, 70, 40), roof_points, 2)

        door_rect = pygame.Rect(
            x + house_width // 2 - int(16 * scale),
            y + house_height - int(44 * scale),
            int(32 * scale),
            int(44 * scale)
        )
        pygame.draw.rect(screen, (120, 70, 40), door_rect)
        pygame.draw.rect(screen, (80, 50, 30), door_rect, 2)

        window_rect = pygame.Rect(
            x + int(20 * scale),
            y + int(24 * scale),
            int(30 * scale),
            int(24 * scale)
        )
        pygame.draw.rect(screen, (190, 220, 250), window_rect)
        pygame.draw.rect(screen, (120, 90, 70), window_rect, 2)

    def _draw_fence_line(self, screen: pygame.Surface, x: int, y: int, width: int):
        """Draw a simple fence line across the scene."""
        post_color = (210, 180, 140)
        rail_color = (190, 160, 120)
        for i in range(x, x + width, 80):
            pygame.draw.rect(screen, post_color, (i, y - 12, 10, 30))
        pygame.draw.rect(screen, rail_color, (x, y - 6, width, 6))
        pygame.draw.rect(screen, rail_color, (x, y + 8, width, 6))

    def _draw_cow(self, screen: pygame.Surface, x: int, y: int, scale: float = 1.0):
        """Draw a simple cow figure."""
        body_width = int(70 * scale)
        body_height = int(40 * scale)
        body_rect = pygame.Rect(x, y, body_width, body_height)
        pygame.draw.ellipse(screen, (245, 245, 245), body_rect)
        pygame.draw.ellipse(screen, (30, 30, 30), (x + int(10 * scale), y + int(8 * scale), int(18 * scale), int(14 * scale)))
        pygame.draw.ellipse(screen, (30, 30, 30), (x + int(36 * scale), y + int(12 * scale), int(20 * scale), int(12 * scale)))

        head_rect = pygame.Rect(x - int(18 * scale), y + int(8 * scale), int(20 * scale), int(18 * scale))
        pygame.draw.ellipse(screen, (245, 245, 245), head_rect)
        pygame.draw.circle(screen, (30, 30, 30), (x - int(6 * scale), y + int(16 * scale)), int(3 * scale))

        for leg_offset in [10, 24, 44, 58]:
            pygame.draw.line(
                screen,
                (90, 70, 50),
                (x + int(leg_offset * scale), y + body_height),
                (x + int(leg_offset * scale), y + body_height + int(16 * scale)),
                4
            )

    def _draw_chicken(self, screen: pygame.Surface, x: int, y: int, scale: float = 1.0):
        """Draw a simple chicken figure."""
        pygame.draw.circle(screen, (255, 255, 255), (x, y), int(12 * scale))
        pygame.draw.circle(screen, (255, 255, 255), (x + int(12 * scale), y - int(4 * scale)), int(8 * scale))
        pygame.draw.circle(screen, (220, 50, 50), (x + int(18 * scale), y - int(6 * scale)), int(3 * scale))
        pygame.draw.polygon(screen, (255, 200, 0), [
            (x + int(20 * scale), y),
            (x + int(28 * scale), y - int(4 * scale)),
            (x + int(20 * scale), y - int(8 * scale))
        ])
        pygame.draw.line(
            screen,
            (150, 100, 50),
            (x - int(4 * scale), y + int(12 * scale)),
            (x - int(8 * scale), y + int(18 * scale)),
            2
        )
        pygame.draw.line(
            screen,
            (150, 100, 50),
            (x + int(4 * scale), y + int(12 * scale)),
            (x + int(8 * scale), y + int(18 * scale)),
            2
        )

    def _draw_crop(self, screen, x, y):
        """Draw a small crop figure"""
        pygame.draw.line(screen, (100, 200, 100), (x, y), (x, y - 15), 3)
        pygame.draw.ellipse(screen, (218, 165, 32), (x - 4, y - 25, 8, 12))