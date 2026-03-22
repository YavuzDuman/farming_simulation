"""
Dark Side Rock Obstacle - Rocks that block zombie movement
"""
import pygame
import random
import math
from typing import Tuple
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    GRID_SIZE, GRID_OFFSET_X, GRID_OFFSET_Y, DARK_SIDE_BORDER
)


class DarkRock:
    """A dark rock obstacle that zombies cannot pass through"""
    
    def __init__(self, grid_col: int, grid_row: int, size: str = "medium"):
        self.grid_col = grid_col
        self.grid_row = grid_row
        
        # Calculate pixel position (center of grid cell)
        self.x = GRID_OFFSET_X + grid_col * GRID_SIZE + GRID_SIZE // 2
        self.y = GRID_OFFSET_Y + grid_row * GRID_SIZE + GRID_SIZE // 2
        
        self.size = size
        self.is_alive = True  # Zombies only check this via collision_rect
        self.is_broken = False  # When smashed by player
        
        # Set dimensions based on size
        if size == "small":
            self.width = 24
            self.height = 20
            self.max_hits = 3
            self.gem_quantity = 1
        elif size == "large":
            self.width = 48
            self.height = 38
            self.max_hits = 8
            self.gem_quantity = 4
        else:  # medium
            self.width = 36
            self.height = 28
            self.max_hits = 5
            self.gem_quantity = 2
        
        self.current_hits = 0
        self.shake_offset = 0
        self.shake_timer = 0
        
        # Collision rect (zombies check this)
        self.collision_rect = pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )
        
        # Render rect
        self.render_rect = pygame.Rect(
            self.x - self.width // 2 - 5,
            self.y - self.height // 2 - 5,
            self.width + 10,
            self.height + 10
        )
        
        # Random appearance variation
        self.rock_seed = random.randint(0, 100)
        self.darkness = random.randint(-10, 10)
        
        # Gem drop tracking
        self.gem_dropped = False
        self.gem_x = self.x
        self.gem_y = self.y
    
    @property
    def sort_y(self) -> int:
        """Y position for depth sorting (bottom of rock)"""
        return self.y + self.height // 2
    
    def collides_with(self, rect: pygame.Rect) -> bool:
        """Check if a rectangle collides with this rock"""
        if not self.is_alive or self.is_broken:
            return False
        return self.collision_rect.colliderect(rect)
    
    def get_collision_rect(self) -> pygame.Rect:
        """Get the collision rectangle"""
        return self.collision_rect
    
    def smash(self) -> bool:
        """
        Smash the rock with hammer. Returns True if rock breaks.
        """
        if not self.is_alive or self.is_broken:
            return False
        
        self.current_hits += 1
        
        # Start shake animation
        self.shake_timer = 10
        
        # Check if rock should break
        if self.current_hits >= self.max_hits:
            self.break_rock()
            return True
        
        return False
    
    def break_rock(self):
        """Rock breaks and drops gems"""
        self.is_alive = False
        self.is_broken = True
        self.gem_dropped = True
        self.gem_x = self.x
        self.gem_y = self.y
        # Remove collision so zombies can pass
        self.collision_rect = None
    
    def get_gem_rect(self) -> pygame.Rect:
        """Get the rect for gem pickup"""
        if not self.gem_dropped:
            return None
        return pygame.Rect(self.gem_x - 12, self.gem_y - 12, 24, 24)
    
    def check_gem_hover(self, mouse_pos: tuple[int, int]) -> bool:
        """Check if mouse is hovering over dropped gems"""
        if not self.gem_dropped:
            return False
        gem_rect = self.get_gem_rect()
        return gem_rect.collidepoint(mouse_pos) if gem_rect else False
    
    def collect_gem(self) -> int:
        """Collect the dropped gems. Returns quantity collected."""
        if not self.gem_dropped:
            return 0
        self.gem_dropped = False
        return self.gem_quantity
    
    def update(self):
        """Update rock animations"""
        if self.shake_timer > 0:
            self.shake_timer -= 1
            # Shake back and forth
            self.shake_offset = int(math.sin(self.shake_timer * 0.5) * 2)
        else:
            self.shake_offset = 0
    
    def draw(self, screen: pygame.Surface):
        """Draw the dark rock obstacle or dropped gems"""
        if self.is_alive and not self.is_broken:
            self._draw_rock(screen)
        elif self.gem_dropped:
            self._draw_gems(screen)
    
    def _draw_rock(self, screen: pygame.Surface):
        """Draw the living rock"""
        draw_x = self.x + self.shake_offset
        
        # Dark rock colors (darker for dark side)
        base_dark = 25 + self.darkness
        base_medium = 40 + self.darkness
        base_light = 55 + self.darkness
        
        # Shadow
        pygame.draw.ellipse(screen, (10, 8, 12),
                           (draw_x - self.width // 2 - 2, self.y + self.height // 2 - 4,
                            self.width + 4, 8))
        
        # Main rock body (irregular, dark)
        if self.size == "small":
            pygame.draw.ellipse(screen, (base_medium, base_medium - 5, base_medium + 5),
                               (draw_x - self.width // 2, self.y - self.height // 2,
                                self.width, self.height))
            pygame.draw.ellipse(screen, (base_light, base_light - 5, base_light + 5),
                               (draw_x - self.width // 2 + 2, self.y - self.height // 2 + 2,
                                self.width // 2, self.height // 2))
        elif self.size == "large":
            # Large boulder with multiple layers
            pygame.draw.ellipse(screen, (base_dark, base_dark - 5, base_dark + 5),
                               (draw_x - self.width // 2 - 2, self.y - self.height // 2 + 5,
                                self.width + 4, self.height))
            pygame.draw.ellipse(screen, (base_medium, base_medium - 5, base_medium + 5),
                               (draw_x - self.width // 2 + 3, self.y - self.height // 2,
                                self.width - 6, self.height - 4))
            pygame.draw.ellipse(screen, (base_light, base_light - 5, base_light + 5),
                               (draw_x - self.width // 3, self.y - self.height // 2 + 3,
                                self.width // 2, self.height // 2))
            # Cracks
            pygame.draw.line(screen, (base_dark - 10, base_dark - 10, base_dark),
                           (draw_x - 10, self.y - 5), (draw_x + 5, self.y + 10), 2)
            pygame.draw.line(screen, (base_dark - 10, base_dark - 10, base_dark),
                           (draw_x + 8, self.y - 8), (draw_x + 15, self.y + 8), 2)
        else:
            # Medium rock
            pygame.draw.ellipse(screen, (base_dark, base_dark - 5, base_dark + 5),
                               (draw_x - self.width // 2 - 1, self.y - self.height // 2 + 3,
                                self.width + 2, self.height - 2))
            pygame.draw.ellipse(screen, (base_medium, base_medium - 5, base_medium + 5),
                               (draw_x - self.width // 2 + 2, self.y - self.height // 2,
                                self.width - 4, self.height - 4))
            pygame.draw.ellipse(screen, (base_light, base_light - 5, base_light + 5),
                               (draw_x - self.width // 3, self.y - self.height // 2 + 2,
                                self.width // 2, self.height // 2))
            # Small crack
            pygame.draw.line(screen, (base_dark - 10, base_dark - 10, base_dark),
                           (draw_x - 5, self.y), (draw_x + 5, self.y + 6), 1)
        
        # Draw hit indicator
        if self.current_hits > 0:
            hit_text = f"{self.current_hits}/{self.max_hits}"
            font = pygame.font.SysFont('Arial', 12, bold=True)
            text_surface = font.render(hit_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(draw_x, self.y - self.height // 2 - 8))
            # Background for text
            pygame.draw.rect(screen, (0, 0, 0), text_rect.inflate(4, 2))
            screen.blit(text_surface, text_rect)
    
    def _draw_gems(self, screen: pygame.Surface):
        """Draw dropped red gems"""
        # Bob animation
        bob_offset = math.sin(pygame.time.get_ticks() * 0.005) * 3
        
        # Draw multiple gems
        for i in range(min(4, self.gem_quantity)):
            offset_x = ((i % 2) - 0.5) * 15
            offset_y = (i // 2) * 10
            
            gem_x = self.gem_x + offset_x
            gem_y = self.gem_y + offset_y + bob_offset
            
            # Shadow
            pygame.draw.ellipse(screen, (30, 10, 10),
                               (gem_x - 6, gem_y + 6, 12, 4))
            
            # Red gem (ruby-like)
            pygame.draw.polygon(screen, (200, 30, 30),
                               [(gem_x, gem_y - 8), (gem_x + 6, gem_y), (gem_x, gem_y + 4), (gem_x - 6, gem_y)])
            pygame.draw.polygon(screen, (255, 80, 80),
                               [(gem_x, gem_y - 6), (gem_x + 4, gem_y), (gem_x, gem_y + 2), (gem_x - 4, gem_y)])
            
            # Shine
            pygame.draw.circle(screen, (255, 200, 200), (int(gem_x - 2), int(gem_y - 3)), 2)
        
        # Quantity label
        if self.gem_quantity > 1:
            font = pygame.font.SysFont('Arial', 14, bold=True)
            qty_text = font.render(f"x{self.gem_quantity}", True, (255, 255, 255))
            screen.blit(qty_text, (self.gem_x + 15, self.gem_y - 15))
        
        # Hover hint
        font_small = pygame.font.SysFont('Arial', 10)
        hint_text = font_small.render("Hover to collect", True, (200, 200, 200))
        hint_rect = hint_text.get_rect(center=(self.gem_x, self.gem_y + 25))
        screen.blit(hint_text, hint_rect)
