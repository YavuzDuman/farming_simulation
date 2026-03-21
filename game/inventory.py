"""
Inventory System - 10-slot inventory with tools and items
"""
import pygame
from typing import Optional, Callable, List
from enum import Enum
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SEED_GROWTH_TIMES


class ToolType(Enum):
    """Types of tools available"""
    SWORD = 0
    IRON_SWORD = 4
    GOLDEN_SWORD = 5
    DIAMOND_SWORD = 6
    HOE = 1
    AXE = 2
    HAMMER = 3


# Sword damage values
SWORD_DAMAGE = {
    ToolType.SWORD: 1,        # Wooden sword - 1 damage (5 hits to kill brute)
    ToolType.IRON_SWORD: 2,   # Iron sword - 2 damage (3 hits to kill brute)
    ToolType.GOLDEN_SWORD: 3, # Golden sword - 3 damage (2 hits to kill brute)
    ToolType.DIAMOND_SWORD: 5 # Diamond sword - 5 damage (1 hit to kill brute)
}


class ItemType(Enum):
    """Types of items that can be collected"""
    WOOD = "wood"
    SEED = "seed"
    CARROT_SEED = "carrot_seed"
    WHEAT = "wheat"
    CARROT = "carrot"
    STONE = "stone"
    # Precious seeds
    TOMATO_SEED = "tomato_seed"
    PUMPKIN_SEED = "pumpkin_seed"
    STRAWBERRY_SEED = "strawberry_seed"
    GOLDEN_SEED = "golden_seed"
    # Precious crops
    TOMATO = "tomato"
    PUMPKIN = "pumpkin"
    STRAWBERRY = "strawberry"
    GOLDEN_WHEAT = "golden_wheat"
    # Animals
    CHICKEN = "chicken"
    COW = "cow"
    # Animal products
    EGG = "egg"


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
        
        elif self.item_type == ItemType.CARROT_SEED:
            # Draw carrot seed packet
            pygame.draw.rect(surface, (210, 170, 130), (8, 8, 24, 28), border_radius=2)
            pygame.draw.rect(surface, (180, 140, 100), (8, 8, 24, 28), 2, border_radius=2)
            # Packet label (orange)
            pygame.draw.rect(surface, (240, 140, 40), (10, 12, 20, 10))
            # Seed dots
            pygame.draw.circle(surface, (120, 90, 40), (16, 28), 2)
            pygame.draw.circle(surface, (120, 90, 40), (24, 30), 2)
            pygame.draw.circle(surface, (120, 90, 40), (20, 32), 2)
        
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
        
        elif self.item_type == ItemType.CARROT:
            # Draw carrot icon
            pygame.draw.polygon(surface, (240, 140, 40), [(20, 8), (30, 30), (10, 30)])
            # Leafy top
            pygame.draw.line(surface, (60, 180, 60), (20, 6), (14, 12), 2)
            pygame.draw.line(surface, (60, 180, 60), (20, 6), (20, 12), 2)
            pygame.draw.line(surface, (60, 180, 60), (20, 6), (26, 12), 2)
        
        elif self.item_type == ItemType.STONE:
            # Draw stone icon
            # Main stone shape
            pygame.draw.ellipse(surface, (130, 130, 130), (8, 12, 24, 18))
            # Highlight
            pygame.draw.ellipse(surface, (160, 160, 160), (10, 14, 12, 8))
            # Shadow
            pygame.draw.ellipse(surface, (100, 100, 100), (10, 24, 20, 6))
            # Cracks
            pygame.draw.line(surface, (90, 90, 90), (14, 18), (18, 26), 1)
            pygame.draw.line(surface, (90, 90, 90), (24, 16), (26, 24), 1)
        
        elif self.item_type == ItemType.TOMATO_SEED:
            # Draw tomato seed packet
            pygame.draw.rect(surface, (220, 180, 140), (8, 8, 24, 28), border_radius=2)
            pygame.draw.rect(surface, (180, 140, 100), (8, 8, 24, 28), 2, border_radius=2)
            # Packet label (red)
            pygame.draw.rect(surface, (220, 60, 60), (10, 12, 20, 10))
            # Seed dots
            pygame.draw.circle(surface, (180, 140, 100), (16, 28), 2)
            pygame.draw.circle(surface, (180, 140, 100), (24, 30), 2)
            pygame.draw.circle(surface, (180, 140, 100), (20, 32), 2)
        
        elif self.item_type == ItemType.PUMPKIN_SEED:
            # Draw pumpkin seed packet
            pygame.draw.rect(surface, (230, 190, 140), (8, 8, 24, 28), border_radius=2)
            pygame.draw.rect(surface, (190, 150, 100), (8, 8, 24, 28), 2, border_radius=2)
            # Packet label (orange)
            pygame.draw.rect(surface, (240, 140, 40), (10, 12, 20, 10))
            # Seed dots
            pygame.draw.circle(surface, (200, 160, 100), (16, 28), 2)
            pygame.draw.circle(surface, (200, 160, 100), (24, 30), 2)
            pygame.draw.circle(surface, (200, 160, 100), (20, 32), 2)
        
        elif self.item_type == ItemType.STRAWBERRY_SEED:
            # Draw strawberry seed packet
            pygame.draw.rect(surface, (240, 200, 160), (8, 8, 24, 28), border_radius=2)
            pygame.draw.rect(surface, (200, 160, 120), (8, 8, 24, 28), 2, border_radius=2)
            # Packet label (pink/red)
            pygame.draw.rect(surface, (255, 100, 120), (10, 12, 20, 10))
            # Seed dots
            pygame.draw.circle(surface, (220, 180, 130), (16, 28), 2)
            pygame.draw.circle(surface, (220, 180, 130), (24, 30), 2)
            pygame.draw.circle(surface, (220, 180, 130), (20, 32), 2)
        
        elif self.item_type == ItemType.GOLDEN_SEED:
            # Draw golden seed packet (rare/precious)
            pygame.draw.rect(surface, (255, 230, 150), (8, 8, 24, 28), border_radius=2)
            pygame.draw.rect(surface, (200, 170, 80), (8, 8, 24, 28), 2, border_radius=2)
            # Packet label (gold)
            pygame.draw.rect(surface, (255, 215, 0), (10, 12, 20, 10))
            # Sparkle effect
            pygame.draw.line(surface, (255, 255, 200), (14, 16), (18, 20), 1)
            pygame.draw.line(surface, (255, 255, 200), (22, 16), (18, 20), 1)
            # Seed dots
            pygame.draw.circle(surface, (255, 200, 100), (16, 28), 2)
            pygame.draw.circle(surface, (255, 200, 100), (24, 30), 2)
            pygame.draw.circle(surface, (255, 200, 100), (20, 32), 2)
        
        elif self.item_type == ItemType.TOMATO:
            # Draw tomato icon
            pygame.draw.circle(surface, (220, 60, 60), (20, 22), 12)
            # Highlight
            pygame.draw.circle(surface, (255, 120, 120), (16, 18), 4)
            # Stem
            pygame.draw.rect(surface, (60, 140, 60), (18, 8, 4, 6))
            # Leaf
            pygame.draw.ellipse(surface, (60, 160, 60), (12, 6, 10, 6))
        
        elif self.item_type == ItemType.PUMPKIN:
            # Draw pumpkin icon
            pygame.draw.ellipse(surface, (240, 140, 40), (8, 14, 24, 20))
            # Ridges
            pygame.draw.arc(surface, (200, 100, 20), (10, 14, 8, 20), 0, 3.14, 1)
            pygame.draw.arc(surface, (200, 100, 20), (22, 14, 8, 20), 0, 3.14, 1)
            # Stem
            pygame.draw.rect(surface, (60, 100, 40), (18, 8, 4, 8))
        
        elif self.item_type == ItemType.STRAWBERRY:
            # Draw strawberry icon
            # Body
            pygame.draw.polygon(surface, (255, 80, 100), [
                (20, 8), (30, 28), (10, 28)
            ])
            # Seeds
            pygame.draw.circle(surface, (255, 255, 150), (16, 16), 1)
            pygame.draw.circle(surface, (255, 255, 150), (24, 16), 1)
            pygame.draw.circle(surface, (255, 255, 150), (20, 20), 1)
            pygame.draw.circle(surface, (255, 255, 150), (14, 22), 1)
            pygame.draw.circle(surface, (255, 255, 150), (26, 22), 1)
            # Leaves
            pygame.draw.polygon(surface, (60, 180, 60), [
                (20, 8), (12, 4), (16, 10), (20, 6), (24, 10), (28, 4)
            ])
        
        elif self.item_type == ItemType.GOLDEN_WHEAT:
            # Draw golden wheat bundle (precious)
            for i, offset in enumerate([-8, 0, 8]):
                x = 20 + offset
                # Stalk
                pygame.draw.line(surface, (255, 220, 100), (x, 32), (x, 12), 2)
                # Head
                pygame.draw.ellipse(surface, (255, 200, 50), (x - 3, 6, 6, 10))
                # Grains
                pygame.draw.line(surface, (255, 180, 0), (x - 2, 8), (x + 2, 8), 1)
                pygame.draw.line(surface, (255, 180, 0), (x - 2, 12), (x + 2, 12), 1)
            # Tie/band (gold)
            pygame.draw.rect(surface, (255, 215, 0), (10, 28, 20, 4), border_radius=2)
            # Sparkle
            pygame.draw.circle(surface, (255, 255, 200), (14, 14), 2)
        
        elif self.item_type == ItemType.CHICKEN:
            # Draw chicken icon
            # Body (white oval)
            pygame.draw.ellipse(surface, (255, 255, 255), (10, 14, 20, 14))
            pygame.draw.ellipse(surface, (220, 220, 220), (11, 15, 18, 12))
            # Head
            pygame.draw.circle(surface, (255, 255, 255), (26, 14), 6)
            # Comb (red)
            pygame.draw.ellipse(surface, (220, 50, 50), (24, 6, 6, 5))
            pygame.draw.ellipse(surface, (220, 50, 50), (22, 4, 4, 4))
            # Beak (orange)
            pygame.draw.polygon(surface, (255, 180, 50), [
                (30, 14), (35, 16), (30, 18)
            ])
            # Eye
            pygame.draw.circle(surface, (30, 30, 30), (27, 13), 2)
            # Feet
            pygame.draw.ellipse(surface, (255, 180, 50), (12, 26, 6, 4))
            pygame.draw.ellipse(surface, (255, 180, 50), (20, 26, 6, 4))
            # Wing
            pygame.draw.ellipse(surface, (220, 220, 220), (14, 16, 8, 8))
            # Tail
            pygame.draw.ellipse(surface, (220, 220, 220), (6, 12, 6, 8))
        
        elif self.item_type == ItemType.COW:
            # Draw cow icon
            # Body (white oval)
            pygame.draw.ellipse(surface, (255, 255, 255), (6, 14, 28, 16))
            # Spots (black)
            pygame.draw.ellipse(surface, (40, 40, 40), (10, 16, 8, 6))
            pygame.draw.ellipse(surface, (40, 40, 40), (22, 20, 6, 5))
            pygame.draw.ellipse(surface, (40, 40, 40), (14, 22, 5, 4))
            # Head
            pygame.draw.ellipse(surface, (255, 255, 255), (28, 8, 10, 12))
            # Ears
            pygame.draw.ellipse(surface, (255, 255, 255), (26, 6, 6, 4))
            pygame.draw.ellipse(surface, (255, 200, 200), (27, 7, 4, 2))
            pygame.draw.ellipse(surface, (255, 255, 255), (34, 6, 6, 4))
            pygame.draw.ellipse(surface, (255, 200, 200), (35, 7, 4, 2))
            # Horns
            pygame.draw.ellipse(surface, (230, 210, 180), (28, 4, 3, 5))
            pygame.draw.ellipse(surface, (230, 210, 180), (35, 4, 3, 5))
            # Nose (pink)
            pygame.draw.ellipse(surface, (255, 200, 200), (32, 14, 6, 4))
            # Nostrils
            pygame.draw.ellipse(surface, (200, 150, 150), (33, 15, 2, 2))
            pygame.draw.ellipse(surface, (200, 150, 150), (36, 15, 2, 2))
            # Eye
            pygame.draw.circle(surface, (255, 255, 255), (31, 11), 2)
            pygame.draw.circle(surface, (30, 30, 30), (31, 11), 1)
            # Legs
            pygame.draw.rect(surface, (255, 255, 255), (8, 28, 4, 6))
            pygame.draw.rect(surface, (255, 255, 255), (14, 28, 4, 6))
            pygame.draw.rect(surface, (255, 255, 255), (22, 28, 4, 6))
            pygame.draw.rect(surface, (255, 255, 255), (28, 28, 4, 6))
            # Hooves
            pygame.draw.rect(surface, (60, 50, 40), (8, 32, 4, 2))
            pygame.draw.rect(surface, (60, 50, 40), (14, 32, 4, 2))
            pygame.draw.rect(surface, (60, 50, 40), (22, 32, 4, 2))
            pygame.draw.rect(surface, (60, 50, 40), (28, 32, 4, 2))
        
        elif self.item_type == ItemType.EGG:
            # Draw egg icon
            # Egg shadow
            pygame.draw.ellipse(surface, (30, 30, 30), (12, 26, 16, 6))
            # Egg body (oval, cream colored)
            pygame.draw.ellipse(surface, (255, 250, 240), (10, 10, 20, 24))
            # Egg highlight
            pygame.draw.ellipse(surface, (255, 255, 255), (14, 12, 8, 10))
            # Subtle speckles
            pygame.draw.circle(surface, (240, 235, 220), (16, 20), 1)
            pygame.draw.circle(surface, (240, 235, 220), (22, 24), 1)
            pygame.draw.circle(surface, (240, 235, 220), (18, 28), 1)
            
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
        elif self.item_type == ItemType.CARROT_SEED:
            # Shadow
            pygame.draw.ellipse(screen, (30, 30, 30), (x - 6, y + 6, 12, 4))
            # Carrot seed packet
            pygame.draw.rect(screen, (210, 170, 130), (x - 8, y - 10, 16, 20), border_radius=2)
            pygame.draw.rect(screen, (240, 140, 40), (x - 6, y - 8, 12, 6))
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
        elif self.item_type == ItemType.CARROT:
            # Shadow
            pygame.draw.ellipse(screen, (30, 30, 30), (x - 6, y + 6, 12, 4))
            # Carrot body
            pygame.draw.polygon(screen, (240, 140, 40), [(x, y - 10), (x + 8, y + 10), (x - 8, y + 10)])
            # Leafy top
            pygame.draw.line(screen, (60, 180, 60), (x, y - 12), (x - 4, y - 4), 2)
            pygame.draw.line(screen, (60, 180, 60), (x, y - 12), (x, y - 4), 2)
            pygame.draw.line(screen, (60, 180, 60), (x, y - 12), (x + 4, y - 4), 2)
        elif self.item_type == ItemType.STONE:
            # Shadow
            pygame.draw.ellipse(screen, (30, 30, 30), (x - 6, y + 4, 12, 5))
            # Small stone
            pygame.draw.ellipse(screen, (130, 130, 130), (x - 6, y - 4, 12, 8))
            pygame.draw.ellipse(screen, (160, 160, 160), (x - 4, y - 3, 6, 4))
        elif self.item_type == ItemType.EGG:
            # Shadow
            pygame.draw.ellipse(screen, (30, 30, 30), (x - 6, y + 6, 12, 4))
            # Egg body
            pygame.draw.ellipse(screen, (255, 250, 240), (x - 6, y - 8, 12, 16))
            # Egg highlight
            pygame.draw.ellipse(screen, (255, 255, 255), (x - 4, y - 6, 5, 6))

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
            # Draw wooden sword
            # Handle
            pygame.draw.rect(surface, (139, 69, 19), (16, 28, 8, 10))
            # Guard
            pygame.draw.rect(surface, (100, 80, 50), (8, 24, 24, 4))
            # Blade (wooden color)
            pygame.draw.polygon(surface, (180, 140, 100), [
                (18, 24), (22, 24), (23, 4), (17, 4)
            ])
            # Blade edge
            pygame.draw.line(surface, (200, 160, 120), (22, 24), (23, 4), 1)
            
        elif self.tool_type == ToolType.IRON_SWORD:
            # Draw iron sword
            # Handle
            pygame.draw.rect(surface, (80, 60, 40), (16, 28, 8, 10))
            # Guard
            pygame.draw.rect(surface, (180, 180, 180), (8, 24, 24, 4))
            # Blade (iron gray)
            pygame.draw.polygon(surface, (200, 200, 210), [
                (18, 24), (22, 24), (23, 4), (17, 4)
            ])
            # Blade edge
            pygame.draw.line(surface, (240, 240, 250), (22, 24), (23, 4), 1)
            
        elif self.tool_type == ToolType.GOLDEN_SWORD:
            # Draw golden sword
            # Handle
            pygame.draw.rect(surface, (139, 69, 19), (16, 28, 8, 10))
            # Guard
            pygame.draw.rect(surface, (255, 215, 0), (8, 24, 24, 4))
            # Blade (golden)
            pygame.draw.polygon(surface, (255, 200, 50), [
                (18, 24), (22, 24), (23, 4), (17, 4)
            ])
            # Blade edge
            pygame.draw.line(surface, (255, 240, 150), (22, 24), (23, 4), 1)
            # Sparkle
            pygame.draw.circle(surface, (255, 255, 200), (20, 12), 2)
            
        elif self.tool_type == ToolType.DIAMOND_SWORD:
            # Draw diamond sword
            # Handle
            pygame.draw.rect(surface, (60, 50, 40), (16, 28, 8, 10))
            # Guard
            pygame.draw.rect(surface, (100, 200, 255), (8, 24, 24, 4))
            # Blade (diamond blue)
            pygame.draw.polygon(surface, (150, 220, 255), [
                (18, 24), (22, 24), (23, 4), (17, 4)
            ])
            # Blade edge
            pygame.draw.line(surface, (200, 240, 255), (22, 24), (23, 4), 1)
            # Sparkle
            pygame.draw.circle(surface, (255, 255, 255), (20, 10), 3)
            pygame.draw.circle(surface, (150, 220, 255), (20, 10), 2)
            
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
                     direction: str, tool_angle: float = 0):
        """Draw the tool as if held by the farmer at the specified angle"""
        import math
        
        # The tool_angle is now the absolute angle the tool should be drawn at
        # 0 degrees = pointing right, 90 = down, 180 = left, -90 = up
        
        if self.tool_type in [ToolType.SWORD, ToolType.IRON_SWORD, ToolType.GOLDEN_SWORD, ToolType.DIAMOND_SWORD]:
            self._draw_sword_new(screen, x, y, tool_angle)
        elif self.tool_type == ToolType.HOE:
            self._draw_hoe_new(screen, x, y, tool_angle)
        elif self.tool_type == ToolType.AXE:
            self._draw_axe_new(screen, x, y, tool_angle)
        elif self.tool_type == ToolType.HAMMER:
            self._draw_hammer_new(screen, x, y, tool_angle)
    
    def _draw_sword(self, screen, x, y, direction, angle):
        import math
        # Enhanced sword swing animation - more realistic sweeping motion
        length = 32  # Longer blade
        
        # Get sword colors based on type
        if self.tool_type == ToolType.SWORD:
            blade_color = (180, 140, 100)  # Wooden
            blade_edge = (200, 160, 120)
            guard_color = (100, 80, 50)
            handle_color = (139, 69, 19)
        elif self.tool_type == ToolType.IRON_SWORD:
            blade_color = (200, 200, 210)  # Iron gray
            blade_edge = (240, 240, 250)
            guard_color = (180, 180, 180)
            handle_color = (80, 60, 40)
        elif self.tool_type == ToolType.GOLDEN_SWORD:
            blade_color = (255, 200, 50)  # Golden
            blade_edge = (255, 240, 150)
            guard_color = (255, 215, 0)
            handle_color = (139, 69, 19)
        elif self.tool_type == ToolType.DIAMOND_SWORD:
            blade_color = (150, 220, 255)  # Diamond blue
            blade_edge = (200, 240, 255)
            guard_color = (100, 200, 255)
            handle_color = (60, 50, 40)
        else:
            blade_color = (180, 180, 200)
            blade_edge = (220, 220, 240)
            guard_color = (160, 140, 100)
            handle_color = (139, 69, 19)
        
        # Base angle depends on swing animation
        # Swing goes from raised position to slash
        if angle > 0:
            # During swing: start from raised (-60), slash through (to +60)
            swing_progress = angle / 60.0  # 0 to 1
            base_angle = -60 + (swing_progress * 120)  # -60 to +60
        else:
            base_angle = -45  # Resting position
        
        # Adjust angle based on direction
        if direction == 'down':
            rad = math.radians(base_angle + 90)
        elif direction == 'up':
            rad = math.radians(base_angle - 90)
        elif direction == 'left':
            rad = math.radians(base_angle + 180)
        else:  # right
            rad = math.radians(base_angle)
        
        # Calculate blade end position
        end_x = x + int(math.cos(rad) * length)
        end_y = y + int(math.sin(rad) * length)
        
        # Draw blade with gradient effect
        # Main blade
        pygame.draw.line(screen, blade_color, (x, y), (end_x, end_y), 5)
        # Blade edge (brighter)
        edge_offset = 2
        edge_x = x + int(math.cos(rad + 0.1) * length)
        edge_y = y + int(math.sin(rad + 0.1) * length)
        pygame.draw.line(screen, blade_edge, (x, y), (edge_x, edge_y), 2)
        
        # Blade tip
        pygame.draw.circle(screen, blade_edge, (end_x, end_y), 3)
        
        # Guard (cross guard)
        perp_x = int(math.cos(rad + 1.57) * 10)
        perp_y = int(math.sin(rad + 1.57) * 10)
        pygame.draw.line(screen, guard_color, 
                        (x - perp_x, y - perp_y), (x + perp_x, y + perp_y), 4)
        # Guard details
        pygame.draw.circle(screen, guard_color, (x - perp_x, y - perp_y), 3)
        pygame.draw.circle(screen, guard_color, (x + perp_x, y + perp_y), 3)
        
        # Handle
        handle_end_x = x - int(math.cos(rad) * 12)
        handle_end_y = y - int(math.sin(rad) * 12)
        pygame.draw.line(screen, handle_color, (x, y), (handle_end_x, handle_end_y), 5)
        # Handle wrap
        for i in range(3):
            wrap_pos = 0.3 + i * 0.25
            wrap_x = x - int(math.cos(rad) * 12 * wrap_pos)
            wrap_y = y - int(math.sin(rad) * 12 * wrap_pos)
            pygame.draw.circle(screen, (80, 50, 25), (wrap_x, wrap_y), 3)
        
        # Pommel
        pygame.draw.circle(screen, guard_color, (handle_end_x, handle_end_y), 4)
        
        # Swing trail effect (motion blur during swing)
        if angle > 20:
            trail_alpha = int((angle / 60.0) * 100)
            trail_surf = pygame.Surface((length * 2, length * 2), pygame.SRCALPHA)
            for i in range(3):
                trail_angle = base_angle - (i * 15)
                trail_rad = math.radians(trail_angle + {'down': 90, 'up': -90, 'left': 180, 'right': 0}.get(direction, 0))
                trail_end_x = length + int(math.cos(trail_rad) * (length - 5))
                trail_end_y = length + int(math.sin(trail_rad) * (length - 5))
                a = max(0, trail_alpha - i * 30)
                pygame.draw.line(trail_surf, (*blade_color[:3], a), 
                               (length, length), (trail_end_x, trail_end_y), 3 - i)
            screen.blit(trail_surf, (x - length, y - length))
    
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
    
    def _draw_sword_new(self, screen, x, y, angle):
        """Draw sword with absolute angle - more realistic"""
        import math
        
        # Get sword colors based on type
        if self.tool_type == ToolType.SWORD:
            blade_color = (180, 140, 100)  # Wooden
            blade_edge = (200, 160, 120)
            guard_color = (100, 80, 50)
            handle_color = (139, 69, 19)
        elif self.tool_type == ToolType.IRON_SWORD:
            blade_color = (200, 200, 210)  # Iron gray
            blade_edge = (240, 240, 250)
            guard_color = (180, 180, 180)
            handle_color = (80, 60, 40)
        elif self.tool_type == ToolType.GOLDEN_SWORD:
            blade_color = (255, 200, 50)  # Golden
            blade_edge = (255, 240, 150)
            guard_color = (255, 215, 0)
            handle_color = (139, 69, 19)
        elif self.tool_type == ToolType.DIAMOND_SWORD:
            blade_color = (150, 220, 255)  # Diamond blue
            blade_edge = (200, 240, 255)
            guard_color = (100, 200, 255)
            handle_color = (60, 50, 40)
        else:
            blade_color = (180, 180, 200)
            blade_edge = (220, 220, 240)
            guard_color = (160, 140, 100)
            handle_color = (139, 69, 19)
        
        rad = math.radians(angle)
        
        # Handle (held part) - extends behind hand
        handle_length = 10
        handle_end_x = x - int(math.cos(rad) * handle_length)
        handle_end_y = y - int(math.sin(rad) * handle_length)
        pygame.draw.line(screen, handle_color, (x, y), (handle_end_x, handle_end_y), 5)
        
        # Handle wrap details
        for i in range(3):
            wrap_dist = 3 + i * 3
            wrap_x = x - int(math.cos(rad) * wrap_dist)
            wrap_y = y - int(math.sin(rad) * wrap_dist)
            pygame.draw.circle(screen, (100, 60, 30), (wrap_x, wrap_y), 3)
        
        # Pommel
        pygame.draw.circle(screen, guard_color, (handle_end_x, handle_end_y), 4)
        
        # Guard (cross guard) - perpendicular to blade
        perp_angle = rad + math.pi / 2
        guard_x1 = x + int(math.cos(perp_angle) * 10)
        guard_y1 = y + int(math.sin(perp_angle) * 10)
        guard_x2 = x - int(math.cos(perp_angle) * 10)
        guard_y2 = y - int(math.sin(perp_angle) * 10)
        pygame.draw.line(screen, guard_color, (guard_x1, guard_y1), (guard_x2, guard_y2), 5)
        pygame.draw.circle(screen, guard_color, (guard_x1, guard_y1), 3)
        pygame.draw.circle(screen, guard_color, (guard_x2, guard_y2), 3)
        
        # Blade - extends from guard
        blade_length = 28
        blade_start_x = x + int(math.cos(rad) * 3)
        blade_start_y = y + int(math.sin(rad) * 3)
        blade_end_x = blade_start_x + int(math.cos(rad) * blade_length)
        blade_end_y = blade_start_y + int(math.sin(rad) * blade_length)
        
        # Main blade
        pygame.draw.line(screen, blade_color, (blade_start_x, blade_start_y), 
                        (blade_end_x, blade_end_y), 5)
        
        # Blade edge (brighter)
        edge_offset_x = int(math.cos(perp_angle) * 1.5)
        edge_offset_y = int(math.sin(perp_angle) * 1.5)
        pygame.draw.line(screen, blade_edge, 
                        (blade_start_x + edge_offset_x, blade_start_y + edge_offset_y),
                        (blade_end_x + edge_offset_x, blade_end_y + edge_offset_y), 2)
        
        # Blade tip
        pygame.draw.circle(screen, blade_edge, (blade_end_x, blade_end_y), 3)
    
    def _draw_hoe_new(self, screen, x, y, angle):
        """Draw hoe with absolute angle"""
        import math
        
        rad = math.radians(angle)
        perp_angle = rad + math.pi / 2
        
        # Handle
        handle_length = 22
        handle_end_x = x - int(math.cos(rad) * handle_length)
        handle_end_y = y - int(math.sin(rad) * handle_length)
        pygame.draw.line(screen, (160, 82, 45), (x, y), (handle_end_x, handle_end_y), 4)
        
        # Metal blade head - perpendicular to handle at the end
        head_x = x + int(math.cos(rad) * 4)
        head_y = y + int(math.sin(rad) * 4)
        
        blade_width = 12
        blade_x1 = head_x + int(math.cos(perp_angle) * blade_width)
        blade_y1 = head_y + int(math.sin(perp_angle) * blade_width)
        blade_x2 = head_x - int(math.cos(perp_angle) * blade_width)
        blade_y2 = head_y - int(math.sin(perp_angle) * blade_width)
        
        # Draw blade
        pygame.draw.polygon(screen, (120, 120, 130), [
            (head_x, head_y), (blade_x1, blade_y1), (blade_x2, blade_y2)
        ])
        # Blade edge
        pygame.draw.line(screen, (200, 200, 200), (blade_x1, blade_y1), (blade_x2, blade_y2), 2)
    
    def _draw_axe_new(self, screen, x, y, angle):
        """Draw axe with absolute angle"""
        import math
        
        rad = math.radians(angle)
        perp_angle = rad + math.pi / 2
        
        # Handle
        handle_length = 20
        handle_end_x = x - int(math.cos(rad) * handle_length)
        handle_end_y = y - int(math.sin(rad) * handle_length)
        pygame.draw.line(screen, (160, 82, 45), (x, y), (handle_end_x, handle_end_y), 5)
        
        # Axe head at the front
        head_x = x + int(math.cos(rad) * 5)
        head_y = y + int(math.sin(rad) * 5)
        
        # Axe head extends perpendicular
        back_x = head_x + int(math.cos(perp_angle) * 4)
        back_y = head_y + int(math.sin(perp_angle) * 4)
        blade_x = head_x - int(math.cos(perp_angle) * 10)
        blade_y = head_y - int(math.sin(perp_angle) * 10)
        
        # Draw axe head
        pygame.draw.polygon(screen, (140, 140, 150), [
            (back_x - 3, back_y - 3), (back_x + 3, back_y + 3),
            (blade_x + 2, blade_y + 2), (blade_x - 2, blade_y - 2)
        ])
        # Blade edge
        pygame.draw.line(screen, (220, 220, 220), 
                        (blade_x - 2, blade_y - 2), (blade_x + 2, blade_y + 2), 3)
    
    def _draw_hammer_new(self, screen, x, y, angle):
        """Draw hammer with absolute angle"""
        import math
        
        rad = math.radians(angle)
        perp_angle = rad + math.pi / 2
        
        # Handle
        handle_length = 16
        handle_end_x = x - int(math.cos(rad) * handle_length)
        handle_end_y = y - int(math.sin(rad) * handle_length)
        pygame.draw.line(screen, (160, 82, 45), (x, y), (handle_end_x, handle_end_y), 5)
        
        # Hammer head at front
        head_x = x + int(math.cos(rad) * 4)
        head_y = y + int(math.sin(rad) * 4)
        
        # Head extends perpendicular
        head_width = 10
        head_x1 = head_x + int(math.cos(perp_angle) * head_width)
        head_y1 = head_y + int(math.sin(perp_angle) * head_width)
        head_x2 = head_x - int(math.cos(perp_angle) * head_width)
        head_y2 = head_y - int(math.sin(perp_angle) * head_width)
        
        # Draw head
        pygame.draw.line(screen, (80, 80, 90), 
                        (head_x1, head_y1), (head_x2, head_y2), 8)
        # Faces
        pygame.draw.circle(screen, (180, 180, 190), (head_x1, head_y1), 4)
        pygame.draw.circle(screen, (180, 180, 190), (head_x2, head_y2), 4)


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

    def _create_tool_from_type(self, tool_type: ToolType) -> Tool:
        """Create a tool instance based on tool type."""
        tool_names = {
            ToolType.SWORD: "Sword",
            ToolType.HOE: "Hoe",
            ToolType.AXE: "Axe",
            ToolType.HAMMER: "Hammer"
        }
        return Tool(tool_type, tool_names.get(tool_type, "Tool"))
    
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

    def add_stone(self, quantity: int = 1) -> bool:
        """Add stone to inventory. Returns True if successful."""
        # Try to stack with existing stone in slots 4+
        for i in range(4, 10):
            if isinstance(self.slots[i], Item) and self.slots[i].item_type == ItemType.STONE:
                self.slots[i].quantity += quantity
                return True
        
        # Find empty slot for new stone
        for i in range(4, 10):
            if self.slots[i] is None:
                self.slots[i] = Item(ItemType.STONE, quantity)
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
    
    def get_slot_at_position(self, mouse_pos: tuple, inventory_rect: pygame.Rect) -> Optional[int]:
        """Get the slot index at the given mouse position, or None if not hovering."""
        x, y = mouse_pos
        
        if not inventory_rect.collidepoint(x, y):
            return None
        
        slot_total_width = self.slot_size + self.slot_spacing
        
        for i in range(len(self.slots)):
            slot_x = inventory_rect.x + i * slot_total_width
            slot_rect = pygame.Rect(slot_x, inventory_rect.y, self.slot_size, self.slot_size)
            if slot_rect.collidepoint(x, y):
                return i
        
        return None
    
    def get_slot_rects(self, x: int, y: int) -> List[pygame.Rect]:
        """Get list of slot rectangles for the inventory bar at given position"""
        slot_rects = []
        for i in range(len(self.slots)):
            slot_x = x + i * (self.slot_size + self.slot_spacing)
            slot_rect = pygame.Rect(slot_x, y, self.slot_size, self.slot_size)
            slot_rects.append(slot_rect)
        return slot_rects
    
    def draw(self, screen: pygame.Surface, x: int, y: int, mouse_pos: tuple = None):
        """Draw the inventory bar at the specified position. If mouse_pos is provided, show tooltip on hover."""
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
        hovered_slot = None
        if mouse_pos:
            hovered_slot = self.get_slot_at_position(mouse_pos, panel_rect)
        
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
            
            # Highlight hovered slot
            if i == hovered_slot and slot_content:
                pygame.draw.rect(screen, (150, 150, 170), slot_rect, 2, border_radius=5)
            
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
            
            # Draw slot number (1-9, then 0 for slot 9)
            font = pygame.font.SysFont('Arial', 12)
            slot_number = i + 1 if i < 9 else 0  # 1-9 for first 9 slots, 0 for last slot
            number_text = font.render(str(slot_number), True, (180, 180, 180))
            screen.blit(number_text, (slot_x + 3, y + 2))
        
        # Draw tooltip for hovered item
        if hovered_slot is not None and self.slots[hovered_slot]:
            self._draw_tooltip(screen, mouse_pos, self.slots[hovered_slot])
        
        return panel_rect
    
    def _draw_tooltip(self, screen: pygame.Surface, mouse_pos: tuple, slot_content):
        """Draw a tooltip for the hovered item"""
        font = pygame.font.SysFont('Arial', 14)
        small_font = pygame.font.SysFont('Arial', 12)
        
        # Get item name and description
        if isinstance(slot_content, Tool):
            name = slot_content.name
            desc = "A tool for farming"
            extra_lines = []
            
            # Add damage info for swords
            if slot_content.tool_type in [ToolType.SWORD, ToolType.IRON_SWORD, ToolType.GOLDEN_SWORD, ToolType.DIAMOND_SWORD]:
                damage = SWORD_DAMAGE.get(slot_content.tool_type, 1)
                desc = "A weapon for combat"
                extra_lines.append(f"Damage: {damage}")
                # Add extra info about damage effectiveness
                if damage == 1:
                    extra_lines.append("5 hits to kill brute")
                elif damage == 2:
                    extra_lines.append("3 hits to kill brute")
                elif damage == 3:
                    extra_lines.append("2 hits to kill brute")
                elif damage >= 5:
                    extra_lines.append("Instant kill brute!")
        elif isinstance(slot_content, Item):
            name = slot_content.item_type.value.replace('_', ' ').title()
            # Item descriptions
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
                ItemType.EGG: "Fresh egg from chicken",
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
            name = "Unknown"
            desc = ""
            extra_lines = []
        
        # Calculate tooltip dimensions
        name_surface = font.render(name, True, (255, 255, 255))
        desc_surface = font.render(desc, True, (200, 200, 200))
        
        # Calculate width based on longest line
        max_width = max(name_surface.get_width(), desc_surface.get_width())
        for line in extra_lines:
            line_surface = small_font.render(line, True, (150, 255, 150))
            max_width = max(max_width, line_surface.get_width())
        
        tooltip_width = max_width + 20
        tooltip_height = 50 + len(extra_lines) * 18  # Extra height for growth time lines
        
        # Position tooltip near mouse
        tooltip_x = mouse_pos[0] + 15
        tooltip_y = mouse_pos[1] - tooltip_height - 5
        
        # Keep tooltip on screen
        if tooltip_x + tooltip_width > screen.get_width():
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


# Need to import math at module level
import math