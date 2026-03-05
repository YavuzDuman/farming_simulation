"""
Grid System - Manages the farm grid with grass texture
"""
import pygame
import random
import time
from typing import Optional, Tuple, List
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    GRID_SIZE, GRID_COLS, GRID_ROWS, GRID_OFFSET_X, GRID_OFFSET_Y,
    GREEN, LIGHT_GREEN, DARK_GREEN, BROWN, LIGHT_BROWN, DARK_BROWN
)


class PlantState:
    """Enum for plant growth states"""
    EMPTY = 0
    SEED = 1      # Just planted
    SPROUT = 2    # Small sprout
    GROWN = 3     # Fully grown wheat


class PlantType:
    """Types of plants that can be grown"""
    WHEAT = "wheat"
    CARROT = "carrot"


class GridCell:
    """Represents a single cell in the farm grid"""
    
    def __init__(self, col: int, row: int, x: int, y: int):
        self.col = col
        self.row = row
        self.x = x
        self.y = y
        self.width = GRID_SIZE
        self.height = GRID_SIZE
        self.is_hovered = False
        self.is_selected = False
        self.is_tilled = False
        # Plant system
        self.plant_state = PlantState.EMPTY
        self.plant_type = PlantType.WHEAT
        self.plant_time = 0  # Time when seed was planted
        self.has_wheat_dropped = False  # Wheat on ground after harvest
        self.wheat_quantity = 0
        self.has_carrot_dropped = False  # Carrots on ground after harvest
        self.carrot_quantity = 0
        self.has_seed_dropped = False  # Seeds on ground after harvest
        self.seed_quantity = 0
        self.has_carrot_seed_dropped = False  # Carrot seeds on ground after harvest
        self.carrot_seed_quantity = 0
        # Random grass variation for texture
        self.grass_variation = random.randint(0, 3)
        self.grass_blades = self._generate_grass_blades()
        # Random soil variation for texture
        self.soil_variation = self._generate_soil_texture()
    
    def _generate_grass_blades(self) -> List[Tuple[int, int]]:
        """Generate random grass blade positions for texture"""
        blades = []
        for _ in range(5):
            bx = random.randint(4, self.width - 4)
            by = random.randint(4, self.height - 4)
            blades.append((bx, by))
        return blades

    def _generate_soil_texture(self) -> List[Tuple[int, int, int, int]]:
        """Generate random soil clods and pebbles for texture"""
        texture = []
        for _ in range(8):
            tx = random.randint(2, self.width - 6)
            ty = random.randint(2, self.height - 6)
            size = random.randint(2, 5)
            # 0: clod, 1: pebble, 2: crack
            type = random.randint(0, 2)
            texture.append((tx, ty, size, type))
        return texture
    
    @property
    def rect(self) -> pygame.Rect:
        """Get the rectangle for this cell"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    @property
    def center(self) -> Tuple[int, int]:
        """Get the center point of the cell"""
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    def get_base_color(self) -> Tuple[int, int, int]:
        """Get the base grass color with variation"""
        if self.is_tilled:
            return BROWN
        
        # Create grass variation
        variation = self.grass_variation
        if variation == 0:
            return (40, 150, 40)  # Slightly lighter
        elif variation == 1:
            return (30, 130, 30)  # Standard
        elif variation == 2:
            return (25, 120, 25)  # Slightly darker
        else:
            return (35, 140, 35)  # Medium
    
    def get_color(self) -> Tuple[int, int, int]:
        """Get the current color based on state"""
        if self.is_selected:
            if self.is_tilled:
                return DARK_BROWN
            return DARK_GREEN
        elif self.is_hovered:
            if self.is_tilled:
                return LIGHT_BROWN
            return LIGHT_GREEN
        else:
            return self.get_base_color()
    
    def update_plant(self, current_time: float):
        """Update plant growth based on time"""
        if self.plant_state == PlantState.SEED:
            # After 5 seconds, become sprout
            if current_time - self.plant_time >= 5:
                self.plant_state = PlantState.SPROUT
        elif self.plant_state == PlantState.SPROUT:
            # After growth duration, become grown
            if current_time - self.plant_time >= self._get_growth_duration():
                self.plant_state = PlantState.GROWN

    def _get_growth_duration(self) -> float:
        """Get growth duration based on plant type"""
        if self.plant_type == PlantType.CARROT:
            return 30.0
        return 30.0

    def plant_seed(self, plant_type: str = PlantType.WHEAT):
        """Plant a seed in this cell"""
        if self.is_tilled and self.plant_state == PlantState.EMPTY:
            self.plant_state = PlantState.SEED
            self.plant_type = plant_type
            self.plant_time = time.time()
            return True
        return False

    def harvest(self) -> int:
        """Harvest the grown plant. Returns harvest quantity."""
        if self.plant_state == PlantState.GROWN:
            self.plant_state = PlantState.EMPTY
            harvest_qty = random.randint(2, 4)
            if self.plant_type == PlantType.CARROT:
                self.has_carrot_dropped = True
                self.carrot_quantity = harvest_qty
                # Random chance to drop carrot seeds (20% chance)
                self.has_carrot_seed_dropped = random.random() < 0.2
                self.carrot_seed_quantity = 1 if self.has_carrot_seed_dropped else 0
            else:
                self.has_wheat_dropped = True
                self.wheat_quantity = harvest_qty
                # Random chance to drop wheat seeds (20% chance)
                self.has_seed_dropped = random.random() < 0.2
                self.seed_quantity = 1 if self.has_seed_dropped else 0
            return harvest_qty
        return 0

    def collect_wheat(self) -> int:
        """Collect wheat from ground. Returns quantity collected."""
        if self.has_wheat_dropped:
            qty = self.wheat_quantity
            self.has_wheat_dropped = False
            self.wheat_quantity = 0
            return qty
        return 0

    def collect_carrot(self) -> int:
        """Collect carrots from ground. Returns quantity collected."""
        if self.has_carrot_dropped:
            qty = self.carrot_quantity
            self.has_carrot_dropped = False
            self.carrot_quantity = 0
            return qty
        return 0

    def collect_seed(self) -> int:
        """Collect wheat seeds from ground. Returns quantity collected."""
        if self.has_seed_dropped:
            qty = self.seed_quantity
            self.has_seed_dropped = False
            self.seed_quantity = 0
            return qty
        return 0

    def collect_carrot_seed(self) -> int:
        """Collect carrot seeds from ground. Returns quantity collected."""
        if self.has_carrot_seed_dropped:
            qty = self.carrot_seed_quantity
            self.has_carrot_seed_dropped = False
            self.carrot_seed_quantity = 0
            return qty
        return 0

    def draw(self, screen: pygame.Surface):
        """Draw the cell with realistic texture"""
        # Draw base
        pygame.draw.rect(screen, self.get_color(), self.rect)
        
        if self.is_tilled:
            # Draw realistic soil texture
            soil_colors = [
                (100, 60, 30), (120, 80, 40), (80, 50, 20), (60, 40, 20)
            ]
            # Darker base spots for moisture/depth
            for tx, ty, size, type in self.soil_variation:
                pos_x = self.x + tx
                pos_y = self.y + ty
                color = soil_colors[type % len(soil_colors)]
                
                if type == 0: # Clod
                    pygame.draw.circle(screen, color, (pos_x, pos_y), size)
                elif type == 1: # Pebble
                    pygame.draw.rect(screen, (130, 130, 130), (pos_x, pos_y, size-1, size-1))
                else: # Crack/Detail
                    pygame.draw.line(screen, (50, 30, 10), (pos_x, pos_y), (pos_x + size, pos_y + size), 1)
            
            # Subtle ridges
            for i in range(2, self.width, 12):
                pygame.draw.line(screen, (90, 60, 30), 
                               (self.x + i, self.y + 2), 
                               (self.x + i + 2, self.y + self.height - 2), 1)
            
            # Draw plant if present
            self._draw_plant(screen)
        else:
            # Draw grass texture (small blades)
            for bx, by in self.grass_blades:
                blade_x = self.x + bx
                blade_y = self.y + by
                # Draw small grass blade
                pygame.draw.line(screen, (20, 100, 20), 
                               (blade_x, blade_y), 
                               (blade_x, blade_y - 3), 2)
                pygame.draw.line(screen, (50, 160, 50), 
                               (blade_x + 1, blade_y), 
                               (blade_x + 2, blade_y - 2), 1)
        
        # Draw subtle border
        border_color = (60, 40, 20) if self.is_tilled else (20, 80, 20)
        pygame.draw.rect(screen, border_color, self.rect, 1)
        
        # Draw selection highlight
        if self.is_selected:
            pygame.draw.rect(screen, (255, 255, 100), self.rect, 3)

    def _draw_plant(self, screen: pygame.Surface):
        """Draw the plant based on its state"""
        cx = self.x + self.width // 2
        cy = self.y + self.height // 2
        
        if self.plant_state == PlantState.SEED:
            # Small seed in soil
            pygame.draw.circle(screen, (100, 80, 40), (cx, cy + 8), 3)
            pygame.draw.circle(screen, (120, 100, 50), (cx - 1, cy + 7), 2)
            
        elif self.plant_state == PlantState.SPROUT:
            # Small green sprout
            # Stem
            pygame.draw.line(screen, (60, 180, 60), (cx, cy + 10), (cx, cy - 2), 3)
            # Leaves
            pygame.draw.ellipse(screen, (80, 200, 80), (cx - 6, cy - 4, 6, 4))
            pygame.draw.ellipse(screen, (80, 200, 80), (cx, cy - 4, 6, 4))
            # Leaf veins
            pygame.draw.line(screen, (40, 150, 40), (cx - 3, cy - 2), (cx - 5, cy - 4), 1)
            pygame.draw.line(screen, (40, 150, 40), (cx + 3, cy - 2), (cx + 5, cy - 4), 1)
            
        elif self.plant_state == PlantState.GROWN:
            if self.plant_type == PlantType.CARROT:
                # Fully grown carrots (leafy tops)
                for offset in [-5, 0, 5]:
                    stalk_x = cx + offset
                    # Leaves
                    pygame.draw.line(screen, (60, 180, 60),
                                   (stalk_x, cy + 10), (stalk_x - 4, cy - 6), 3)
                    pygame.draw.line(screen, (60, 180, 60),
                                   (stalk_x, cy + 10), (stalk_x, cy - 6), 3)
                    pygame.draw.line(screen, (60, 180, 60),
                                   (stalk_x, cy + 10), (stalk_x + 4, cy - 6), 3)
                    # Carrot tip peeking
                    pygame.draw.polygon(screen, (240, 140, 40),
                                      [(stalk_x, cy + 12), (stalk_x + 3, cy + 18), (stalk_x - 3, cy + 18)])
            else:
                # Fully grown wheat
                # Stalks
                for offset in [-4, 0, 4]:
                    stalk_x = cx + offset
                    # Main stalk
                    pygame.draw.line(screen, (200, 180, 100), 
                                   (stalk_x, cy + 12), (stalk_x, cy - 8), 2)
                    # Wheat head (golden)
                    pygame.draw.ellipse(screen, (218, 165, 32), 
                                      (stalk_x - 3, cy - 12, 6, 10))
                    # Wheat grains detail
                    for i in range(3):
                        grain_y = cy - 10 + i * 3
                        pygame.draw.line(screen, (184, 134, 11), 
                                       (stalk_x - 2, grain_y), (stalk_x + 2, grain_y), 1)
                    # Leaves
                    pygame.draw.line(screen, (100, 200, 100), 
                                   (stalk_x, cy + 5), (stalk_x - 5, cy + 12), 2)
                    pygame.draw.line(screen, (100, 200, 100), 
                                   (stalk_x, cy + 5), (stalk_x + 5, cy + 12), 2)
        
        # Draw dropped wheat on ground
        if self.has_wheat_dropped:
            self._draw_wheat_on_ground(screen, cx, cy)
        
        # Draw dropped carrots on ground
        if self.has_carrot_dropped:
            self._draw_carrot_on_ground(screen, cx, cy)
        
        # Draw dropped seeds on ground
        if self.has_seed_dropped:
            self._draw_seed_on_ground(screen, cx, cy)
        
        # Draw dropped carrot seeds on ground
        if self.has_carrot_seed_dropped:
            self._draw_carrot_seed_on_ground(screen, cx, cy)

    def _draw_seed_on_ground(self, screen: pygame.Surface, cx: int, cy: int):
        """Draw seed packet on the ground"""
        # Shadow
        pygame.draw.ellipse(screen, (30, 30, 30), (cx - 6, cy + 6, 12, 4))
        # Seed packet
        pygame.draw.rect(screen, (200, 180, 150), (cx - 8, cy - 4, 16, 14), border_radius=2)
        pygame.draw.rect(screen, (50, 150, 50), (cx - 6, cy - 2, 12, 5))

    def _draw_carrot_seed_on_ground(self, screen: pygame.Surface, cx: int, cy: int):
        """Draw carrot seed packet on the ground"""
        # Shadow
        pygame.draw.ellipse(screen, (30, 30, 30), (cx - 6, cy + 6, 12, 4))
        # Carrot seed packet
        pygame.draw.rect(screen, (210, 170, 130), (cx - 8, cy - 4, 16, 14), border_radius=2)
        pygame.draw.rect(screen, (240, 140, 40), (cx - 6, cy - 2, 12, 5))

    def _draw_carrot_on_ground(self, screen: pygame.Surface, cx: int, cy: int):
        """Draw carrots on the ground"""
        # Shadow
        pygame.draw.ellipse(screen, (30, 30, 30), (cx - 10, cy + 8, 20, 6))
        
        # Multiple carrots bundled together
        for i in range(self.carrot_quantity):
            offset_x = (i - self.carrot_quantity // 2) * 5
            # Carrot body
            pygame.draw.polygon(screen, (240, 140, 40),
                               [(cx + offset_x, cy - 8), (cx + offset_x + 6, cy + 10), (cx + offset_x - 6, cy + 10)])
            # Leaves
            pygame.draw.line(screen, (60, 180, 60), (cx + offset_x, cy - 10), (cx + offset_x - 3, cy - 4), 2)
            pygame.draw.line(screen, (60, 180, 60), (cx + offset_x, cy - 10), (cx + offset_x, cy - 4), 2)
            pygame.draw.line(screen, (60, 180, 60), (cx + offset_x, cy - 10), (cx + offset_x + 3, cy - 4), 2)

    def _draw_wheat_on_ground(self, screen: pygame.Surface, cx: int, cy: int):
        """Draw wheat bundle on the ground"""
        # Shadow
        pygame.draw.ellipse(screen, (30, 30, 30), (cx - 10, cy + 8, 20, 6))
        
        # Wheat bundle
        # Multiple wheat stalks bundled together
        for i in range(self.wheat_quantity):
            offset_x = (i - self.wheat_quantity // 2) * 6
            # Stalk
            pygame.draw.line(screen, (200, 180, 100), 
                           (cx + offset_x, cy + 10), (cx + offset_x, cy - 5), 2)
            # Head
            pygame.draw.ellipse(screen, (218, 165, 32), 
                              (cx + offset_x - 2, cy - 10, 4, 8))
            # Grains
            pygame.draw.line(screen, (184, 134, 11), 
                           (cx + offset_x - 2, cy - 8), (cx + offset_x + 2, cy - 8), 1)
            pygame.draw.line(screen, (184, 134, 11), 
                           (cx + offset_x - 2, cy - 5), (cx + offset_x + 2, cy - 5), 1)


class Grid:
    """Manages the entire farm grid"""
    
    def __init__(self):
        self.cells: List[List[GridCell]] = []
        self.selected_cell: Optional[Tuple[int, int]] = None
        self._initialize_grid()
    
    def _initialize_grid(self):
        """Create the grid cells"""
        self.cells = []
        for row in range(GRID_ROWS):
            row_cells = []
            for col in range(GRID_COLS):
                x = GRID_OFFSET_X + col * GRID_SIZE
                y = GRID_OFFSET_Y + row * GRID_SIZE
                cell = GridCell(col, row, x, y)
                row_cells.append(cell)
            self.cells.append(row_cells)
    
    def update(self, current_time: float):
        """Update all cells (for plant growth)"""
        for row in self.cells:
            for cell in row:
                cell.update_plant(current_time)
    
    def get_cell_at_position(self, x: int, y: int) -> Optional[GridCell]:
        """Get the cell at screen position"""
        for row in self.cells:
            for cell in row:
                if cell.rect.collidepoint(x, y):
                    return cell
        return None
    
    def get_cell(self, col: int, row: int) -> Optional[GridCell]:
        """Get cell at specific grid coordinates"""
        if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
            return self.cells[row][col]
        return None
    
    def handle_hover(self, mouse_pos: Tuple[int, int], allowed_coords: Optional[set] = None):
        """Handle mouse hover over grid"""
        for row in self.cells:
            for cell in row:
                is_hovered = cell.rect.collidepoint(mouse_pos)
                if allowed_coords is not None:
                    is_hovered = is_hovered and (cell.col, cell.row) in allowed_coords
                cell.is_hovered = is_hovered
    
    def handle_click(self, mouse_pos: Tuple[int, int], allowed_coords: Optional[set] = None) -> Optional[Tuple[int, int]]:
        """Handle mouse click on grid, returns selected cell coordinates"""
        clicked_cell = self.get_cell_at_position(*mouse_pos)
        if clicked_cell:
            if allowed_coords is not None and (clicked_cell.col, clicked_cell.row) not in allowed_coords:
                return None

            # Deselect previous cell
            if self.selected_cell:
                prev_col, prev_row = self.selected_cell
                self.cells[prev_row][prev_col].is_selected = False
            
            # Select new cell
            clicked_cell.is_selected = True
            self.selected_cell = (clicked_cell.col, clicked_cell.row)
            return self.selected_cell
        return None
    
    def draw(self, screen: pygame.Surface):
        """Draw all grid cells"""
        for row in self.cells:
            for cell in row:
                cell.draw(screen)