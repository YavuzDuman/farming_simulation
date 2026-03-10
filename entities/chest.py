"""
Chest Entity - Grid-sized treasure chest
"""
import pygame
from typing import Tuple, List, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CHEST_WOOD, CHEST_GOLD, GRID_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
from game.inventory import Item, ItemType


class Chest:
    """A wooden chest that fills one grid cell with internal inventory"""
    
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

        # Inventory (2x5 slots)
        self.slots: List[Optional[Item]] = [None] * 10
        self.slots[0] = Item(ItemType.SEED, 50)  # Wheat seeds
        self.slots[1] = Item(ItemType.CARROT_SEED, 30)  # Carrot seeds
        
        self.is_open = False
        self.inventory_rect = None
        self.slot_size = 48
        self.slot_spacing = 8
    
    def toggle_inventory(self):
        """Toggle the chest inventory display"""
        self.is_open = not self.is_open
    
    def close_inventory(self):
        """Close the chest inventory"""
        self.is_open = False
    
    def handle_click(self, mouse_pos: Tuple[int, int]) -> Optional[Item]:
        """Handle click on chest inventory slots. Returns item if clicked."""
        if not self.is_open or not self.inventory_rect:
            return None
        
        x, y = mouse_pos
        if not self.inventory_rect.collidepoint(x, y):
            # Clicked outside inventory, maybe close it?
            # For now, let GameManager handle closing if needed
            return None
            
        # Check each slot
        cols = 5
        rows = 2
        start_x = self.inventory_rect.x + 10
        start_y = self.inventory_rect.y + 35 # Leave space for title
        
        for row in range(rows):
            for col in range(cols):
                idx = row * cols + col
                slot_x = start_x + col * (self.slot_size + self.slot_spacing)
                slot_y = start_y + row * (self.slot_size + self.slot_spacing)
                slot_rect = pygame.Rect(slot_x, slot_y, self.slot_size, self.slot_size)
                
                if slot_rect.collidepoint(x, y):
                    item = self.slots[idx]
                    if item:
                        self.slots[idx] = None # Take the item
                        return item
        return None
    
    def handle_key(self, key: int) -> bool:
        """Handle key press. Returns True if key was handled (ESC closes chest)."""
        if self.is_open and key == pygame.K_ESCAPE:
            self.close_inventory()
            return True
        return False
    
    def is_click_outside_inventory(self, mouse_pos: Tuple[int, int]) -> bool:
        """Check if a click is outside the inventory panel (but not on chest itself)."""
        if not self.is_open or not self.inventory_rect:
            return False
        x, y = mouse_pos
        # Check if click is outside inventory rect
        if not self.inventory_rect.collidepoint(x, y):
            return True
        return False

    def draw_inventory(self, screen: pygame.Surface):
        """Draw the 2x5 chest inventory"""
        if not self.is_open:
            return
            
        cols = 5
        rows = 2
        inv_width = cols * self.slot_size + (cols + 1) * self.slot_spacing + 20
        inv_height = rows * self.slot_size + (rows + 1) * self.slot_spacing + 40
        
        # Center on screen
        inv_x = (SCREEN_WIDTH - inv_width) // 2
        inv_y = (SCREEN_HEIGHT - inv_height) // 2
        self.inventory_rect = pygame.Rect(inv_x, inv_y, inv_width, inv_height)
        
        # Draw background
        pygame.draw.rect(screen, (50, 40, 30), self.inventory_rect, border_radius=10)
        pygame.draw.rect(screen, (100, 80, 60), self.inventory_rect, 3, border_radius=10)
        
        # Title
        font = pygame.font.SysFont('Arial', 20, bold=True)
        title = font.render("Chest Inventory", True, (255, 255, 255))
        screen.blit(title, (inv_x + 15, inv_y + 10))
        
        # Close help
        small_font = pygame.font.SysFont('Arial', 12)
        help_text = small_font.render("Press ESC or click outside to close", True, (200, 200, 200))
        screen.blit(help_text, (inv_x + inv_width - 180, inv_y + 12))
        
        # Draw slots
        start_x = inv_x + 10
        start_y = inv_y + 35
        
        for row in range(rows):
            for col in range(cols):
                idx = row * cols + col
                slot_x = start_x + col * (self.slot_size + self.slot_spacing)
                slot_y = start_y + row * (self.slot_size + self.slot_spacing)
                slot_rect = pygame.Rect(slot_x, slot_y, self.slot_size, self.slot_size)
                
                # Slot background
                pygame.draw.rect(screen, (30, 25, 20), slot_rect, border_radius=5)
                pygame.draw.rect(screen, (70, 60, 50), slot_rect, 1, border_radius=5)
                
                # Draw item
                item = self.slots[idx]
                if item:
                    # Draw item icon centered in slot
                    icon = item.icon
                    icon_rect = icon.get_rect(center=slot_rect.center)
                    screen.blit(icon, icon_rect)
                    
                    # Quantity
                    if item.quantity > 1:
                        qty_font = pygame.font.SysFont('Arial', 14, bold=True)
                        qty_text = qty_font.render(str(item.quantity), True, (255, 255, 255))
                        screen.blit(qty_text, (slot_x + self.slot_size - 18, slot_y + self.slot_size - 18))

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