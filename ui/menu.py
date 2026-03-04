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
    
    def __init__(self, on_start_game: Callable[[str], None]):
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
        input_y = SCREEN_HEIGHT // 2 - 50
        self.username_input = TextInput(input_x, input_y, input_width, input_height)
        
        # Start button
        button_width = 200
        button_height = 50
        button_x = (SCREEN_WIDTH - button_width) // 2
        button_y = SCREEN_HEIGHT // 2 + 30
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
        
        if self.start_button.handle_event(event):
            username = self.username_input.get_text().strip()
            if username:
                self.on_start_game(username)
    
    def update(self, dt: float):
        """Update menu state"""
        self.username_input.update(dt)
    
    def draw(self, screen: pygame.Surface):
        """Draw the menu"""
        # Draw background
        screen.fill(SKY_BLUE := (135, 206, 235))
        
        # Draw decorative grass at bottom
        grass_rect = pygame.Rect(0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100)
        pygame.draw.rect(screen, (34, 139, 34), grass_rect)
        
        # Draw title with shadow
        title_shadow = self.title_font.render(self.title_text, True, (0, 50, 0))
        shadow_rect = title_shadow.get_rect(center=(SCREEN_WIDTH // 2 + 3, 150 + 3))
        screen.blit(title_shadow, shadow_rect)
        
        title_surface = self.title_font.render(self.title_text, True, YELLOW)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title_surface, title_rect)
        
        # Draw subtitle
        subtitle_font = pygame.font.SysFont(FONT_NAME, 28)
        subtitle = subtitle_font.render("A Grid-Based Farming Adventure", True, DARK_GREEN)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 210))
        screen.blit(subtitle, subtitle_rect)
        
        # Draw username label
        label_font = pygame.font.SysFont(FONT_NAME, 24)
        label = label_font.render("Enter your name:", True, BLACK)
        label_rect = label.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        screen.blit(label, label_rect)
        
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