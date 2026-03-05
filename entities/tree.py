"""
Tree Entity - Realistic tree with chopping mechanics
"""
import pygame
import math
from typing import Tuple, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    TREE_TRUNK, TREE_LEAVES_DARK, TREE_LEAVES_MEDIUM, TREE_LEAVES_LIGHT,
    GRID_SIZE, GRID_OFFSET_X, GRID_OFFSET_Y
)


class Tree:
    """A realistic tree that can be chopped down"""
    
    def __init__(self, x: int, y: int, size: str = "medium"):
        self.x = x
        self.y = y
        self.size = size
        self.is_alive = True
        
        # Wood drop
        self.wood_dropped = False
        self.wood_x = x
        self.wood_y = y
        
        # Set dimensions based on size
        if size == "small":
            self.trunk_width = 12
            self.trunk_height = 30
            self.leaves_radius = 25
            self.max_hits = 5
            self.wood_quantity = 5
        elif size == "large":
            self.trunk_width = 20
            self.trunk_height = 50
            self.leaves_radius = 45
            self.max_hits = 15
            self.wood_quantity = 20
        else:  # medium
            self.trunk_width = 16
            self.trunk_height = 40
            self.leaves_radius = 35
            self.max_hits = 10
            self.wood_quantity = 10
        
        # Chopping mechanics
        self.current_hits = 0
        self.shake_offset = 0
        self.shake_timer = 0
        
        # Collision rect (trunk only - player can't walk through trunk)
        self.collision_rect = pygame.Rect(
            x - self.trunk_width // 2,
            y - self.trunk_height // 4,
            self.trunk_width,
            self.trunk_height // 2
        )
        
        # Full rect for rendering (includes leaves)
        self.render_rect = pygame.Rect(
            x - self.leaves_radius,
            y - self.trunk_height - self.leaves_radius,
            self.leaves_radius * 2,
            self.trunk_height + self.leaves_radius * 2
        )
        
        # Grid cell for wood drop
        self.grid_col = (x - GRID_OFFSET_X) // GRID_SIZE
        self.grid_row = (y - GRID_OFFSET_Y) // GRID_SIZE
    
    @property
    def sort_y(self) -> int:
        """Y position for depth sorting (bottom of trunk)"""
        return self.y + self.trunk_height // 4
    
    def get_collision_rect(self) -> pygame.Rect:
        """Get the collision rectangle (trunk area)"""
        return self.collision_rect
    
    def collides_with(self, rect: pygame.Rect) -> bool:
        """Check if a rectangle collides with the tree trunk"""
        if not self.is_alive:
            return False
        return self.collision_rect.colliderect(rect)
    
    def is_behind_tree(self, entity_y: int) -> bool:
        """Check if an entity at given Y is behind (under) the tree"""
        if not self.is_alive:
            return False
        return entity_y < self.sort_y
    
    def chop(self) -> bool:
        """
        Chop the tree. Returns True if tree falls.
        """
        if not self.is_alive:
            return False
        
        self.current_hits += 1
        
        # Start shake animation
        self.shake_timer = 10
        
        # Check if tree should fall
        if self.current_hits >= self.max_hits:
            self.fall()
            return True
        
        return False
    
    def fall(self):
        """Tree falls and drops wood"""
        self.is_alive = False
        self.wood_dropped = True
        # Wood is dropped at tree location
        self.wood_x = self.x
        self.wood_y = self.y
    
    def get_wood_rect(self) -> Optional[pygame.Rect]:
        """Get the rect for wood pickup"""
        if not self.wood_dropped:
            return None
        return pygame.Rect(self.wood_x - 15, self.wood_y - 10, 30, 20)
    
    def check_wood_hover(self, mouse_pos: tuple[int, int]) -> bool:
        """Check if mouse is hovering over dropped wood"""
        if not self.wood_dropped:
            return False
        wood_rect = self.get_wood_rect()
        return wood_rect.collidepoint(mouse_pos) if wood_rect else False
    
    def collect_wood(self) -> int:
        """Collect the dropped wood. Returns quantity collected."""
        if not self.wood_dropped:
            return 0
        self.wood_dropped = False
        return self.wood_quantity
    
    def update(self):
        """Update tree animations"""
        if self.shake_timer > 0:
            self.shake_timer -= 1
            # Shake back and forth
            self.shake_offset = int(math.sin(self.shake_timer * 0.5) * 3)
        else:
            self.shake_offset = 0
    
    def draw(self, screen: pygame.Surface, alpha: int = 255):
        """Draw the tree or wood drops"""
        if self.is_alive:
            self._draw_tree(screen)
        elif self.wood_dropped:
            self._draw_wood(screen)
    
    def _draw_tree(self, screen: pygame.Surface):
        """Draw the living tree"""
        # Apply shake offset
        draw_x = self.x + self.shake_offset
        
        # Draw trunk
        trunk_rect = pygame.Rect(
            draw_x - self.trunk_width // 2,
            self.y - self.trunk_height,
            self.trunk_width,
            self.trunk_height
        )
        
        # Trunk shadow/depth
        pygame.draw.ellipse(screen, (60, 40, 20), 
                           (draw_x - self.trunk_width // 2 - 2, 
                            self.y - 5, 
                            self.trunk_width + 4, 8))
        
        # Main trunk
        pygame.draw.rect(screen, TREE_TRUNK, trunk_rect)
        
        # Trunk texture (vertical lines)
        for i in range(2, self.trunk_width - 2, 4):
            pygame.draw.line(screen, (80, 50, 30),
                           (draw_x - self.trunk_width // 2 + i, self.y - self.trunk_height),
                           (draw_x - self.trunk_width // 2 + i, self.y), 1)
        
        # Draw leaves in layers (back to front)
        leaves_center_y = self.y - self.trunk_height + 5
        
        # Back layer (darker)
        pygame.draw.circle(screen, TREE_LEAVES_DARK,
                          (draw_x - 5, leaves_center_y + 5), 
                          int(self.leaves_radius * 0.9))
        pygame.draw.circle(screen, TREE_LEAVES_DARK,
                          (draw_x + 8, leaves_center_y + 8), 
                          int(self.leaves_radius * 0.85))
        
        # Middle layer (medium)
        pygame.draw.circle(screen, TREE_LEAVES_MEDIUM,
                          (draw_x, leaves_center_y), 
                          self.leaves_radius)
        pygame.draw.circle(screen, TREE_LEAVES_MEDIUM,
                          (draw_x - 10, leaves_center_y - 5), 
                          int(self.leaves_radius * 0.8))
        pygame.draw.circle(screen, TREE_LEAVES_MEDIUM,
                          (draw_x + 12, leaves_center_y - 3), 
                          int(self.leaves_radius * 0.75))
        
        # Front layer (lighter highlights)
        pygame.draw.circle(screen, TREE_LEAVES_LIGHT,
                          (draw_x - 5, leaves_center_y - 8), 
                          int(self.leaves_radius * 0.5))
        pygame.draw.circle(screen, TREE_LEAVES_LIGHT,
                          (draw_x + 6, leaves_center_y - 10), 
                          int(self.leaves_radius * 0.4))
        
        # Add some leaf details
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            leaf_x = draw_x + int(math.cos(rad) * self.leaves_radius * 0.6)
            leaf_y = leaves_center_y + int(math.sin(rad) * self.leaves_radius * 0.5)
            pygame.draw.circle(screen, TREE_LEAVES_LIGHT, (leaf_x, leaf_y), 4)
        
        # Draw hit indicator (chop count)
        if self.current_hits > 0:
            hit_text = f"{self.current_hits}/{self.max_hits}"
            font = pygame.font.SysFont('Arial', 12, bold=True)
            text_surface = font.render(hit_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(draw_x, self.y - self.trunk_height - 10))
            # Background for text
            pygame.draw.rect(screen, (0, 0, 0), text_rect.inflate(4, 2))
            screen.blit(text_surface, text_rect)
    
    def _draw_wood(self, screen: pygame.Surface):
        """Draw dropped wood logs"""
        # Draw multiple logs in a pile
        for i in range(min(5, self.wood_quantity)):
            offset_x = (i % 3 - 1) * 12
            offset_y = (i // 3) * 8
            
            log_x = self.wood_x + offset_x
            log_y = self.wood_y + offset_y
            
            # Shadow
            pygame.draw.ellipse(screen, (30, 30, 30), 
                               (log_x - 10, log_y + 6, 20, 6))
            
            # Log body
            pygame.draw.ellipse(screen, (139, 90, 43), 
                               (log_x - 10, log_y - 4, 20, 12))
            # End grain
            pygame.draw.ellipse(screen, (160, 110, 60), 
                               (log_x - 10, log_y - 6, 20, 5))
            # Grain lines
            pygame.draw.line(screen, (100, 65, 30), 
                           (log_x - 6, log_y - 2), (log_x - 6, log_y + 6), 1)
            pygame.draw.line(screen, (100, 65, 30), 
                           (log_x, log_y - 2), (log_x, log_y + 6), 1)
            pygame.draw.line(screen, (100, 65, 30), 
                           (log_x + 6, log_y - 2), (log_x + 6, log_y + 6), 1)
        
        # Quantity label
        font = pygame.font.SysFont('Arial', 14, bold=True)
        qty_text = font.render(f"x{self.wood_quantity}", True, (255, 255, 255))
        screen.blit(qty_text, (self.wood_x + 15, self.wood_y - 15))
        
        # Hover hint
        font_small = pygame.font.SysFont('Arial', 10)
        hint_text = font_small.render("Hover to collect", True, (200, 200, 200))
        hint_rect = hint_text.get_rect(center=(self.wood_x, self.wood_y + 20))
        screen.blit(hint_text, hint_rect)
    
    def draw_transparent(self, screen: pygame.Surface):
        """Draw tree with transparency (when player is behind)"""
        # Create a transparent surface
        temp_surface = pygame.Surface((self.render_rect.width, self.render_rect.height), pygame.SRCALPHA)
        
        # Draw tree on temp surface
        offset_x = self.leaves_radius
        offset_y = self.trunk_height + self.leaves_radius - self.trunk_height // 4
        
        # Draw trunk on temp surface
        trunk_rect = pygame.Rect(
            offset_x - self.trunk_width // 2,
            offset_y - self.trunk_height,
            self.trunk_width,
            self.trunk_height
        )
        pygame.draw.rect(temp_surface, (*TREE_TRUNK, 120), trunk_rect)
        
        # Draw leaves on temp surface with transparency
        leaves_center_y = offset_y - self.trunk_height + 5
        
        pygame.draw.circle(temp_surface, (*TREE_LEAVES_DARK, 100),
                          (offset_x - 5, leaves_center_y + 5), 
                          int(self.leaves_radius * 0.9))
        pygame.draw.circle(temp_surface, (*TREE_LEAVES_MEDIUM, 120),
                          (offset_x, leaves_center_y), 
                          self.leaves_radius)
        
        # Blit to screen
        screen.blit(temp_surface, (self.x - self.leaves_radius, 
                                   self.y - self.trunk_height - self.leaves_radius))