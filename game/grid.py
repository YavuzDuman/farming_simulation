"""
Grid System - Manages the farm grid with grass texture
"""
import pygame
import random
from typing import Optional, Tuple, List
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    GRID_SIZE, GRID_COLS, GRID_ROWS, GRID_OFFSET_X, GRID_OFFSET_Y,
    GREEN, LIGHT_GREEN, DARK_GREEN, BROWN, LIGHT_BROWN, DARK_BROWN
)


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
        self.is_planted = False
        self.plant_type = None
        # Random grass variation for texture
        self.grass_variation = random.randint(0, 3)
        self.grass_blades = self._generate_grass_blades()
    
    def _generate_grass_blades(self) -> List[Tuple[int, int]]:
        """Generate random grass blade positions for texture"""
        blades = []
        for _ in range(5):
            bx = random.randint(4, self.width - 4)
            by = random.randint(4, self.height - 4)
            blades.append((bx, by))
        return blades
    
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
    
    def draw(self, screen: pygame.Surface):
        """Draw the cell with grass texture"""
        # Draw base
        pygame.draw.rect(screen, self.get_color(), self.rect)
        
        # Draw grass texture (small blades)
        if not self.is_tilled:
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
        pygame.draw.rect(screen, (20, 80, 20), self.rect, 1)
        
        # Draw selection highlight
        if self.is_selected:
            pygame.draw.rect(screen, (255, 255, 100), self.rect, 3)


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
    
    def handle_hover(self, mouse_pos: Tuple[int, int]):
        """Handle mouse hover over grid"""
        for row in self.cells:
            for cell in row:
                cell.is_hovered = cell.rect.collidepoint(mouse_pos)
    
    def handle_click(self, mouse_pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Handle mouse click on grid, returns selected cell coordinates"""
        clicked_cell = self.get_cell_at_position(*mouse_pos)
        if clicked_cell:
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