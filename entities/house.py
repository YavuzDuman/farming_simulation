"""
House Entity - 3D Farm House with stone path entrance
"""
import pygame
from typing import Tuple, List
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    HOUSE_WALL, HOUSE_ROOF, HOUSE_DOOR, HOUSE_WINDOW,
    GRID_SIZE, GRID_OFFSET_X, GRID_OFFSET_Y
)


class House:
    """A 3D-looking farm house with stone path entrance"""
    
    def __init__(self, grid_col: int, grid_row: int, grid_offset_x: int, grid_offset_y: int):
        # Grid position
        self.grid_col = grid_col
        self.grid_row = grid_row
        
        # Calculate pixel position (center of the house base)
        self.x = grid_offset_x + grid_col * GRID_SIZE + (GRID_SIZE * 5) // 2  # Center of 5-wide house
        self.y = grid_offset_y + grid_row * GRID_SIZE + GRID_SIZE  # Bottom of house
        
        # House dimensions (in grid cells)
        self.cells_wide = 5
        self.cells_tall = 3
        self.width = GRID_SIZE * self.cells_wide
        self.height = GRID_SIZE * self.cells_tall
        
        # 3D depth offset
        self.depth_3d = 15
        
        # Components
        self.wall_height = int(self.height * 0.55)
        self.roof_height = int(self.height * 0.45)
        self.door_width = 32
        self.door_height = 48
        
        # Collision rect (the base of the house - full width)
        self.collision_rect = pygame.Rect(
            grid_offset_x + grid_col * GRID_SIZE,
            grid_offset_y + grid_row * GRID_SIZE,
            self.width,
            GRID_SIZE * 2  # 2 cells deep for collision
        )
        
        # Stone path (grid cells in front of door)
        # Centered with door at col + 2 for a 5-wide house
        self.path_cells = [
            (grid_col + 2, grid_row + 1),  # Starts at the door cell (bottom part of house)
            (grid_col + 2, grid_row + 2),  # Directly in front
            (grid_col + 2, grid_row + 3),  # One more
            (grid_col + 2, grid_row + 4),  # And another
        ]
        self.path_rects = []
        for col, row in self.path_cells:
            self.path_rects.append(pygame.Rect(
                grid_offset_x + col * GRID_SIZE,
                grid_offset_y + row * GRID_SIZE,
                GRID_SIZE, GRID_SIZE
            ))
    
    @property
    def sort_y(self) -> int:
        """Y position for depth sorting (front of house)"""
        return self.y
    
    def get_collision_rect(self) -> pygame.Rect:
        """Get collision rectangle"""
        return self.collision_rect
    
    def collides_with(self, rect: pygame.Rect) -> bool:
        """Check if rectangle collides with house"""
        return self.collision_rect.colliderect(rect)
    
    def draw_stone_path(self, screen: pygame.Surface):
        """Draw the stone path leading to the house entrance"""
        stone_colors = [
            (140, 140, 140), (130, 130, 130), (150, 150, 150),
            (125, 125, 125), (145, 145, 145), (135, 135, 135)
        ]
        
        for rect in self.path_rects:
            # Draw stone tile background
            pygame.draw.rect(screen, (120, 115, 110), rect)
            
            # Draw individual stones
            stone_size = 12
            for row in range(3):
                for col in range(3):
                    stone_x = rect.x + col * 14 + 4
                    stone_y = rect.y + row * 14 + 4
                    color = stone_colors[(row * 3 + col) % len(stone_colors)]
                    
                    # Stone with 3D effect
                    pygame.draw.ellipse(screen, (color[0]-20, color[1]-20, color[2]-20),
                                       (stone_x + 1, stone_y + 1, stone_size, stone_size - 2))
                    pygame.draw.ellipse(screen, color,
                                       (stone_x, stone_y, stone_size, stone_size - 2))
                    pygame.draw.ellipse(screen, (color[0]+20, color[1]+20, color[2]+20),
                                       (stone_x + 1, stone_y + 1, stone_size - 4, stone_size - 6))
            
            # Border
            pygame.draw.rect(screen, (80, 75, 70), rect, 1)
    
    def draw(self, screen: pygame.Surface):
        """Draw the 3D house"""
        # First draw the stone path
        self.draw_stone_path(screen)
        
        # Calculate positions
        left_x = self.x - self.width // 2
        right_x = self.x + self.width // 2
        top_y = self.y - self.height
        wall_top = top_y + self.roof_height
        wall_bottom = self.y
        
        # === SHADOW ===
        shadow_points = [
            (left_x - 10, wall_bottom),
            (right_x + 10, wall_bottom),
            (right_x + 20, wall_bottom + 15),
            (left_x, wall_bottom + 15)
        ]
        pygame.draw.polygon(screen, (30, 30, 30), shadow_points)
        
        # === 3D RIGHT WALL (visible side) ===
        side_wall_points = [
            (right_x, wall_top),
            (right_x + self.depth_3d, wall_top - self.depth_3d // 2),
            (right_x + self.depth_3d, wall_bottom - self.depth_3d // 2),
            (right_x, wall_bottom)
        ]
        pygame.draw.polygon(screen, (200, 170, 130), side_wall_points)
        pygame.draw.polygon(screen, (160, 130, 100), side_wall_points, 2)
        
        # === 3D RIGHT ROOF ===
        roof_peak = (self.x, top_y)
        side_roof_points = [
            (right_x, wall_top),
            (right_x + self.depth_3d, wall_top - self.depth_3d // 2),
            (self.x + self.depth_3d // 2, top_y - self.depth_3d // 3),
            roof_peak
        ]
        pygame.draw.polygon(screen, (180, 90, 50), side_roof_points)
        pygame.draw.polygon(screen, (140, 70, 40), side_roof_points, 2)
        
        # === MAIN WALLS (front) ===
        wall_rect = pygame.Rect(left_x, wall_top, self.width, self.wall_height)
        
        # Wall shadow (3D effect)
        pygame.draw.rect(screen, (200, 175, 135), 
                        (left_x + 3, wall_top + 3, self.width, self.wall_height))
        # Main wall
        pygame.draw.rect(screen, (230, 200, 160), wall_rect)
        
        # Wall texture (horizontal wood planks)
        for i in range(0, self.wall_height, 10):
            pygame.draw.line(screen, (210, 180, 140),
                           (left_x, wall_top + i),
                           (right_x, wall_top + i), 1)
        
        # Wall border
        pygame.draw.rect(screen, (180, 150, 120), wall_rect, 2)
        
        # === MAIN ROOF (front) ===
        roof_points = [
            (left_x - 15, wall_top),
            (self.x, top_y),
            (right_x + 5, wall_top)
        ]
        pygame.draw.polygon(screen, (200, 100, 60), roof_points)
        
        # Roof tile lines
        for i in range(6):
            y_pos = top_y + int((wall_top - top_y) * i / 6)
            width_at_y = int((self.width + 20) * (1 - i / 6))
            pygame.draw.line(screen, (170, 85, 50),
                           (self.x - width_at_y // 2, y_pos),
                           (self.x + width_at_y // 2, y_pos), 2)
        
        # Roof border
        pygame.draw.polygon(screen, (150, 75, 45), roof_points, 3)
        
        # === DOOR ===
        door_x = self.x - self.door_width // 2
        door_y = wall_bottom - self.door_height
        
        # Door shadow
        pygame.draw.rect(screen, (100, 70, 40),
                        (door_x + 2, door_y + 2, self.door_width, self.door_height))
        # Door
        pygame.draw.rect(screen, (120, 70, 40),
                        (door_x, door_y, self.door_width, self.door_height))
        
        # Door frame
        pygame.draw.rect(screen, (80, 50, 30),
                        (door_x - 3, door_y - 3, self.door_width + 6, self.door_height + 3), 3)
        
        # Door arch
        pygame.draw.arc(screen, (80, 50, 30),
                       (door_x - 3, door_y - 15, self.door_width + 6, 30),
                       0, 3.14, 3)
        
        # Door panels
        pygame.draw.rect(screen, (100, 60, 35),
                        (door_x + 4, door_y + 5, self.door_width - 8, self.door_height // 2 - 5), 2)
        pygame.draw.rect(screen, (100, 60, 35),
                        (door_x + 4, door_y + self.door_height // 2 + 3, self.door_width - 8, self.door_height // 2 - 8), 2)
        
        # Door knob
        pygame.draw.circle(screen, (255, 200, 50),
                          (door_x + self.door_width - 7, door_y + self.door_height // 2), 4)
        pygame.draw.circle(screen, (200, 150, 30),
                          (door_x + self.door_width - 7, door_y + self.door_height // 2), 4, 1)
        
        # === WINDOWS ===
        window_width = 30
        window_height = 36
        window_y = wall_top + 15
        
        # Left window
        left_window_x = left_x + 30
        self._draw_window(screen, left_window_x, window_y, window_width, window_height)
        
        # Right window
        right_window_x = right_x - 30 - window_width
        self._draw_window(screen, right_window_x, window_y, window_width, window_height)
        
        # === CHIMNEY ===
        chimney_x = right_x - 40
        chimney_y = top_y + 20
        chimney_width = 24
        chimney_height = 50
        
        # Chimney shadow (3D)
        pygame.draw.rect(screen, (100, 50, 30),
                        (chimney_x + 3, chimney_y, chimney_width, chimney_height))
        # Chimney front
        pygame.draw.rect(screen, (140, 70, 45),
                        (chimney_x, chimney_y - 5, chimney_width, chimney_height))
        # Chimney top
        pygame.draw.rect(screen, (120, 60, 40),
                        (chimney_x - 2, chimney_y - 10, chimney_width + 4, 8))
        pygame.draw.rect(screen, (100, 50, 30),
                        (chimney_x, chimney_y, chimney_width, chimney_height), 2)
        
        # Smoke
        import math
        for i in range(3):
            smoke_x = chimney_x + chimney_width // 2 + int(math.sin(i + self.x * 0.01) * 5)
            smoke_y = chimney_y - 15 - i * 12
            smoke_size = 5 + i * 2
            alpha = 180 - i * 40
            pygame.draw.circle(screen, (200, 200, 200), (smoke_x, smoke_y), smoke_size)
    
    def _draw_window(self, screen: pygame.Surface, x: int, y: int, width: int, height: int):
        """Draw a single window with 3D effect"""
        # Window shadow
        pygame.draw.rect(screen, (60, 40, 20),
                        (x + 2, y + 2, width, height))
        
        # Window frame
        pygame.draw.rect(screen, (100, 60, 35),
                        (x - 2, y - 2, width + 4, height + 4))
        
        # Window glass (light blue)
        pygame.draw.rect(screen, (180, 210, 240), (x, y, width, height))
        
        # Window reflection
        pygame.draw.line(screen, (220, 240, 255),
                        (x + 2, y + 2), (x + width - 4, y + height // 3), 2)
        
        # Window cross bars
        pygame.draw.line(screen, (80, 50, 30),
                        (x + width // 2, y), (x + width // 2, y + height), 3)
        pygame.draw.line(screen, (80, 50, 30),
                        (x, y + height // 2), (x + width, y + height // 2), 3)
        
        # Shutters
        shutter_width = 8
        # Left shutter
        pygame.draw.rect(screen, (160, 80, 50),
                        (x - shutter_width - 4, y - 2, shutter_width, height + 4))
        pygame.draw.rect(screen, (120, 60, 40),
                        (x - shutter_width - 4, y - 2, shutter_width, height + 4), 2)
        # Right shutter
        pygame.draw.rect(screen, (160, 80, 50),
                        (x + width + 4, y - 2, shutter_width, height + 4))
        pygame.draw.rect(screen, (120, 60, 40),
                        (x + width + 4, y - 2, shutter_width, height + 4), 2)