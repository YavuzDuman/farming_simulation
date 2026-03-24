"""
In-Game UI Components
"""
import pygame
import sys
import os
import time
from typing import Optional, List, Tuple
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    SCREEN_WIDTH, WHITE, BLACK, GREEN, DARK_GREEN, YELLOW, 
    GAME_UI_SIZE, FONT_NAME, GRID_OFFSET_Y, GRID_OFFSET_X, GRID_COLS, GRID_SIZE,
    HEALTH_RED, HEALTH_BG
)
from ui.menu import Button


class XPMessage:
    """A single XP notification message"""
    
    def __init__(self, activity: str, xp_amount: int, x: int, y: int):
        self.activity = activity
        self.xp_amount = xp_amount
        self.x = x
        self.y = y
        self.created_time = time.time()
        self.duration = 5.0  # 5 seconds display time
        self.alpha = 255
        
        # Format activity name for display - SHORTER text to fit
        self.display_text = self._format_activity(activity, xp_amount)
    
    def _format_activity(self, activity: str, xp: int) -> str:
        """Format the activity name for display - shorter text"""
        if activity.startswith('tree_'):
            size = activity.split('_')[1]
            return f"+{xp} XP - {size} tree"
        elif activity.startswith('stone_'):
            size = activity.split('_')[1]
            return f"+{xp} XP - {size} stone"
        elif activity == 'plant_seed':
            return f"+{xp} XP - planted"
        elif activity == 'harvest_plant':
            return f"+{xp} XP - harvested"
        else:
            return f"+{xp} XP"
    
    def is_expired(self) -> bool:
        """Check if the message has expired"""
        return time.time() - self.created_time >= self.duration
    
    def get_alpha(self) -> int:
        """Get current alpha value for fade effect"""
        elapsed = time.time() - self.created_time
        if elapsed > self.duration - 1.0:  # Start fading in last second
            fade_progress = (elapsed - (self.duration - 1.0)) / 1.0
            # Clamp fade_progress to valid range [0, 1]
            fade_progress = max(0.0, min(1.0, fade_progress))
            return int(255 * (1.0 - fade_progress))
        return 255


class TempMessage:
    """A simple temporary text message (for notifications without XP)"""
    
    def __init__(self, text: str, x: int, y: int, color: tuple = (255, 255, 100)):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.created_time = time.time()
        self.duration = 3.0  # 3 seconds display time
    
    def is_expired(self) -> bool:
        return time.time() - self.created_time >= self.duration
    
    def get_alpha(self) -> int:
        elapsed = time.time() - self.created_time
        if elapsed > self.duration - 1.0:
            fade_progress = (elapsed - (self.duration - 1.0)) / 1.0
            fade_progress = max(0.0, min(1.0, fade_progress))
            return int(255 * (1.0 - fade_progress))
        return 255


class GameUI:
    """Handles the in-game user interface"""
    
    def __init__(self, username: str):
        self.username = username
        self.font = pygame.font.SysFont(FONT_NAME, GAME_UI_SIZE, bold=True)
        self.title_font = pygame.font.SysFont(FONT_NAME, 32, bold=True)
        self.button_font = pygame.font.SysFont(FONT_NAME, 20, bold=True)
        self.small_font = pygame.font.SysFont(FONT_NAME, 16, bold=True)
        self.message_font = pygame.font.SysFont(FONT_NAME, 18, bold=True)
        self.money_font = pygame.font.SysFont(FONT_NAME, 22, bold=True)
        
        # UI State
        self.selected_cell_text = None
        self.show_health_bar = False
        
        # Weather display
        self.weather_text = "☀️ Sunny"
        
        # Temporary messages (for notifications)
        self.temp_messages: List[TempMessage] = []
        
        # XP Bar settings
        self.xp_bar_width = 200
        self.xp_bar_height = 20
        self.xp_bar_x = 20
        self.xp_bar_y = 70
        
        # Health Bar settings
        self.health_bar_width = 200
        self.health_bar_height = 20
        self.health_bar_x = SCREEN_WIDTH // 2 - 100
        self.health_bar_y = 85
        
        # XP display values (updated by game manager)
        self.player_level = 1
        self.player_xp = 0
        self.xp_to_next = 100
        self.xp_percentage = 0
        
        # Money display (updated by game manager)
        self.player_money = 100
        
        # Health display
        self.player_health = 100
        self.player_max_health = 100
        
        # XP Message box settings (top right of visible area, below top bar)
        self.xp_messages: List[XPMessage] = []
        self.message_box_x = SCREEN_WIDTH - 240  # Position from right edge
        self.message_box_y = GRID_OFFSET_Y + 10  # Below top bar
        self.message_box_width = 230  # Wider to fit text
        self.message_box_height = 80
        self.message_spacing = 28
        
        self.tasks_button = Button(
            SCREEN_WIDTH - 380,
            15,
            110,
            36,
            "Tasks",
            (80, 110, 160),
            (100, 140, 190)
        )
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
    
    def add_xp_message(self, activity: str, xp_amount: int):
        """Add a new XP notification message"""
        # Calculate position (stack from top)
        y_offset = len(self.xp_messages) * self.message_spacing
        msg = XPMessage(activity, xp_amount, self.message_box_x, self.message_box_y + y_offset)
        self.xp_messages.append(msg)
    
    def show_message(self, text: str, color: tuple = (255, 255, 100)):
        """Show a temporary notification message"""
        # Calculate position (stack below existing temp messages)
        y_offset = len(self.temp_messages) * self.message_spacing
        msg = TempMessage(text, self.message_box_x, self.message_box_y + y_offset, color)
        self.temp_messages.append(msg)
    
    def update(self, selected_cell: tuple = None):
        """Update UI state"""
        self.selected_cell_text = selected_cell
        
        # Remove expired messages
        self.xp_messages = [msg for msg in self.xp_messages if not msg.is_expired()]
        self.temp_messages = [msg for msg in self.temp_messages if not msg.is_expired()]
        
        # Update message positions
        for i, msg in enumerate(self.xp_messages):
            msg.y = self.message_box_y + i * self.message_spacing
        for i, msg in enumerate(self.temp_messages):
            msg.y = self.message_box_y + i * self.message_spacing
    
    def update_xp_display(self, level: int, xp: int, xp_to_next: int, percentage: float):
        """Update the XP display values"""
        self.player_level = level
        self.player_xp = xp
        self.xp_to_next = xp_to_next
        self.xp_percentage = percentage
    
    def update_money_display(self, money: int):
        """Update the money display value"""
        self.player_money = money
    
    def update_weather_display(self, weather_text: str):
        """Update the weather display text"""
        self.weather_text = weather_text
    
    def update_health_display(self, health: int, max_health: int, show: bool):
        """Update the health display values"""
        self.player_health = health
        self.player_max_health = max_health
        self.show_health_bar = show
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Handle UI events and return action name when clicked."""
        if self.tasks_button.handle_event(event):
            return "tasks"
        if self.save_button.handle_event(event):
            return "save"
        if self.menu_button.handle_event(event):
            return "menu"
        return None
    
    def _draw_xp_bar(self, screen: pygame.Surface):
        """Draw the XP/Level bar in the top left"""
        # Draw level badge
        level_text = f"Lv.{self.player_level}"
        level_surface = self.font.render(level_text, True, YELLOW)
        level_rect = level_surface.get_rect(topleft=(self.xp_bar_x, self.xp_bar_y - 5))
        screen.blit(level_surface, level_rect)
        
        # Calculate bar position (to the right of level badge)
        bar_x = self.xp_bar_x + 60
        bar_y = self.xp_bar_y
        
        # Draw bar background (dark)
        bar_bg_rect = pygame.Rect(bar_x, bar_y, self.xp_bar_width, self.xp_bar_height)
        pygame.draw.rect(screen, (40, 30, 20), bar_bg_rect, border_radius=5)
        pygame.draw.rect(screen, (80, 60, 40), bar_bg_rect, 2, border_radius=5)
        
        # Draw XP fill
        # Clamp percentage to valid range [0, 100]
        clamped_percentage = max(0.0, min(100.0, self.xp_percentage))
        fill_width = int((clamped_percentage / 100) * self.xp_bar_width)
        if fill_width > 0:
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, self.xp_bar_height)
            # Gradient color from green to yellow based on progress
            progress = clamped_percentage / 100
            r = int(50 + 205 * progress)  # 50 -> 255
            g = int(200 - 50 * progress)  # 200 -> 150
            b = int(50)
            pygame.draw.rect(screen, (r, g, b), fill_rect, border_radius=5)
        
        # Draw XP text (centered in bar)
        xp_text = f"{self.player_xp}/{self.xp_to_next} XP"
        xp_surface = self.small_font.render(xp_text, True, WHITE)
        xp_rect = xp_surface.get_rect(center=(bar_x + self.xp_bar_width // 2, bar_y + self.xp_bar_height // 2))
        screen.blit(xp_surface, xp_rect)
    
    def _draw_xp_messages(self, screen: pygame.Surface):
        """Draw XP notification messages and temp messages in top right of grid"""
        # Draw XP messages (green theme)
        for msg in self.xp_messages:
            alpha = msg.get_alpha()
            
            msg_surface = pygame.Surface((self.message_box_width, 24), pygame.SRCALPHA)
            bg_color = (20, 40, 20, int(alpha * 0.95))
            border_color = (120, 220, 120, alpha)
            
            pygame.draw.rect(msg_surface, bg_color, (0, 0, self.message_box_width, 24), border_radius=4)
            pygame.draw.rect(msg_surface, border_color, (0, 0, self.message_box_width, 24), 2, border_radius=4)
            
            text_surface = self.message_font.render(msg.display_text, True, (255, 255, 255))
            text_alpha = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
            text_alpha.fill((255, 255, 255, alpha))
            text_surface.blit(text_alpha, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            msg_surface.blit(text_surface, (8, 3))
            screen.blit(msg_surface, (msg.x, msg.y))
        
        # Draw temp messages (yellow/warning theme)
        for msg in self.temp_messages:
            alpha = msg.get_alpha()
            
            msg_surface = pygame.Surface((self.message_box_width, 24), pygame.SRCALPHA)
            bg_color = (50, 40, 10, int(alpha * 0.95))  # Dark yellow-brown background
            border_color = (255, 215, 0, alpha)  # Gold border
            
            pygame.draw.rect(msg_surface, bg_color, (0, 0, self.message_box_width, 24), border_radius=4)
            pygame.draw.rect(msg_surface, border_color, (0, 0, self.message_box_width, 24), 2, border_radius=4)
            
            text_surface = self.message_font.render(msg.text, True, msg.color)
            text_alpha = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
            text_alpha.fill((*msg.color, alpha))
            text_surface.blit(text_alpha, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            msg_surface.blit(text_surface, (8, 3))
            screen.blit(msg_surface, (msg.x, msg.y))
    
    def draw(self, screen: pygame.Surface):
        """Draw the game UI"""
        # Draw top bar background
        top_bar = pygame.Rect(0, 0, SCREEN_WIDTH, GRID_OFFSET_Y - 10)
        pygame.draw.rect(screen, (50, 30, 20), top_bar)  # Dark brown
        pygame.draw.rect(screen, (139, 69, 19), top_bar, 3)  # Brown border
        
        # Draw username (top-left)
        username_surface = self.font.render(self.username, True, YELLOW)
        username_rect = username_surface.get_rect(topleft=(20, 20))
        screen.blit(username_surface, username_rect)
        
        # Draw weather display (top-left, next to username)
        weather_surface = self.font.render(self.weather_text, True, WHITE)
        weather_rect = weather_surface.get_rect(topleft=(20, 50))
        screen.blit(weather_surface, weather_rect)
        
        # Draw XP/Level bar
        self._draw_xp_bar(screen)
        
        # Draw money display (center of navbar, below title)
        self._draw_money_display(screen)
        
        # Draw health bar if in dark side
        if self.show_health_bar:
            self._draw_health_bar(screen)
        
        # Draw selected cell info (top-right, moved down to avoid overlap)
        if self.selected_cell_text:
            col, row = self.selected_cell_text
            cell_text = f"Grid ({col}, {row})"
            cell_surface = self.font.render(cell_text, True, WHITE)
            cell_rect = cell_surface.get_rect(topright=(SCREEN_WIDTH - 20, 55))
            screen.blit(cell_surface, cell_rect)
        
        # Draw game title (centered)
        title_surface = self.title_font.render("Farm Life", True, YELLOW)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 25))
        screen.blit(title_surface, title_rect)
        
        # Draw tasks/save/menu buttons
        self.tasks_button.draw(screen, self.button_font)
        self.save_button.draw(screen, self.button_font)
        self.menu_button.draw(screen, self.button_font)
        
        # Draw XP notification messages
        self._draw_xp_messages(screen)
    
    def _draw_money_display(self, screen: pygame.Surface):
        """Draw the money display in the center of the navbar"""
        # Position below the title
        money_x = SCREEN_WIDTH // 2
        money_y = 55
        
        # Draw coin icon (gold circle)
        coin_radius = 10
        pygame.draw.circle(screen, (255, 215, 0), (money_x - 50, money_y), coin_radius)  # Gold fill
        pygame.draw.circle(screen, (218, 165, 32), (money_x - 50, money_y), coin_radius, 2)  # Gold border
        
        # Draw money amount
        money_text = f"{self.player_money}"
        money_surface = self.money_font.render(money_text, True, YELLOW)
        money_rect = money_surface.get_rect(midleft=(money_x - 35, money_y))
        screen.blit(money_surface, money_rect)

    def _draw_health_bar(self, screen: pygame.Surface):
        """Draw the health bar in the center area"""
        # Draw bar background
        bar_rect = pygame.Rect(self.health_bar_x, self.health_bar_y, self.health_bar_width, self.health_bar_height)
        pygame.draw.rect(screen, HEALTH_BG, bar_rect, border_radius=5)
        pygame.draw.rect(screen, (100, 50, 50), bar_rect, 2, border_radius=5)
        
        # Draw health fill
        health_ratio = self.player_health / self.player_max_health
        fill_width = int(self.health_bar_width * health_ratio)
        if fill_width > 0:
            fill_rect = pygame.Rect(self.health_bar_x, self.health_bar_y, fill_width, self.health_bar_height)
            pygame.draw.rect(screen, HEALTH_RED, fill_rect, border_radius=5)
            
        # Draw health text
        health_text = f"HP: {self.player_health}/{self.player_max_health}"
        text_surf = self.small_font.render(health_text, True, WHITE)
        text_rect = text_surf.get_rect(center=bar_rect.center)
        screen.blit(text_surf, text_rect)