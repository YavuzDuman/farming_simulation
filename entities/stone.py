"""
Stone Entity - Mineable stone with hammer mechanics
"""
import pygame
import math
from typing import Tuple, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    GRID_SIZE, GRID_OFFSET_X, GRID_OFFSET_Y
)


class Stone:
    """A mineable stone that can be smashed with a hammer"""
    
    def __init__(self, grid_col: int, grid_row: int, size: str = "medium"):
        self.grid_col = grid_col
        self.grid_row = grid_row
        
        # Calculate pixel position (center of grid cell)
        self.x = GRID_OFFSET_X + grid_col * GRID_SIZE + GRID_SIZE // 2
        self.y = GRID_OFFSET_Y + grid_row * GRID_SIZE + GRID_SIZE // 2
        
        self.size = size
        self.is_alive = True
        
        # Stone drop
        self.stone_dropped = False
        self.stone_x = self.x
        self.stone_y = self.y
        
        # Set dimensions based on size
        if size == "small":
            self.width = 20
            self.height = 16
            self.max_hits = 3
            self.stone_quantity = 2
        elif size == "large":
            self.width = 40
            self.height = 32
            self.max_hits = 8
            self.stone_quantity = 8
        else:  # medium
            self.width = 28
            self.height = 22
            self.max_hits = 5
            self.stone_quantity = 4
        
        # Mining mechanics
        self.current_hits = 0
        self.shake_offset = 0
        self.shake_timer = 0
        
        # Collision rect
        self.collision_rect = pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )
        
        # Render rect (slightly larger for shadow)
        self.render_rect = pygame.Rect(
            self.x - self.width // 2 - 5,
            self.y - self.height // 2 - 5,
            self.width + 10,
            self.height + 10
        )
    
    @property
    def sort_y(self) -> int:
        """Y position for depth sorting (bottom of stone)"""
        return self.y + self.height // 2
    
    def get_collision_rect(self) -> pygame.Rect:
        """Get the collision rectangle"""
        return self.collision_rect
    
    def collides_with(self, rect: pygame.Rect) -> bool:
        """Check if a rectangle collides with the stone"""
        if not self.is_alive:
            return False
        return self.collision_rect.colliderect(rect)
    
    def smash(self) -> bool:
        """
        Smash the stone with hammer. Returns True if stone breaks.
        """
        if not self.is_alive:
            return False
        
        self.current_hits += 1
        
        # Start shake animation
        self.shake_timer = 10
        
        # Check if stone should break
        if self.current_hits >= self.max_hits:
            self.break_stone()
            return True
        
        return False
    
    def break_stone(self):
        """Stone breaks and drops stone items"""
        self.is_alive = False
        self.stone_dropped = True
        self.stone_x = self.x
        self.stone_y = self.y
    
    def get_stone_rect(self) -> Optional[pygame.Rect]:
        """Get the rect for stone pickup"""
        if not self.stone_dropped:
            return None
        return pygame.Rect(self.stone_x - 15, self.stone_y - 10, 30, 20)
    
    def check_stone_hover(self, mouse_pos: tuple[int, int]) -> bool:
        """Check if mouse is hovering over dropped stones"""
        if not self.stone_dropped:
            return False
        stone_rect = self.get_stone_rect()
        return stone_rect.collidepoint(mouse_pos) if stone_rect else False
    
    def collect_stone(self) -> int:
        """Collect the dropped stones. Returns quantity collected."""
        if not self.stone_dropped:
            return 0
        self.stone_dropped = False
        return self.stone_quantity
    
    def update(self):
        """Update stone animations"""
        if self.shake_timer > 0:
            self.shake_timer -= 1
            # Shake back and forth
            self.shake_offset = int(math.sin(self.shake_timer * 0.5) * 2)
        else:
            self.shake_offset = 0
    
    def draw(self, screen: pygame.Surface):
        """Draw the stone or stone drops"""
        if self.is_alive:
            self._draw_stone(screen)
        elif self.stone_dropped:
            self._draw_stone_items(screen)
    
    def _draw_stone(self, screen: pygame.Surface):
        """Draw the living stone"""
        draw_x = self.x + self.shake_offset
        
        # Shadow
        pygame.draw.ellipse(screen, (30, 30, 30),
                           (draw_x - self.width // 2 - 2, self.y + self.height // 2 - 4,
                            self.width + 4, 8))
        
        # Main stone body (irregular shape)
        if self.size == "small":
            # Small round stone
            pygame.draw.ellipse(screen, (120, 120, 125),
                               (draw_x - self.width // 2, self.y - self.height // 2,
                                self.width, self.height))
            # Highlight
            pygame.draw.ellipse(screen, (150, 150, 155),
                               (draw_x - self.width // 2 + 3, self.y - self.height // 2 + 2,
                                self.width // 2, self.height // 3))
        elif self.size == "large":
            # Large boulder (multiple layers)
            # Base
            pygame.draw.ellipse(screen, (90, 90, 95),
                               (draw_x - self.width // 2 - 2, self.y - self.height // 2 + 5,
                                self.width + 4, self.height))
            # Middle layer
            pygame.draw.ellipse(screen, (110, 110, 115),
                               (draw_x - self.width // 2 + 3, self.y - self.height // 2,
                                self.width - 6, self.height - 4))
            # Top highlight
            pygame.draw.ellipse(screen, (140, 140, 145),
                               (draw_x - self.width // 3, self.y - self.height // 2 + 2,
                                self.width // 2, self.height // 3))
            # Cracks
            pygame.draw.line(screen, (70, 70, 75),
                           (draw_x - 8, self.y - 5), (draw_x + 2, self.y + 8), 2)
            pygame.draw.line(screen, (70, 70, 75),
                           (draw_x + 5, self.y - 8), (draw_x + 12, self.y + 5), 2)
        else:
            # Medium stone
            pygame.draw.ellipse(screen, (100, 100, 105),
                               (draw_x - self.width // 2 - 1, self.y - self.height // 2 + 3,
                                self.width + 2, self.height - 2))
            pygame.draw.ellipse(screen, (120, 120, 125),
                               (draw_x - self.width // 2 + 2, self.y - self.height // 2,
                                self.width - 4, self.height - 4))
            # Highlight
            pygame.draw.ellipse(screen, (150, 150, 155),
                               (draw_x - self.width // 3, self.y - self.height // 2 + 2,
                                self.width // 2, self.height // 3))
            # Small crack
            pygame.draw.line(screen, (80, 80, 85),
                           (draw_x - 5, self.y), (draw_x + 3, self.y + 5), 1)
        
        # Draw hit indicator
        if self.current_hits > 0:
            hit_text = f"{self.current_hits}/{self.max_hits}"
            font = pygame.font.SysFont('Arial', 12, bold=True)
            text_surface = font.render(hit_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(draw_x, self.y - self.height // 2 - 8))
            # Background for text
            pygame.draw.rect(screen, (0, 0, 0), text_rect.inflate(4, 2))
            screen.blit(text_surface, text_rect)
    
    def _draw_stone_items(self, screen: pygame.Surface):
        """Draw dropped stone items"""
        # Draw multiple small stones
        for i in range(min(4, self.stone_quantity)):
            offset_x = ((i % 2) - 0.5) * 15
            offset_y = (i // 2) * 10
            
            stone_x = self.stone_x + offset_x
            stone_y = self.stone_y + offset_y
            
            # Shadow
            pygame.draw.ellipse(screen, (30, 30, 30),
                               (stone_x - 6, stone_y + 4, 12, 4))
            
            # Small stone
            pygame.draw.ellipse(screen, (130, 130, 135),
                               (stone_x - 6, stone_y - 4, 12, 8))
            pygame.draw.ellipse(screen, (160, 160, 165),
                               (stone_x - 4, stone_y - 3, 6, 4))
        
        # Quantity label
        font = pygame.font.SysFont('Arial', 14, bold=True)
        qty_text = font.render(f"x{self.stone_quantity}", True, (255, 255, 255))
        screen.blit(qty_text, (self.stone_x + 15, self.stone_y - 15))
        
        # Hover hint
        font_small = pygame.font.SysFont('Arial', 10)
        hint_text = font_small.render("Hover to collect", True, (200, 200, 200))
        hint_rect = hint_text.get_rect(center=(self.stone_x, self.stone_y + 20))
        screen.blit(hint_text, hint_rect)
