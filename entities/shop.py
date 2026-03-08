"""
Shop Entity - A shop building where players can buy/sell items
"""
import pygame
from typing import Tuple
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    GRID_SIZE, GRID_OFFSET_X, GRID_OFFSET_Y, GRID_COLS
)


class Shop:
    """A shop building for buying and selling items"""
    
    def __init__(self, grid_col: int, grid_row: int, grid_offset_x: int, grid_offset_y: int):
        # Grid position
        self.grid_col = grid_col
        self.grid_row = grid_row
        
        # Shop dimensions (in grid cells) - BIGGER: 4 cells wide, 3 cells tall
        self.cells_wide = 4
        self.cells_tall = 3
        self.width = GRID_SIZE * self.cells_wide
        self.height = GRID_SIZE * self.cells_tall
        
        # Calculate pixel position (top-right corner aligned)
        # Position at the right edge of the grid
        self.x = grid_offset_x + (grid_col + self.cells_wide // 2) * GRID_SIZE
        self.y = grid_offset_y + (grid_row + self.cells_tall // 2) * GRID_SIZE
        
        # Collision rect (the base of the shop)
        self.collision_rect = pygame.Rect(
            grid_offset_x + grid_col * GRID_SIZE,
            grid_offset_y + grid_row * GRID_SIZE,
            self.width,
            self.height
        )
        
        # Shop is not interactive yet
        self.is_interactive = False
    
    @property
    def sort_y(self) -> int:
        """Y position for depth sorting (bottom of shop)"""
        return self.y + self.height // 2
    
    def get_collision_rect(self) -> pygame.Rect:
        """Get collision rectangle"""
        return self.collision_rect
    
    def collides_with(self, rect: pygame.Rect) -> bool:
        """Check if rectangle collides with shop"""
        return self.collision_rect.colliderect(rect)
    
    def draw(self, screen: pygame.Surface):
        """Draw the shop building"""
        # Calculate positions
        left_x = self.x - self.width // 2
        right_x = self.x + self.width // 2
        base_y = self.y + self.height // 2
        wall_height = 60  # Increased from 40
        roof_height = 40  # Increased from 25
        
        # === SHADOW ===
        shadow_points = [
            (left_x - 8, base_y),
            (right_x + 8, base_y),
            (right_x + 15, base_y + 12),
            (left_x, base_y + 12)
        ]
        pygame.draw.polygon(screen, (30, 30, 30), shadow_points)
        
        # === WALLS ===
        wall_rect = pygame.Rect(left_x, base_y - wall_height, self.width, wall_height)
        # Wall shadow
        pygame.draw.rect(screen, (180, 140, 100), wall_rect)
        # Main wall (lighter wood/plank look)
        pygame.draw.rect(screen, (200, 160, 120), wall_rect)
        # Wall planks
        for i in range(0, self.width, 25):
            pygame.draw.line(screen, (170, 130, 90),
                           (left_x + i, base_y - wall_height),
                           (left_x + i, base_y), 2)
        # Wall border
        pygame.draw.rect(screen, (140, 100, 60), wall_rect, 3)
        
        # === ROOF ===
        roof_top_y = base_y - wall_height - roof_height
        roof_points = [
            (left_x - 15, base_y - wall_height),
            (self.x, roof_top_y),
            (right_x + 15, base_y - wall_height)
        ]
        pygame.draw.polygon(screen, (139, 69, 19), roof_points)  # Brown roof
        pygame.draw.polygon(screen, (100, 50, 20), roof_points, 3)  # Roof border
        
        # Roof tiles (horizontal lines)
        for i in range(1, 5):
            y_offset = roof_height * i // 5
            width_at_y = self.width + 30 - (y_offset * 2)
            pygame.draw.line(screen, (100, 50, 20),
                           (self.x - width_at_y // 2, base_y - wall_height - y_offset),
                           (self.x + width_at_y // 2, base_y - wall_height - y_offset), 2)
        
        # === DOOR ===
        door_width = 36  # Increased from 24
        door_height = 50  # Increased from 35
        door_x = self.x - door_width // 2
        door_y = base_y - door_height
        
        # Door frame
        pygame.draw.rect(screen, (80, 50, 30),
                        (door_x - 4, door_y - 4, door_width + 8, door_height + 4), 4)
        # Door
        pygame.draw.rect(screen, (60, 40, 25),
                        (door_x, door_y, door_width, door_height))
        # Door panels
        pygame.draw.rect(screen, (50, 30, 20),
                        (door_x + 5, door_y + 8, door_width - 10, door_height // 2 - 8), 2)
        pygame.draw.rect(screen, (50, 30, 20),
                        (door_x + 5, door_y + door_height // 2 + 5, door_width - 10, door_height // 2 - 10), 2)
        # Door handle
        pygame.draw.circle(screen, (200, 150, 50),
                          (door_x + door_width - 8, door_y + door_height // 2), 4)
        
        # === SIGN ===
        sign_width = 70  # Increased from 50
        sign_height = 24  # Increased from 18
        sign_x = self.x - sign_width // 2
        sign_y = base_y - wall_height - 8
        
        # Sign background
        pygame.draw.rect(screen, (139, 90, 43), (sign_x, sign_y, sign_width, sign_height))
        pygame.draw.rect(screen, (100, 60, 30), (sign_x, sign_y, sign_width, sign_height), 2)
        
        # Sign text "SHOP"
        font = pygame.font.SysFont('Arial', 14, bold=True)
        text_surface = font.render("SHOP", True, (255, 220, 150))
        text_rect = text_surface.get_rect(center=(self.x, sign_y + sign_height // 2))
        screen.blit(text_surface, text_rect)
        
        # Sign posts
        pygame.draw.line(screen, (100, 60, 30),
                        (sign_x + 8, sign_y),
                        (sign_x + 8, sign_y - 12), 3)
        pygame.draw.line(screen, (100, 60, 30),
                        (sign_x + sign_width - 8, sign_y),
                        (sign_x + sign_width - 8, sign_y - 12), 3)
        
        # === WINDOWS ===
        window_width = 28  # Increased from 20
        window_height = 28  # Increased from 20
        
        # Left window
        window_x1 = left_x + 20
        window_y = base_y - wall_height + 15
        
        # Window 1 frame
        pygame.draw.rect(screen, (80, 50, 30),
                        (window_x1 - 3, window_y - 3, window_width + 6, window_height + 6))
        # Window 1 glass
        pygame.draw.rect(screen, (150, 200, 255),
                        (window_x1, window_y, window_width, window_height))
        # Window 1 cross
        pygame.draw.line(screen, (80, 50, 30),
                        (window_x1 + window_width // 2, window_y),
                        (window_x1 + window_width // 2, window_y + window_height), 2)
        pygame.draw.line(screen, (80, 50, 30),
                        (window_x1, window_y + window_height // 2),
                        (window_x1 + window_width, window_y + window_height // 2), 2)
        
        # Right window
        window_x2 = right_x - 20 - window_width
        
        # Window 2 frame
        pygame.draw.rect(screen, (80, 50, 30),
                        (window_x2 - 3, window_y - 3, window_width + 6, window_height + 6))
        # Window 2 glass
        pygame.draw.rect(screen, (150, 200, 255),
                        (window_x2, window_y, window_width, window_height))
        # Window 2 cross
        pygame.draw.line(screen, (80, 50, 30),
                        (window_x2 + window_width // 2, window_y),
                        (window_x2 + window_width // 2, window_y + window_height), 2)
        pygame.draw.line(screen, (80, 50, 30),
                        (window_x2, window_y + window_height // 2),
                        (window_x2 + window_width, window_y + window_height // 2), 2)
        
        # === AWNING ===
        awning_y = base_y - wall_height
        awning_width = self.width + 20
        awning_height = 15  # Increased from 10
        
        # Striped awning
        stripe_width = 12
        for i in range(0, awning_width, stripe_width * 2):
            # Red stripe
            pygame.draw.rect(screen, (180, 50, 50),
                           (left_x - 10 + i, awning_y - awning_height, stripe_width, awning_height))
            # White stripe
            if i + stripe_width < awning_width:
                pygame.draw.rect(screen, (240, 230, 200),
                               (left_x - 10 + i + stripe_width, awning_y - awning_height, stripe_width, awning_height))
        # Awning border
        pygame.draw.rect(screen, (100, 30, 30),
                        (left_x - 10, awning_y - awning_height, awning_width, awning_height), 2)
