"""
Chest Entity - Grid-sized treasure chest
"""
import pygame
from typing import Tuple
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CHEST_WOOD, CHEST_GOLD, GRID_SIZE


class Chest:
    """A wooden chest that fills one grid cell"""
    
    def __init__(self, grid_col: int, grid_row: int, grid_offset_x: int, grid_offset_y: int):
        # Position at center of grid cell
        self.grid_col = grid_col
        self.grid_row = grid_row
        
        # Calculate pixel position (center of grid cell)
        self.x = grid_offset_x + grid_col * GRID_SIZE + GRID_SIZE // 2
        self.y = grid_offset_y + grid_row * GRID_SIZE + GRID_SIZE // 2
        
        # Chest fills the grid cell
        self.width = GRID_SIZE - 4  # Slightly smaller than grid for border
        self.height = GRID_SIZE - 4
        
        # Collision rect (full grid cell)
        self.collision_rect = pygame.Rect(
            grid_offset_x + grid_col * GRID_SIZE,
            grid_offset_y + grid_row * GRID_SIZE,
            GRID_SIZE,
            GRID_SIZE
        )
        
        # Render rect
        self.render_rect = pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )
    
    @property
    def sort_y(self) -> int:
        """Y position for depth sorting (bottom of chest)"""
        return self.y + self.height // 2
    
    def get_collision_rect(self) -> pygame.Rect:
        """Get collision rectangle"""
        return self.collision_rect
    
    def collides_with(self, rect: pygame.Rect) -> bool:
        """Check if rectangle collides with chest"""
        return self.collision_rect.colliderect(rect)
    
    def draw(self, screen: pygame.Surface):
        """Draw the chest filling one grid cell"""
        left_x = self.x - self.width // 2
        top_y = self.y - self.height // 2
        bottom_y = self.y + self.height // 2
        
        # Shadow under chest
        pygame.draw.ellipse(screen, (30, 30, 30), 
                           (left_x + 2, bottom_y - 6, self.width - 4, 8))
        
        # === CHEST BODY (3D effect) ===
        body_height = int(self.height * 0.5)
        body_top = bottom_y - body_height
        
        # Body shadow (right side - 3D depth)
        body_shadow_rect = pygame.Rect(left_x + 3, body_top + 3, self.width, body_height)
        pygame.draw.rect(screen, (90, 45, 20), body_shadow_rect, border_radius=3)
        
        # Main body
        body_rect = pygame.Rect(left_x, body_top, self.width, body_height)
        pygame.draw.rect(screen, CHEST_WOOD, body_rect, border_radius=3)
        
        # Wood plank lines on body
        plank_spacing = self.width // 4
        for i in range(1, 4):
            pygame.draw.line(screen, (120, 60, 30),
                           (left_x + i * plank_spacing, body_top + 3),
                           (left_x + i * plank_spacing, bottom_y - 3), 2)
        
        # Horizontal band
        pygame.draw.rect(screen, (140, 70, 35),
                        (left_x, body_top + body_height // 2 - 3, self.width, 6))
        
        # === CHEST LID (curved, 3D) ===
        lid_height = int(self.height * 0.35)
        lid_top = body_top - lid_height
        
        # Lid shadow
        pygame.draw.ellipse(screen, (90, 45, 20),
                           (left_x + 3, lid_top + 3, self.width, lid_height + 4))
        
        # Lid base
        pygame.draw.ellipse(screen, CHEST_WOOD,
                           (left_x, lid_top, self.width, lid_height + 4))
        
        # Lid highlight (3D effect)
        pygame.draw.ellipse(screen, (180, 100, 50),
                           (left_x + 4, lid_top + 2, self.width - 8, lid_height - 2))
        
        # Lid border
        pygame.draw.ellipse(screen, (100, 50, 25),
                           (left_x, lid_top, self.width, lid_height + 4), 2)
        
        # === GOLD BANDS ===
        band_width = 6
        # Left band
        pygame.draw.rect(screen, CHEST_GOLD,
                        (left_x + 3, lid_top, band_width, body_height + lid_height))
        pygame.draw.rect(screen, (200, 170, 50),
                        (left_x + 4, lid_top + 2, 2, body_height + lid_height - 4))
        
        # Right band
        pygame.draw.rect(screen, CHEST_GOLD,
                        (left_x + self.width - 3 - band_width, lid_top, band_width, body_height + lid_height))
        pygame.draw.rect(screen, (200, 170, 50),
                        (left_x + self.width - 3 - band_width + 1, lid_top + 2, 2, body_height + lid_height - 4))
        
        # === LOCK ===
        lock_width = 16
        lock_height = 20
        lock_x = self.x - lock_width // 2
        lock_y = body_top - 4
        
        # Lock plate
        pygame.draw.rect(screen, CHEST_GOLD,
                        (lock_x, lock_y, lock_width, lock_height),
                        border_radius=3)
        
        # Lock highlight
        pygame.draw.rect(screen, (220, 190, 80),
                        (lock_x + 2, lock_y + 2, lock_width - 4, lock_height - 4),
                        border_radius=2)
        
        # Lock border
        pygame.draw.rect(screen, (180, 140, 0),
                        (lock_x, lock_y, lock_width, lock_height), 2,
                        border_radius=3)
        
        # Keyhole
        keyhole_x = self.x
        keyhole_y = lock_y + lock_height // 2
        pygame.draw.circle(screen, (40, 30, 10), (keyhole_x, keyhole_y - 3), 4)
        pygame.draw.rect(screen, (40, 30, 10),
                        (keyhole_x - 2, keyhole_y - 2, 4, 8))
        
        # === CORNER BRACKETS ===
        bracket_size = 8
        bracket_color = (180, 140, 0)
        
        # Top-left
        pygame.draw.polygon(screen, bracket_color, [
            (left_x, body_top),
            (left_x + bracket_size, body_top),
            (left_x, body_top + bracket_size)
        ])
        # Top-right
        pygame.draw.polygon(screen, bracket_color, [
            (left_x + self.width, body_top),
            (left_x + self.width - bracket_size, body_top),
            (left_x + self.width, body_top + bracket_size)
        ])
        # Bottom-left
        pygame.draw.polygon(screen, bracket_color, [
            (left_x, bottom_y),
            (left_x + bracket_size, bottom_y),
            (left_x, bottom_y - bracket_size)
        ])
        # Bottom-right
        pygame.draw.polygon(screen, bracket_color, [
            (left_x + self.width, bottom_y),
            (left_x + self.width - bracket_size, bottom_y),
            (left_x + self.width, bottom_y - bracket_size)
        ])