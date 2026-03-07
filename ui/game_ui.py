"""
In-Game UI Components
"""
import pygame
import sys
import os
from typing import Optional
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    SCREEN_WIDTH, WHITE, BLACK, GREEN, DARK_GREEN, YELLOW, 
    GAME_UI_SIZE, FONT_NAME, GRID_OFFSET_Y
)
from ui.menu import Button


class GameUI:
    """Handles the in-game user interface"""
    
    def __init__(self, username: str):
        self.username = username
        self.font = pygame.font.SysFont(FONT_NAME, GAME_UI_SIZE, bold=True)
        self.title_font = pygame.font.SysFont(FONT_NAME, 32, bold=True)
        self.button_font = pygame.font.SysFont(FONT_NAME, 20, bold=True)
        
        # UI State
        self.selected_cell_text = None
        self.save_button = Button(
            SCREEN_WIDTH - 260,
            15,
            110,
            36,
            "Save",
            GREEN,
            DARK_GREEN
        )
        self.menu_button = Button(
            SCREEN_WIDTH - 140,
            15,
            110,
            36,
            "Menu",
            (120, 120, 120),
            (150, 150, 150)
        )
    
    def update(self, selected_cell: tuple = None):
        """Update UI state"""
        self.selected_cell_text = selected_cell
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Handle UI events and return action name when clicked."""
        if self.save_button.handle_event(event):
            return "save"
        if self.menu_button.handle_event(event):
            return "menu"
        return None
    
    def draw(self, screen: pygame.Surface):
        """Draw the game UI"""
        # Draw top bar background
        top_bar = pygame.Rect(0, 0, SCREEN_WIDTH, GRID_OFFSET_Y - 10)
        pygame.draw.rect(screen, (50, 30, 20), top_bar)  # Dark brown
        pygame.draw.rect(screen, (139, 69, 19), top_bar, 3)  # Brown border
        
        # Draw username (top-left)
        username_text = f"Farmer: {self.username}"
        username_surface = self.font.render(username_text, True, YELLOW)
        username_rect = username_surface.get_rect(topleft=(20, 20))
        screen.blit(username_surface, username_rect)
        
        # Draw welcome message
        welcome_text = "Welcome to your farm!"
        welcome_surface = self.font.render(welcome_text, True, WHITE)
        welcome_rect = welcome_surface.get_rect(topleft=(20, 50))
        screen.blit(welcome_surface, welcome_rect)
        
        # Draw selected cell info (top-right)
        if self.selected_cell_text:
            col, row = self.selected_cell_text
            cell_text = f"Selected: Grid ({col}, {row})"
            cell_surface = self.font.render(cell_text, True, WHITE)
            cell_rect = cell_surface.get_rect(topright=(SCREEN_WIDTH - 20, 20))
            screen.blit(cell_surface, cell_rect)
        
        # Draw controls hint
        controls_text = "WASD: Move | Click: Select | ESC: Quit"
        controls_surface = self.font.render(controls_text, True, (200, 200, 200))
        controls_rect = controls_surface.get_rect(topright=(SCREEN_WIDTH - 170, 50))
        screen.blit(controls_surface, controls_rect)
        
        # Draw game title (centered)
        title_surface = self.title_font.render("Farm Life", True, YELLOW)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 40))
        screen.blit(title_surface, title_rect)
        
        # Draw save button
        self.save_button.draw(screen, self.button_font)
        self.menu_button.draw(screen, self.button_font)
        
        # Draw decorative line under title
        pygame.draw.line(screen, YELLOW, 
                        (SCREEN_WIDTH // 2 - 80, 60), 
                        (SCREEN_WIDTH // 2 + 80, 60), 2)