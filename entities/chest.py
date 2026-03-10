"""
Chest Entity - Grid-sized treasure chest
"""
import pygame
from typing import Tuple, List, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CHEST_WOOD, CHEST_GOLD, GRID_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, SEED_GROWTH_TIMES
from game.inventory import Item, Tool, ItemType


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

        # Inventory (2x5 slots) - can hold both Items and Tools
        self.slots: List[Optional[object]] = [None] * 10
        self.slots[0] = Item(ItemType.SEED, 50)  # Wheat seeds
        self.slots[1] = Item(ItemType.CARROT_SEED, 30)  # Carrot seeds
        
        self.is_open = False
        self.inventory_rect = None
        self.slot_size = 48
        self.slot_spacing = 8
        
        # Player inventory reference for transfers
        self.player_inventory = None
        
        # Drag and drop state
        self.dragging = False
        self.drag_source = None  # ('chest', slot_idx) or ('player', slot_idx)
        self.drag_item = None
        
        # Slot rects for hover detection
        self.chest_slot_rects: List[pygame.Rect] = []
        self.player_slot_rects: List[pygame.Rect] = []
    
    def set_player_inventory(self, inventory):
        """Set reference to player inventory for transfers"""
        self.player_inventory = inventory
    
    def toggle_inventory(self):
        """Toggle the chest inventory display"""
        self.is_open = not self.is_open
    
    def close_inventory(self):
        """Close the chest inventory"""
        self.is_open = False
        self.dragging = False
        self.drag_item = None
        self.drag_source = None
    
    def handle_click(self, mouse_pos: Tuple[int, int]) -> Optional[Item]:
        """Handle click on chest inventory slots. Returns item if clicked for legacy compatibility."""
        if not self.is_open or not self.inventory_rect:
            return None
        
        x, y = mouse_pos
        
        # Update slot rects
        self._update_slot_rects()
        
        # Check chest slots for drag start
        for i, rect in enumerate(self.chest_slot_rects):
            if rect.collidepoint(x, y):
                if self.slots[i]:
                    self.dragging = True
                    self.drag_source = ('chest', i)
                    self.drag_item = self.slots[i]
                return None
        
        # Check player inventory slots for drag start
        if self.player_inventory:
            for i, rect in enumerate(self.player_slot_rects):
                if rect.collidepoint(x, y):
                    if self.player_inventory.slots[i]:
                        self.dragging = True
                        self.drag_source = ('player', i)
                        self.drag_item = self.player_inventory.slots[i]
                    return None
        
        return None
    
    def handle_release(self, mouse_pos: Tuple[int, int], hotbar_rect: pygame.Rect = None, hotbar_slot_rects: List[pygame.Rect] = None):
        """Handle mouse release for drag and drop"""
        if not self.dragging or not self.drag_item:
            self.dragging = False
            self.drag_item = None
            self.drag_source = None
            return
        
        x, y = mouse_pos
        
        # Check if dropped on chest slots
        for i, rect in enumerate(self.chest_slot_rects):
            if rect.collidepoint(x, y):
                self._drop_on_chest_slot(i)
                self.dragging = False
                self.drag_item = None
                self.drag_source = None
                return
        
        # Check if dropped on hotbar slots
        if hotbar_slot_rects and self.player_inventory:
            for i, rect in enumerate(hotbar_slot_rects):
                if rect.collidepoint(x, y):
                    self._drop_on_player_slot(i)
                    self.dragging = False
                    self.drag_item = None
                    self.drag_source = None
                    return
        
        # Dropped outside - cancel
        self.dragging = False
        self.drag_item = None
        self.drag_source = None
    
    def _drop_on_chest_slot(self, target_idx: int):
        """Handle dropping an item on a chest slot"""
        if self.drag_source[0] == 'chest':
            source_idx = self.drag_source[1]
            if source_idx != target_idx:
                # Swap items within chest
                self.slots[source_idx], self.slots[target_idx] = \
                    self.slots[target_idx], self.slots[source_idx]
        elif self.drag_source[0] == 'player' and self.player_inventory:
            source_idx = self.drag_source[1]
            # Swap items between player and chest
            self.player_inventory.slots[source_idx], self.slots[target_idx] = \
                self.slots[target_idx], self.player_inventory.slots[source_idx]
    
    def _drop_on_player_slot(self, target_idx: int):
        """Handle dropping an item on a player inventory slot"""
        if not self.player_inventory:
            return
        
        if self.drag_source[0] == 'player':
            source_idx = self.drag_source[1]
            if source_idx != target_idx:
                # Swap slots within player inventory (including tools)
                self.player_inventory.slots[source_idx], self.player_inventory.slots[target_idx] = \
                    self.player_inventory.slots[target_idx], self.player_inventory.slots[source_idx]
        elif self.drag_source[0] == 'chest':
            source_idx = self.drag_source[1]
            # Swap items between chest and player (including tools)
            self.slots[source_idx], self.player_inventory.slots[target_idx] = \
                self.player_inventory.slots[target_idx], self.slots[source_idx]
    
    def _update_slot_rects(self):
        """Update slot rectangles for hover/click detection"""
        self.chest_slot_rects = []
        self.player_slot_rects = []
        
        if not self.inventory_rect:
            return
        
        cols = 5
        rows = 2
        start_x = self.inventory_rect.x + 10
        start_y = self.inventory_rect.y + 35
        
        # Chest slots only
        for row in range(rows):
            for col in range(cols):
                idx = row * cols + col
                slot_x = start_x + col * (self.slot_size + self.slot_spacing)
                slot_y = start_y + row * (self.slot_size + self.slot_spacing)
                slot_rect = pygame.Rect(slot_x, slot_y, self.slot_size, self.slot_size)
                self.chest_slot_rects.append(slot_rect)
    
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
        """Draw the chest inventory (player uses hotbar at bottom for transfers)"""
        if not self.is_open:
            return
        
        self._update_slot_rects()
        
        cols = 5
        rows = 2
        inv_width = cols * self.slot_size + (cols + 1) * self.slot_spacing + 20
        inv_height = rows * self.slot_size + (rows + 1) * self.slot_spacing + 40
        
        # Center on screen (higher up to not overlap with hotbar)
        inv_x = (SCREEN_WIDTH - inv_width) // 2
        inv_y = (SCREEN_HEIGHT - inv_height) // 2 - 80
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
        help_text = small_font.render("Drag items to/from hotbar | ESC to close", True, (200, 200, 200))
        screen.blit(help_text, (inv_x + inv_width - 220, inv_y + 12))
        
        # Draw chest slots
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
                
                # Draw item (if not being dragged)
                item = self.slots[idx]
                if item and not (self.dragging and self.drag_source == ('chest', idx)):
                    # Draw item icon centered in slot
                    icon = item.icon
                    icon_rect = icon.get_rect(center=slot_rect.center)
                    screen.blit(icon, icon_rect)
                    
                    # Quantity (only for Items, not Tools)
                    if isinstance(item, Item) and item.quantity > 1:
                        qty_font = pygame.font.SysFont('Arial', 14, bold=True)
                        qty_text = qty_font.render(str(item.quantity), True, (255, 255, 255))
                        screen.blit(qty_text, (slot_x + self.slot_size - 18, slot_y + self.slot_size - 18))
        
        # Draw dragged item
        if self.dragging and self.drag_item:
            mouse_pos = pygame.mouse.get_pos()
            icon = self.drag_item.icon
            icon_rect = icon.get_rect(center=mouse_pos)
            screen.blit(icon, icon_rect)
        
        # Draw tooltip for hovered item
        self._draw_tooltip(screen, pygame.mouse.get_pos())
    
    def _draw_tooltip(self, screen: pygame.Surface, mouse_pos: Tuple[int, int]):
        """Draw tooltip for hovered item"""
        font = pygame.font.SysFont('Arial', 14)
        small_font = pygame.font.SysFont('Arial', 12)
        
        # Check chest slots for hover
        for i, rect in enumerate(self.chest_slot_rects):
            if rect.collidepoint(mouse_pos) and self.slots[i] and not self.dragging:
                self._draw_item_tooltip(screen, mouse_pos, self.slots[i], font, small_font)
                return
    
    def _draw_item_tooltip(self, screen: pygame.Surface, mouse_pos: Tuple[int, int], 
                           slot_content, font, small_font):
        """Draw tooltip for an item"""
        # Get item name and description
        if isinstance(slot_content, Tool):
            name = slot_content.name
            desc = "A tool for farming"
            extra_lines = []
        elif isinstance(slot_content, Item):
            name = slot_content.item_type.value.replace('_', ' ').title()
            descriptions = {
                ItemType.WOOD: "Used for crafting",
                ItemType.SEED: "Plant to grow wheat",
                ItemType.CARROT_SEED: "Plant to grow carrots",
                ItemType.TOMATO_SEED: "Plant to grow tomatoes",
                ItemType.PUMPKIN_SEED: "Plant to grow pumpkins",
                ItemType.STRAWBERRY_SEED: "Plant to grow strawberries",
                ItemType.GOLDEN_SEED: "Rare! Plant for golden wheat",
                ItemType.WHEAT: "Sell or use for crafting",
                ItemType.CARROT: "A tasty vegetable",
                ItemType.TOMATO: "A juicy tomato",
                ItemType.PUMPKIN: "A large pumpkin",
                ItemType.STRAWBERRY: "A sweet berry",
                ItemType.GOLDEN_WHEAT: "Precious golden wheat",
                ItemType.STONE: "Used for crafting",
            }
            desc = descriptions.get(slot_content.item_type, "An item")
            if slot_content.quantity > 1:
                desc = f"{desc} (x{slot_content.quantity})"
            
            # Add growth time for seeds
            extra_lines = []
            seed_growth_map = {
                ItemType.SEED: 'wheat',
                ItemType.CARROT_SEED: 'carrot',
                ItemType.TOMATO_SEED: 'tomato',
                ItemType.PUMPKIN_SEED: 'pumpkin',
                ItemType.STRAWBERRY_SEED: 'strawberry',
                ItemType.GOLDEN_SEED: 'golden_wheat',
            }
            if slot_content.item_type in seed_growth_map:
                growth_key = seed_growth_map[slot_content.item_type]
                growth_time = SEED_GROWTH_TIMES.get(growth_key, 30)
                extra_lines.append(f"Growth time: {growth_time}s")
        else:
            return
        
        # Calculate tooltip dimensions
        name_surface = font.render(name, True, (255, 255, 255))
        desc_surface = font.render(desc, True, (200, 200, 200))
        
        max_width = max(name_surface.get_width(), desc_surface.get_width())
        for line in extra_lines:
            line_surface = small_font.render(line, True, (150, 255, 150))
            max_width = max(max_width, line_surface.get_width())
        
        tooltip_width = max_width + 20
        tooltip_height = 50 + len(extra_lines) * 18
        
        # Position tooltip near mouse
        tooltip_x = mouse_pos[0] + 15
        tooltip_y = mouse_pos[1] - tooltip_height - 5
        
        # Keep tooltip on screen
        if tooltip_x + tooltip_width > SCREEN_WIDTH:
            tooltip_x = mouse_pos[0] - tooltip_width - 15
        if tooltip_y < 0:
            tooltip_y = mouse_pos[1] + 20
        
        # Draw tooltip background
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        pygame.draw.rect(screen, (30, 30, 40), tooltip_rect, border_radius=5)
        pygame.draw.rect(screen, (100, 100, 120), tooltip_rect, 2, border_radius=5)
        
        # Draw name and description
        screen.blit(name_surface, (tooltip_x + 10, tooltip_y + 8))
        screen.blit(desc_surface, (tooltip_x + 10, tooltip_y + 28))
        
        # Draw extra lines (growth time)
        y_offset = 48
        for line in extra_lines:
            line_surface = small_font.render(line, True, (150, 255, 150))
            screen.blit(line_surface, (tooltip_x + 10, tooltip_y + y_offset))
            y_offset += 18

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