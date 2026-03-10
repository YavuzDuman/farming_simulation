"""
Extended Inventory UI - Full inventory view with drag and drop support
"""
import pygame
from typing import Optional, List, Tuple
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, YELLOW, RED, SEED_GROWTH_TIMES
from game.inventory import Inventory, Item, Tool, ToolType, ItemType


class ExtendedInventoryUI:
    """Extended inventory UI with drag and drop support"""
    
    def __init__(self, inventory: Inventory):
        self.inventory = inventory
        self.is_open = False
        
        # Panel dimensions
        self.width = 500
        self.height = 400
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = (SCREEN_HEIGHT - self.height) // 2
        
        # Extended slots (20 additional slots in a 5x4 grid)
        self.extended_slots: List[Optional[Item]] = [None] * 20
        
        # Fonts
        self.title_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.small_font = pygame.font.SysFont('Arial', 12)
        
        # Slot settings
        self.slot_size = 45
        self.slot_spacing = 8
        self.hotbar_cols = 10
        self.extended_cols = 5
        self.extended_rows = 4
        
        # Drag and drop state
        self.dragging = False
        self.drag_source = None  # ('hotbar', slot_idx) or ('extended', slot_idx)
        self.drag_item = None
        self.drag_offset = (0, 0)
        
        # Garbage bin
        self.garbage_rect = pygame.Rect(self.x + self.width + 20, self.y + 150, 60, 60)
        self.garbage_hover = False
        
        # Close button
        self.close_button_rect = pygame.Rect(self.x + self.width - 35, self.y + 10, 25, 25)
        
        # Store slot rects for click detection
        self.hotbar_slot_rects: List[pygame.Rect] = []
        self.extended_slot_rects: List[pygame.Rect] = []
    
    def open(self):
        """Open the extended inventory"""
        self.is_open = True
        self._update_slot_rects()
    
    def close(self):
        """Close the extended inventory"""
        self.is_open = False
        self.dragging = False
        self.drag_item = None
        self.drag_source = None
    
    def toggle(self):
        """Toggle the extended inventory"""
        if self.is_open:
            self.close()
        else:
            self.open()
    
    def _update_slot_rects(self):
        """Update the slot rectangles for click detection"""
        self.hotbar_slot_rects = []
        self.extended_slot_rects = []
        
        # Hotbar slots (bottom of panel)
        hotbar_y = self.y + self.height - 70
        hotbar_start_x = self.x + (self.width - (self.hotbar_cols * self.slot_size + (self.hotbar_cols - 1) * self.slot_spacing)) // 2
        
        for i in range(10):
            slot_x = hotbar_start_x + i * (self.slot_size + self.slot_spacing)
            slot_rect = pygame.Rect(slot_x, hotbar_y, self.slot_size, self.slot_size)
            self.hotbar_slot_rects.append(slot_rect)
        
        # Extended slots (main area)
        extended_start_x = self.x + (self.width - (self.extended_cols * self.slot_size + (self.extended_cols - 1) * self.slot_spacing)) // 2
        extended_start_y = self.y + 60
        
        for row in range(self.extended_rows):
            for col in range(self.extended_cols):
                slot_x = extended_start_x + col * (self.slot_size + self.slot_spacing)
                slot_y = extended_start_y + row * (self.slot_size + self.slot_spacing)
                slot_rect = pygame.Rect(slot_x, slot_y, self.slot_size, self.slot_size)
                self.extended_slot_rects.append(slot_rect)
        
        # Update garbage rect position
        self.garbage_rect = pygame.Rect(self.x + self.width + 20, self.y + 150, 60, 60)
        
        # Update close button
        self.close_button_rect = pygame.Rect(self.x + self.width - 35, self.y + 10, 25, 25)
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Handle events for the extended inventory. Returns 'close' if should close."""
        if not self.is_open:
            return None
        
        self._update_slot_rects()
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            
            # Check close button
            if self.close_button_rect.collidepoint(mouse_pos):
                self.close()
                return "close"
            
            # Check hotbar slots
            for i, rect in enumerate(self.hotbar_slot_rects):
                if rect.collidepoint(mouse_pos):
                    if self.inventory.slots[i]:
                        self.dragging = True
                        self.drag_source = ('hotbar', i)
                        self.drag_item = self.inventory.slots[i]
                        self.drag_offset = (mouse_pos[0] - rect.centerx, mouse_pos[1] - rect.centery)
                    return None
            
            # Check extended slots
            for i, rect in enumerate(self.extended_slot_rects):
                if rect.collidepoint(mouse_pos):
                    if self.extended_slots[i]:
                        self.dragging = True
                        self.drag_source = ('extended', i)
                        self.drag_item = self.extended_slots[i]
                        self.drag_offset = (mouse_pos[0] - rect.centerx, mouse_pos[1] - rect.centery)
                    return None
            
            # Click outside panel closes it
            panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            if not panel_rect.collidepoint(mouse_pos) and not self.garbage_rect.collidepoint(mouse_pos):
                self.close()
                return "close"
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging and self.drag_item:
                mouse_pos = event.pos
                
                # Check if dropped on garbage
                if self.garbage_rect.collidepoint(mouse_pos):
                    self._delete_item()
                else:
                    # Check hotbar slots
                    for i, rect in enumerate(self.hotbar_slot_rects):
                        if rect.collidepoint(mouse_pos):
                            self._drop_on_hotbar(i)
                            break
                    else:
                        # Check extended slots
                        for i, rect in enumerate(self.extended_slot_rects):
                            if rect.collidepoint(mouse_pos):
                                self._drop_on_extended(i)
                                break
                
                self.dragging = False
                self.drag_item = None
                self.drag_source = None
        
        elif event.type == pygame.MOUSEMOTION:
            # Update garbage hover state
            self.garbage_hover = self.garbage_rect.collidepoint(event.pos)
        
        return None
    
    def _drop_on_hotbar(self, target_idx: int):
        """Handle dropping an item on a hotbar slot"""
        if self.drag_source[0] == 'hotbar':
            source_idx = self.drag_source[1]
            if source_idx != target_idx:
                # Swap slots (including tools)
                self.inventory.slots[source_idx], self.inventory.slots[target_idx] = \
                    self.inventory.slots[target_idx], self.inventory.slots[source_idx]
        elif self.drag_source[0] == 'extended':
            source_idx = self.drag_source[1]
            # Swap slots (including tools)
            self.extended_slots[source_idx], self.inventory.slots[target_idx] = \
                self.inventory.slots[target_idx], self.extended_slots[source_idx]
    
    def _drop_on_extended(self, target_idx: int):
        """Handle dropping an item on an extended slot"""
        if self.drag_source[0] == 'extended':
            source_idx = self.drag_source[1]
            if source_idx != target_idx:
                # Swap slots (including tools)
                self.extended_slots[source_idx], self.extended_slots[target_idx] = \
                    self.extended_slots[target_idx], self.extended_slots[source_idx]
        elif self.drag_source[0] == 'hotbar':
            source_idx = self.drag_source[1]
            # Swap slots (including tools)
            self.inventory.slots[source_idx], self.extended_slots[target_idx] = \
                self.extended_slots[target_idx], self.inventory.slots[source_idx]
    
    def _delete_item(self):
        """Delete the dragged item"""
        if self.drag_source[0] == 'hotbar':
            # Allow deleting anything from hotbar
            self.inventory.slots[self.drag_source[1]] = None
        elif self.drag_source[0] == 'extended':
            # Allow deleting anything from extended slots
            self.extended_slots[self.drag_source[1]] = None
    
    def add_item(self, item: Item) -> bool:
        """Add an item to extended inventory. Returns True if successful."""
        # Try to stack with existing items
        for i, slot in enumerate(self.extended_slots):
            if isinstance(slot, Item) and slot.item_type == item.item_type:
                slot.quantity += item.quantity
                return True
        
        # Find empty slot
        for i, slot in enumerate(self.extended_slots):
            if slot is None:
                self.extended_slots[i] = item
                return True
        
        return False
    
    def draw(self, screen: pygame.Surface):
        """Draw the extended inventory UI"""
        if not self.is_open:
            return
        
        self._update_slot_rects()
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Draw main panel
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, (50, 40, 35), panel_rect, border_radius=10)
        pygame.draw.rect(screen, (100, 80, 60), panel_rect, 3, border_radius=10)
        
        # Draw title
        title_surface = self.title_font.render("Inventory", True, YELLOW)
        title_rect = title_surface.get_rect(centerx=self.x + self.width // 2, top=self.y + 15)
        screen.blit(title_surface, title_rect)
        
        # Draw close button
        pygame.draw.rect(screen, (150, 50, 50), self.close_button_rect, border_radius=5)
        pygame.draw.rect(screen, (200, 80, 80), self.close_button_rect, 2, border_radius=5)
        x_text = self.title_font.render("X", True, WHITE)
        x_rect = x_text.get_rect(center=self.close_button_rect.center)
        screen.blit(x_text, x_rect)
        
        # Draw extended slots
        for i, rect in enumerate(self.extended_slot_rects):
            # Slot background
            pygame.draw.rect(screen, (60, 55, 50), rect, border_radius=5)
            pygame.draw.rect(screen, (90, 85, 75), rect, 2, border_radius=5)
            
            # Draw item if present (and not being dragged)
            if self.extended_slots[i] and not (self.dragging and self.drag_source == ('extended', i)):
                item = self.extended_slots[i]
                icon = item.icon
                icon_rect = icon.get_rect(center=rect.center)
                screen.blit(icon, icon_rect)
                
                # Draw quantity
                if isinstance(item, Item) and item.quantity > 1:
                    qty_text = self.small_font.render(str(item.quantity), True, WHITE)
                    screen.blit(qty_text, (rect.right - 15, rect.bottom - 15))
        
        # Draw separator line
        sep_y = self.y + self.height - 85
        pygame.draw.line(screen, (100, 80, 60), (self.x + 20, sep_y), (self.x + self.width - 20, sep_y), 2)
        
        # Draw hotbar label
        hotbar_label = self.small_font.render("Hotbar", True, (180, 180, 180))
        screen.blit(hotbar_label, (self.x + 20, sep_y + 5))
        
        # Draw hotbar slots
        for i, rect in enumerate(self.hotbar_slot_rects):
            # Slot background
            if i == self.inventory.selected_slot:
                pygame.draw.rect(screen, (80, 80, 100), rect, border_radius=5)
                pygame.draw.rect(screen, YELLOW, rect, 3, border_radius=5)
            else:
                pygame.draw.rect(screen, (60, 55, 50), rect, border_radius=5)
                pygame.draw.rect(screen, (90, 85, 75), rect, 2, border_radius=5)
            
            # Draw item if present (and not being dragged)
            if self.inventory.slots[i] and not (self.dragging and self.drag_source == ('hotbar', i)):
                item = self.inventory.slots[i]
                icon = item.icon
                icon_rect = icon.get_rect(center=rect.center)
                screen.blit(icon, icon_rect)
                
                # Draw quantity
                if isinstance(item, Item) and item.quantity > 1:
                    qty_text = self.small_font.render(str(item.quantity), True, WHITE)
                    screen.blit(qty_text, (rect.right - 15, rect.bottom - 15))
            
            # Draw slot number
            num_text = self.small_font.render(str(i), True, (150, 150, 150))
            screen.blit(num_text, (rect.left + 3, rect.top + 2))
        
        # Draw garbage bin
        garbage_color = (100, 60, 60) if self.garbage_hover else (80, 50, 50)
        pygame.draw.rect(screen, garbage_color, self.garbage_rect, border_radius=10)
        pygame.draw.rect(screen, (150, 80, 80), self.garbage_rect, 3, border_radius=10)
        
        # Draw garbage icon (trash can)
        can_x = self.garbage_rect.centerx
        can_y = self.garbage_rect.centery
        # Can body
        pygame.draw.rect(screen, (120, 70, 70), (can_x - 15, can_y - 10, 30, 25), border_radius=3)
        # Can lid
        pygame.draw.rect(screen, (140, 80, 80), (can_x - 18, can_y - 15, 36, 8), border_radius=2)
        # Lines on can
        pygame.draw.line(screen, (100, 60, 60), (can_x - 8, can_y - 5), (can_x - 8, can_y + 10), 2)
        pygame.draw.line(screen, (100, 60, 60), (can_x, can_y - 5), (can_x, can_y + 10), 2)
        pygame.draw.line(screen, (100, 60, 60), (can_x + 8, can_y - 5), (can_x + 8, can_y + 10), 2)
        
        # Label
        trash_label = self.small_font.render("Trash", True, (180, 100, 100))
        label_rect = trash_label.get_rect(centerx=self.garbage_rect.centerx, top=self.garbage_rect.bottom + 5)
        screen.blit(trash_label, label_rect)
        
        # Draw dragged item last (on top of everything)
        if self.dragging and self.drag_item:
            mouse_pos = pygame.mouse.get_pos()
            icon = self.drag_item.icon
            icon_rect = icon.get_rect(center=mouse_pos)
            screen.blit(icon, icon_rect)
        
        # Draw tooltip for hovered item
        mouse_pos = pygame.mouse.get_pos()
        self._draw_tooltip(screen, mouse_pos)
    
    def _draw_tooltip(self, screen: pygame.Surface, mouse_pos: Tuple[int, int]):
        """Draw tooltip for hovered item"""
        font = pygame.font.SysFont('Arial', 14)
        small_font = pygame.font.SysFont('Arial', 12)
        
        # Check extended slots for hover
        for i, rect in enumerate(self.extended_slot_rects):
            if rect.collidepoint(mouse_pos) and self.extended_slots[i] and not self.dragging:
                self._draw_item_tooltip(screen, mouse_pos, self.extended_slots[i], font, small_font)
                return
        
        # Check hotbar slots for hover
        for i, rect in enumerate(self.hotbar_slot_rects):
            if rect.collidepoint(mouse_pos) and self.inventory.slots[i] and not self.dragging:
                self._draw_item_tooltip(screen, mouse_pos, self.inventory.slots[i], font, small_font)
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
