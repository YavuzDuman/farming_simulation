"""
Inventory System - 10-slot inventory with tools and items
"""
import pygame
from typing import Optional, Callable
from enum import Enum


class ToolType(Enum):
    """Types of tools available"""
    SWORD = 0
    HOE = 1
    AXE = 2
    HAMMER = 3


class ItemType(Enum):
    """Types of items that can be collected"""
    WOOD = "wood"
    SEED = "seed"
    WHEAT = "wheat"


class Item:
    """Represents a collectable item"""
    
    def __init__(self, item_type: ItemType, quantity: int = 1):
        self.item_type = item_type
        self.quantity = quantity
        self.icon = self._create_icon()
    
    def _create_icon(self) -> pygame.Surface:
        """Create a visual icon for the item"""
        size = 40
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        if self.item_type == ItemType.WOOD:
            # Draw wood log
            # Log body
            pygame.draw.ellipse(surface, (139, 90, 43), (8, 12, 24, 20))
            # Wood grain lines
            pygame.draw.line(surface, (100, 65, 30), (12, 16), (12, 28), 1)
            pygame.draw.line(surface, (100, 65, 30), (18, 14), (18, 30), 1)
            pygame.draw.line(surface, (100, 65, 30), (24, 16), (24, 28), 1)
            # End grain
            pygame.draw.ellipse(surface, (160, 110, 60), (8, 10, 24, 8))
        
        elif self.item_type == ItemType.SEED:
            # Draw seed packet
            # Packet body
            pygame.draw.rect(surface, (200, 180, 150), (8, 8, 24, 28), border_radius=2)
            pygame.draw.rect(surface, (180, 160, 130), (8, 8, 24, 28), 2, border_radius=2)
            # Packet label (green)
            pygame.draw.rect(surface, (50, 150, 50), (10, 12, 20, 10))
            # Seed dots
            pygame.draw.circle(surface, (100, 80, 40), (16, 28), 2)
            pygame.draw.circle(surface, (100, 80, 40), (24, 30), 2)
            pygame.draw.circle(surface, (100, 80, 40), (20, 32), 2)
        
        elif self.item_type == ItemType.WHEAT:
            # Draw wheat bundle icon
            # Three wheat stalks
            for i, offset in enumerate([-8, 0, 8]):
                x = 20 + offset
                # Stalk
                pygame.draw.line(surface, (200, 180, 100), (x, 32), (x, 12), 2)
                # Head
                pygame.draw.ellipse(surface, (218, 165, 32), (x - 3, 6, 6, 10))
                # Grains
                pygame.draw.line(surface, (184, 134, 11), (x - 2, 8), (x + 2, 8), 1)
                pygame.draw.line(surface, (184, 134, 11), (x - 2, 12), (x + 2, 12), 1)
            # Tie/band
            pygame.draw.rect(surface, (139, 90, 43), (10, 28, 20, 4), border_radius=2)
            
        return surface
    
    def draw_on_ground(self, screen: pygame.Surface, x: int, y: int):
        """Draw the item on the ground (in a grid cell)"""
        if self.item_type == ItemType.WOOD:
            # Shadow
            pygame.draw.ellipse(screen, (30, 30, 30), (x - 8, y + 8, 16, 6))
            # Wood log
            pygame.draw.ellipse(screen, (139, 90, 43), (x - 10, y - 5, 20, 16))
            pygame.draw.ellipse(screen, (160, 110, 60), (x - 10, y - 8, 20, 6))
            # Grain
            pygame.draw.line(screen, (100, 65, 30), (x - 6, y), (x - 6, y + 8), 1)
            pygame.draw.line(screen, (100, 65, 30), (x, y - 2), (x, y + 10), 1)
            pygame.draw.line(screen, (100, 65, 30), (x + 6, y), (x + 6, y + 8), 1)
        elif self.item_type == ItemType.SEED:
            # Shadow
            pygame.draw.ellipse(screen, (30, 30, 30), (x - 6, y + 6, 12, 4))
            # Seed packet
            pygame.draw.rect(screen, (200, 180, 150), (x - 8, y - 10, 16, 20), border_radius=2)
            pygame.draw.rect(screen, (50, 150, 50), (x - 6, y - 8, 12, 6))
        elif self.item_type == ItemType.WHEAT:
            # Draw wheat bundle on ground
            # Shadow
            pygame.draw.ellipse(screen, (30, 30, 30), (x - 10, y + 8, 20, 6))
            # Multiple wheat stalks
            for i in range(3):
                offset_x = (i - 1) * 6
                # Stalk
                pygame.draw.line(screen, (200, 180, 100), 
                               (x + offset_x, y + 10), (x + offset_x, y - 5), 2)
                # Head
                pygame.draw.ellipse(screen, (218, 165, 32), 
                                  (x + offset_x - 2, y - 10, 4, 8))
                # Grains
                pygame.draw.line(screen, (184, 134, 11), 
                               (x + offset_x - 2, y - 8), (x + offset_x + 2, y - 8), 1)
                pygame.draw.line(screen, (184, 134, 11), 
                               (x + offset_x - 2, y - 5), (x + offset_x + 2, y - 5), 1)

    def draw_in_hand(self, screen: pygame.Surface, x: int, y: int, 
                     direction: str, shake_angle: float = 0):
        """Draw the item as if held by the farmer"""
        import math
        
        # Base position (farmer's hand position)
        hand_x = x
        hand_y = y
        
        # Apply shake rotation
        angle = shake_angle
        
        if self.item_type == ItemType.WOOD:
            self._draw_wood(screen, hand_x, hand_y, direction, angle)
        elif self.item_type == ItemType.SEED:
            self._draw_seeds(screen, hand_x, hand_y, direction, angle)

    def _draw_wood(self, screen, x, y, direction, angle):
        import math
        # Wood log is held horizontally
        length = 20
        rad = math.radians(angle)
        
        # Draw small log
        # Log body
        rect_width = 24
        rect_height = 12
        
        # Create a surface for the log to rotate it easily
        log_surf = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)
        pygame.draw.ellipse(log_surf, (139, 90, 43), (0, 0, rect_width, rect_height))
        # Grain lines
        pygame.draw.line(log_surf, (100, 65, 30), (4, 3), (4, 9), 1)
        pygame.draw.line(log_surf, (100, 65, 30), (12, 2), (12, 10), 1)
        pygame.draw.line(log_surf, (100, 65, 30), (20, 3), (20, 9), 1)
        
        # Rotate and blit
        rotated_log = pygame.transform.rotate(log_surf, -angle)
        log_rect = rotated_log.get_rect(center=(x, y))
        screen.blit(rotated_log, log_rect)

    def _draw_seeds(self, screen, x, y, direction, angle):
        import math
        # Seed packet is held pointing up
        rad = math.radians(angle)
        
        # Create a surface for the packet
        rect_width = 16
        rect_height = 22
        packet_surf = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)
        pygame.draw.rect(packet_surf, (200, 180, 150), (0, 0, rect_width, rect_height), border_radius=2)
        pygame.draw.rect(packet_surf, (50, 150, 50), (2, 4, 12, 8))
        
        # Rotate and blit
        rotated_packet = pygame.transform.rotate(packet_surf, -angle)
        packet_rect = rotated_packet.get_rect(center=(x, y))
        screen.blit(rotated_packet, packet_rect)


class Tool:
    """Represents a tool in the inventory"""
    
    def __init__(self, tool_type: ToolType, name: str):
        self.tool_type = tool_type
        self.name = name
        self.icon = self._create_icon()
    
    def _create_icon(self) -> pygame.Surface:
        """Create a visual icon for the tool"""
        size = 40
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        if self.tool_type == ToolType.SWORD:
            # Draw sword
            # Handle
            pygame.draw.rect(surface, (139, 69, 19), (16, 28, 8, 10))
            # Guard
            pygame.draw.rect(surface, (180, 180, 180), (8, 24, 24, 4))
            # Blade
            pygame.draw.polygon(surface, (200, 200, 220), [
                (18, 24), (22, 24), (23, 4), (17, 4)
            ])
            # Blade edge
            pygame.draw.line(surface, (255, 255, 255), (22, 24), (23, 4), 1)
            
        elif self.tool_type == ToolType.HOE:
            # Draw hoe
            # Handle
            pygame.draw.rect(surface, (160, 82, 45), (18, 8, 4, 28))
            # Metal head
            pygame.draw.polygon(surface, (120, 120, 130), [
                (8, 8), (32, 8), (28, 16), (12, 16)
            ])
            # Blade edge
            pygame.draw.line(surface, (200, 200, 200), (8, 8), (12, 16), 2)
            
        elif self.tool_type == ToolType.AXE:
            # Draw axe
            # Handle
            pygame.draw.rect(surface, (160, 82, 45), (18, 6, 5, 30))
            # Axe head (metal)
            pygame.draw.polygon(surface, (180, 180, 190), [
                (8, 8), (22, 8), (22, 20), (12, 22)
            ])
            # Blade edge
            pygame.draw.line(surface, (220, 220, 220), (8, 8), (12, 22), 2)
            # Head back
            pygame.draw.rect(surface, (140, 140, 150), (20, 8, 6, 12))
            
        elif self.tool_type == ToolType.HAMMER:
            # Draw hammer
            # Handle
            pygame.draw.rect(surface, (160, 82, 45), (18, 12, 4, 26))
            # Head
            pygame.draw.rect(surface, (80, 80, 90), (8, 8, 24, 10))
            # Face
            pygame.draw.rect(surface, (180, 180, 190), (6, 8, 4, 10))
            pygame.draw.rect(surface, (180, 180, 190), (30, 8, 4, 10))
        
        return surface
    
    def draw_in_hand(self, screen: pygame.Surface, x: int, y: int, 
                     direction: str, shake_angle: float = 0):
        """Draw the tool as if held by the farmer"""
        import math
        
        # Base position (farmer's hand position)
        hand_x = x
        hand_y = y
        
        # Apply shake rotation
        angle = shake_angle
        
        if self.tool_type == ToolType.SWORD:
            self._draw_sword(screen, hand_x, hand_y, direction, angle)
        elif self.tool_type == ToolType.HOE:
            self._draw_hoe(screen, hand_x, hand_y, direction, angle)
        elif self.tool_type == ToolType.AXE:
            self._draw_axe(screen, hand_x, hand_y, direction, angle)
        elif self.tool_type == ToolType.HAMMER:
            self._draw_hammer(screen, hand_x, hand_y, direction, angle)
    
    def _draw_sword(self, screen, x, y, direction, angle):
        import math
        # Sword is held pointing forward/slightly up
        length = 28
        rad = math.radians(angle - 45)  # Default angle
        
        end_x = x + int(math.cos(rad) * length)
        end_y = y + int(math.sin(rad) * length)
        
        # Blade
        pygame.draw.line(screen, (200, 200, 220), (x, y), (end_x, end_y), 4)
        # Edge highlight
        pygame.draw.line(screen, (255, 255, 255), (x, y), (end_x, end_y), 2)
        # Guard
        perp_x = int(math.cos(rad + 1.57) * 8)
        perp_y = int(math.sin(rad + 1.57) * 8)
        pygame.draw.line(screen, (180, 180, 180), 
                        (x - perp_x, y - perp_y), (x + perp_x, y + perp_y), 3)
        # Handle
        handle_end_x = x - int(math.cos(rad) * 8)
        handle_end_y = y - int(math.sin(rad) * 8)
        pygame.draw.line(screen, (139, 69, 19), (x, y), (handle_end_x, handle_end_y), 4)
    
    def _draw_hoe(self, screen, x, y, direction, angle):
        import math
        # Hoe is held with blade forward
        handle_length = 20
        rad = math.radians(angle + 30)
        
        # Handle
        end_x = x + int(math.cos(rad) * handle_length)
        end_y = y + int(math.sin(rad) * handle_length)
        pygame.draw.line(screen, (160, 82, 45), (x, y), (end_x, end_y), 3)
        
        # Blade (perpendicular to handle)
        blade_rad = rad + 1.57
        blade_x1 = end_x + int(math.cos(blade_rad) * 10)
        blade_y1 = end_y + int(math.sin(blade_rad) * 10)
        blade_x2 = end_x - int(math.cos(blade_rad) * 10)
        blade_y2 = end_y - int(math.sin(blade_rad) * 10)
        
        pygame.draw.polygon(screen, (120, 120, 130), [
            (end_x, end_y), (blade_x1, blade_y1), (blade_x2, blade_y2)
        ])
        # Blade edge
        pygame.draw.line(screen, (200, 200, 200), (blade_x1, blade_y1), (blade_x2, blade_y2), 2)
    
    def _draw_axe(self, screen, x, y, direction, angle):
        import math
        # Axe is held with blade facing forward
        handle_length = 22
        # Angle the axe based on shake
        rad = math.radians(angle + 45)
        
        # Handle
        end_x = x + int(math.cos(rad) * handle_length)
        end_y = y + int(math.sin(rad) * handle_length)
        pygame.draw.line(screen, (160, 82, 45), (x, y), (end_x, end_y), 4)
        
        # Axe head (perpendicular to handle)
        head_rad = rad + 1.57
        head_width = 12
        
        # Back of axe head
        back_x = end_x + int(math.cos(head_rad) * 4)
        back_y = end_y + int(math.sin(head_rad) * 4)
        # Front of axe head (blade)
        blade_x = end_x - int(math.cos(head_rad) * 8)
        blade_y = end_y - int(math.sin(head_rad) * 8)
        
        # Draw axe head
        pygame.draw.polygon(screen, (140, 140, 150), [
            (back_x - 4, back_y - 4), (back_x + 4, back_y + 4),
            (blade_x + 2, blade_y + 2), (blade_x - 2, blade_y - 2)
        ])
        # Blade edge
        pygame.draw.line(screen, (220, 220, 220), 
                        (blade_x - 2, blade_y - 2), (blade_x + 2, blade_y + 2), 3)
    
    def _draw_hammer(self, screen, x, y, direction, angle):
        import math
        # Hammer handle
        handle_length = 18
        rad = math.radians(angle - 90)
        
        end_x = x + int(math.cos(rad) * handle_length)
        end_y = y + int(math.sin(rad) * handle_length)
        pygame.draw.line(screen, (160, 82, 45), (x, y), (end_x, end_y), 4)
        
        # Hammer head (perpendicular)
        head_rad = rad + 1.57
        head_x1 = end_x + int(math.cos(head_rad) * 10)
        head_y1 = end_y + int(math.sin(head_rad) * 10)
        head_x2 = end_x - int(math.cos(head_rad) * 10)
        head_y2 = end_y - int(math.sin(head_rad) * 10)
        
        pygame.draw.rect(screen, (80, 80, 90), 
                        (min(head_x1, head_x2), min(head_y1, head_y2), 
                         abs(head_x1 - head_x2) + 4, abs(head_y1 - head_y2) + 4))
        # Faces
        pygame.draw.circle(screen, (180, 180, 190), (head_x1, head_y1), 3)
        pygame.draw.circle(screen, (180, 180, 190), (head_x2, head_y2), 3)


class Inventory:
    """10-slot inventory system"""
    
    def __init__(self):
        self.slots: list[Optional[Tool]] = [None] * 10  # 10 slots
        self.selected_slot: int = 0
        self.slot_size = 45
        self.slot_spacing = 8
        
        # Initialize with tools in first 4 slots
        self.slots[0] = Tool(ToolType.SWORD, "Sword")
        self.slots[1] = Tool(ToolType.HOE, "Hoe")
        self.slots[2] = Tool(ToolType.AXE, "Axe")
        self.slots[3] = Tool(ToolType.HAMMER, "Hammer")
        # Slots 4-9 are empty initially
        
        # Wood collection (stored as Item in slots 4+)
        self.wood_count = 0
        
        # Tool shake animation
        self.is_shaking = False
        self.shake_timer = 0
        self.shake_duration = 15  # frames
        self.shake_angle = 0
        
        # Click callback
        self.on_slot_click: Optional[Callable[[int], None]] = None
    
    def get_selected_tool(self) -> Optional[Tool]:
        """Get the currently selected tool"""
        return self.slots[self.selected_slot]
    
    def select_slot(self, slot_index: int):
        """Select a slot by index"""
        if 0 <= slot_index < len(self.slots):
            self.selected_slot = slot_index
    
    def add_item(self, item: Item) -> bool:
        """Add any item to inventory. Returns True if successful."""
        # Try to stack if it's the same type
        for i in range(4, 10):
            if isinstance(self.slots[i], Item) and self.slots[i].item_type == item.item_type:
                self.slots[i].quantity += item.quantity
                if item.item_type == ItemType.WOOD:
                    self.wood_count += item.quantity
                return True
        
        # Find empty slot
        for i in range(4, 10):
            if self.slots[i] is None:
                self.slots[i] = item
                if item.item_type == ItemType.WOOD:
                    self.wood_count += item.quantity
                return True
        
        return False  # Inventory full

    def add_wood(self, quantity: int = 1) -> bool:
        """Add wood to inventory. Returns True if successful."""
        # Try to stack with existing wood in slots 4+
        for i in range(4, 10):
            if isinstance(self.slots[i], Item) and self.slots[i].item_type == ItemType.WOOD:
                self.slots[i].quantity += quantity
                self.wood_count += quantity
                return True
        
        # Find empty slot for new wood
        for i in range(4, 10):
            if self.slots[i] is None:
                self.slots[i] = Item(ItemType.WOOD, quantity)
                self.wood_count += quantity
                return True
        
        return False  # Inventory full
    
    def handle_click(self, mouse_pos: tuple[int, int], 
                    inventory_rect: pygame.Rect) -> bool:
        """Handle mouse click on inventory slots"""
        x, y = mouse_pos
        
        # Check if click is within inventory area
        if not inventory_rect.collidepoint(x, y):
            return False
        
        # Calculate which slot was clicked
        relative_x = x - inventory_rect.x
        slot_total_width = self.slot_size + self.slot_spacing
        
        for i in range(len(self.slots)):
            slot_x = i * slot_total_width
            slot_rect = pygame.Rect(
                inventory_rect.x + slot_x,
                inventory_rect.y,
                self.slot_size,
                self.slot_size
            )
            if slot_rect.collidepoint(x, y):
                self.select_slot(i)
                if self.on_slot_click:
                    self.on_slot_click(i)
                return True
        
        return False
    
    def start_shake(self):
        """Start the tool shake animation"""
        self.is_shaking = True
        self.shake_timer = self.shake_duration
    
    def update(self):
        """Update inventory animations"""
        if self.is_shaking:
            self.shake_timer -= 1
            # Calculate shake angle (oscillate)
            progress = 1 - (self.shake_timer / self.shake_duration)
            self.shake_angle = math.sin(progress * math.pi * 4) * 30  # +/- 30 degrees
            
            if self.shake_timer <= 0:
                self.is_shaking = False
                self.shake_angle = 0
    
    def get_shake_angle(self) -> float:
        """Get current shake angle for tool rendering"""
        return self.shake_angle if self.is_shaking else 0
    
    def draw(self, screen: pygame.Surface, x: int, y: int):
        """Draw the inventory bar at the specified position"""
        import math
        
        total_width = len(self.slots) * self.slot_size + (len(self.slots) - 1) * self.slot_spacing
        
        # Draw background panel
        panel_padding = 10
        panel_rect = pygame.Rect(
            x - panel_padding,
            y - panel_padding,
            total_width + panel_padding * 2,
            self.slot_size + panel_padding * 2
        )
        pygame.draw.rect(screen, (40, 40, 40, 200), panel_rect, border_radius=10)
        pygame.draw.rect(screen, (80, 80, 80), panel_rect, 2, border_radius=10)
        
        # Draw slots
        for i, slot_content in enumerate(self.slots):
            slot_x = x + i * (self.slot_size + self.slot_spacing)
            slot_rect = pygame.Rect(slot_x, y, self.slot_size, self.slot_size)
            
            # Slot background
            if i == self.selected_slot:
                # Selected slot - brighter
                pygame.draw.rect(screen, (100, 100, 120), slot_rect, border_radius=5)
                pygame.draw.rect(screen, (255, 215, 0), slot_rect, 3, border_radius=5)  # Gold border
            else:
                # Unselected slot
                pygame.draw.rect(screen, (60, 60, 70), slot_rect, border_radius=5)
                pygame.draw.rect(screen, (100, 100, 100), slot_rect, 1, border_radius=5)
            
            # Draw content (tool or item) if present
            if slot_content:
                icon = slot_content.icon
                icon_rect = icon.get_rect(center=slot_rect.center)
                screen.blit(icon, icon_rect)
                
                # If it's an item with quantity > 1, show the count
                if isinstance(slot_content, Item) and slot_content.quantity > 1:
                    font = pygame.font.SysFont('Arial', 12, bold=True)
                    qty_text = font.render(str(slot_content.quantity), True, (255, 255, 255))
                    screen.blit(qty_text, (slot_x + self.slot_size - 16, y + self.slot_size - 16))
            
            # Draw slot number (0-9)
            font = pygame.font.SysFont('Arial', 12)
            number_text = font.render(str(i), True, (180, 180, 180))
            screen.blit(number_text, (slot_x + 3, y + 2))
        
        return panel_rect


# Need to import math at module level
import math