"""
Fence Entity - A fence that creates enclosed areas for animals
"""
import pygame
from typing import Tuple, List, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    GRID_SIZE, GRID_OFFSET_X, GRID_OFFSET_Y
)


class Fence:
    """A fence segment that can be combined to create enclosed areas"""
    
    def __init__(self, grid_col: int, grid_row: int, fence_type: str = "horizontal"):
        """
        Create a fence segment.
        
        Args:
            grid_col: Column position in grid
            grid_row: Row position in grid
            fence_type: "horizontal", "vertical", "corner_tl", "corner_tr", "corner_bl", "corner_br", "t_up", "t_down", "t_left", "t_right", "cross"
        """
        self.grid_col = grid_col
        self.grid_row = grid_row
        self.fence_type = fence_type
        
        # Calculate pixel position
        self.x = GRID_OFFSET_X + grid_col * GRID_SIZE + GRID_SIZE // 2
        self.y = GRID_OFFSET_Y + grid_row * GRID_SIZE + GRID_SIZE // 2
        
        # Dimensions
        self.width = GRID_SIZE
        self.height = GRID_SIZE
        
        # Colors
        self.wood_color = (139, 90, 43)  # Saddle brown
        self.wood_dark = (101, 67, 33)
        self.wood_light = (160, 110, 60)
        self.post_color = (120, 75, 35)
        
        # Collision rect (full cell for simplicity)
        self.collision_rect = pygame.Rect(
            GRID_OFFSET_X + grid_col * GRID_SIZE,
            GRID_OFFSET_Y + grid_row * GRID_SIZE,
            GRID_SIZE,
            GRID_SIZE
        )
    
    @property
    def sort_y(self) -> int:
        """Y position for depth sorting"""
        return self.y
    
    def get_collision_rect(self) -> pygame.Rect:
        """Get collision rectangle"""
        return self.collision_rect
    
    def collides_with(self, rect: pygame.Rect) -> bool:
        """Check if rectangle collides with fence"""
        return self.collision_rect.colliderect(rect)
    
    def draw(self, screen: pygame.Surface):
        """Draw the fence segment"""
        cx = self.x
        cy = self.y
        
        # Draw based on fence type
        if self.fence_type == "horizontal":
            self._draw_horizontal(screen, cx, cy)
        elif self.fence_type == "vertical":
            self._draw_vertical(screen, cx, cy)
        elif self.fence_type == "corner_tl":
            self._draw_corner_tl(screen, cx, cy)
        elif self.fence_type == "corner_tr":
            self._draw_corner_tr(screen, cx, cy)
        elif self.fence_type == "corner_bl":
            self._draw_corner_bl(screen, cx, cy)
        elif self.fence_type == "corner_br":
            self._draw_corner_br(screen, cx, cy)
        elif self.fence_type == "t_up":
            self._draw_t_up(screen, cx, cy)
        elif self.fence_type == "t_down":
            self._draw_t_down(screen, cx, cy)
        elif self.fence_type == "t_left":
            self._draw_t_left(screen, cx, cy)
        elif self.fence_type == "t_right":
            self._draw_t_right(screen, cx, cy)
        elif self.fence_type == "cross":
            self._draw_cross(screen, cx, cy)
        elif self.fence_type == "end_left":
            self._draw_end_left(screen, cx, cy)
        elif self.fence_type == "end_right":
            self._draw_end_right(screen, cx, cy)
        elif self.fence_type == "end_up":
            self._draw_end_up(screen, cx, cy)
        elif self.fence_type == "end_down":
            self._draw_end_down(screen, cx, cy)
    
    def _draw_posts(self, screen, cx, cy, posts: List[Tuple[int, int]]):
        """Draw fence posts at given positions"""
        for px, py in posts:
            # Post shadow
            pygame.draw.rect(screen, (30, 30, 30), (cx + px - 4, cy + py - 8, 8, 18))
            # Post body
            pygame.draw.rect(screen, self.post_color, (cx + px - 3, cy + py - 10, 6, 16))
            # Post top (rounded)
            pygame.draw.circle(screen, self.post_color, (cx + px, cy + py - 10), 3)
            # Post highlight
            pygame.draw.line(screen, self.wood_light, (cx + px - 2, cy + py - 8), (cx + px - 2, cy + py + 4), 1)
    
    def _draw_horizontal_rails(self, screen, cx, cy, start_x, end_x, y_offset):
        """Draw horizontal fence rails"""
        rail_height = 4
        # Rail shadow
        pygame.draw.rect(screen, (40, 40, 40), 
                        (cx + start_x, cy + y_offset + 2, end_x - start_x, rail_height))
        # Rail body
        pygame.draw.rect(screen, self.wood_color, 
                        (cx + start_x, cy + y_offset, end_x - start_x, rail_height))
        # Rail highlight
        pygame.draw.line(screen, self.wood_light, 
                        (cx + start_x, cy + y_offset), (cx + end_x, cy + y_offset), 1)
    
    def _draw_vertical_rails(self, screen, cx, cy, start_y, end_y, x_offset):
        """Draw vertical fence rails"""
        rail_width = 4
        # Rail shadow
        pygame.draw.rect(screen, (40, 40, 40), 
                        (cx + x_offset + 2, cy + start_y, rail_width, end_y - start_y))
        # Rail body
        pygame.draw.rect(screen, self.wood_color, 
                        (cx + x_offset, cy + start_y, rail_width, end_y - start_y))
        # Rail highlight
        pygame.draw.line(screen, self.wood_light, 
                        (cx + x_offset, cy + start_y), (cx + x_offset, cy + end_y), 1)
    
    def _draw_horizontal(self, screen, cx, cy):
        """Draw horizontal fence segment"""
        # Posts at ends
        self._draw_posts(screen, cx, cy, [(-18, 0), (18, 0)])
        # Horizontal rails
        self._draw_horizontal_rails(screen, cx, cy, -15, 15, -6)
        self._draw_horizontal_rails(screen, cx, cy, -15, 15, 4)
    
    def _draw_vertical(self, screen, cx, cy):
        """Draw vertical fence segment"""
        # Posts at ends
        self._draw_posts(screen, cx, cy, [(0, -18), (0, 18)])
        # Vertical rails
        self._draw_vertical_rails(screen, cx, cy, -15, 15, -6)
        self._draw_vertical_rails(screen, cx, cy, -15, 15, 4)
    
    def _draw_corner_tl(self, screen, cx, cy):
        """Draw top-left corner fence"""
        self._draw_posts(screen, cx, cy, [(-18, -18), (18, 0), (0, 18)])
        # Horizontal rail (right side)
        self._draw_horizontal_rails(screen, cx, cy, 0, 18, -6)
        self._draw_horizontal_rails(screen, cx, cy, 0, 18, 4)
        # Vertical rail (bottom side)
        self._draw_vertical_rails(screen, cx, cy, 0, 18, -6)
        self._draw_vertical_rails(screen, cx, cy, 0, 18, 4)
    
    def _draw_corner_tr(self, screen, cx, cy):
        """Draw top-right corner fence"""
        self._draw_posts(screen, cx, cy, [(18, -18), (-18, 0), (0, 18)])
        # Horizontal rail (left side)
        self._draw_horizontal_rails(screen, cx, cy, -18, 0, -6)
        self._draw_horizontal_rails(screen, cx, cy, -18, 0, 4)
        # Vertical rail (bottom side)
        self._draw_vertical_rails(screen, cx, cy, 0, 18, 2)
        self._draw_vertical_rails(screen, cx, cy, 0, 18, 4)
    
    def _draw_corner_bl(self, screen, cx, cy):
        """Draw bottom-left corner fence"""
        self._draw_posts(screen, cx, cy, [(-18, 18), (18, 0), (0, -18)])
        # Horizontal rail (right side)
        self._draw_horizontal_rails(screen, cx, cy, 0, 18, -6)
        self._draw_horizontal_rails(screen, cx, cy, 0, 18, 4)
        # Vertical rail (top side)
        self._draw_vertical_rails(screen, cx, cy, -18, 0, -6)
        self._draw_vertical_rails(screen, cx, cy, -18, 0, 4)
    
    def _draw_corner_br(self, screen, cx, cy):
        """Draw bottom-right corner fence"""
        self._draw_posts(screen, cx, cy, [(18, 18), (-18, 0), (0, -18)])
        # Horizontal rail (left side)
        self._draw_horizontal_rails(screen, cx, cy, -18, 0, -6)
        self._draw_horizontal_rails(screen, cx, cy, -18, 0, 4)
        # Vertical rail (top side)
        self._draw_vertical_rails(screen, cx, cy, -18, 0, 2)
        self._draw_vertical_rails(screen, cx, cy, -18, 0, 4)
    
    def _draw_t_up(self, screen, cx, cy):
        """Draw T-shaped fence (connection from bottom)"""
        self._draw_posts(screen, cx, cy, [(-18, 0), (18, 0), (0, 18)])
        self._draw_horizontal_rails(screen, cx, cy, -18, 18, -6)
        self._draw_horizontal_rails(screen, cx, cy, -18, 18, 4)
        self._draw_vertical_rails(screen, cx, cy, 0, 18, -6)
        self._draw_vertical_rails(screen, cx, cy, 0, 18, 4)
    
    def _draw_t_down(self, screen, cx, cy):
        """Draw T-shaped fence (connection from top)"""
        self._draw_posts(screen, cx, cy, [(-18, 0), (18, 0), (0, -18)])
        self._draw_horizontal_rails(screen, cx, cy, -18, 18, -6)
        self._draw_horizontal_rails(screen, cx, cy, -18, 18, 4)
        self._draw_vertical_rails(screen, cx, cy, -18, 0, -6)
        self._draw_vertical_rails(screen, cx, cy, -18, 0, 4)
    
    def _draw_t_left(self, screen, cx, cy):
        """Draw T-shaped fence (connection from right)"""
        self._draw_posts(screen, cx, cy, [(0, -18), (0, 18), (18, 0)])
        self._draw_vertical_rails(screen, cx, cy, -18, 18, -6)
        self._draw_vertical_rails(screen, cx, cy, -18, 18, 4)
        self._draw_horizontal_rails(screen, cx, cy, 0, 18, -6)
        self._draw_horizontal_rails(screen, cx, cy, 0, 18, 4)
    
    def _draw_t_right(self, screen, cx, cy):
        """Draw T-shaped fence (connection from left)"""
        self._draw_posts(screen, cx, cy, [(0, -18), (0, 18), (-18, 0)])
        self._draw_vertical_rails(screen, cx, cy, -18, 18, -6)
        self._draw_vertical_rails(screen, cx, cy, -18, 18, 4)
        self._draw_horizontal_rails(screen, cx, cy, -18, 0, -6)
        self._draw_horizontal_rails(screen, cx, cy, -18, 0, 4)
    
    def _draw_cross(self, screen, cx, cy):
        """Draw cross-shaped fence (4-way connection)"""
        self._draw_posts(screen, cx, cy, [(-18, 0), (18, 0), (0, -18), (0, 18)])
        self._draw_horizontal_rails(screen, cx, cy, -18, 18, -6)
        self._draw_horizontal_rails(screen, cx, cy, -18, 18, 4)
        self._draw_vertical_rails(screen, cx, cy, -18, 18, -6)
        self._draw_vertical_rails(screen, cx, cy, -18, 18, 4)
    
    def _draw_end_left(self, screen, cx, cy):
        """Draw fence end (left side)"""
        self._draw_posts(screen, cx, cy, [(0, -18), (0, 18)])
        self._draw_vertical_rails(screen, cx, cy, -18, 18, -6)
        self._draw_vertical_rails(screen, cx, cy, -18, 18, 4)
        # End cap
        pygame.draw.rect(screen, self.wood_dark, (cx - 8, cy - 12, 6, 24))
    
    def _draw_end_right(self, screen, cx, cy):
        """Draw fence end (right side)"""
        self._draw_posts(screen, cx, cy, [(0, -18), (0, 18)])
        self._draw_vertical_rails(screen, cx, cy, -18, 18, -6)
        self._draw_vertical_rails(screen, cx, cy, -18, 18, 4)
        # End cap
        pygame.draw.rect(screen, self.wood_dark, (cx + 2, cy - 12, 6, 24))
    
    def _draw_end_up(self, screen, cx, cy):
        """Draw fence end (top side)"""
        self._draw_posts(screen, cx, cy, [(-18, 0), (18, 0)])
        self._draw_horizontal_rails(screen, cx, cy, -18, 18, -6)
        self._draw_horizontal_rails(screen, cx, cy, -18, 18, 4)
        # End cap
        pygame.draw.rect(screen, self.wood_dark, (cx - 12, cy - 12, 24, 6))
    
    def _draw_end_down(self, screen, cx, cy):
        """Draw fence end (bottom side)"""
        self._draw_posts(screen, cx, cy, [(-18, 0), (18, 0)])
        self._draw_horizontal_rails(screen, cx, cy, -18, 18, -6)
        self._draw_horizontal_rails(screen, cx, cy, -18, 18, 4)
        # End cap
        pygame.draw.rect(screen, self.wood_dark, (cx - 12, cy + 6, 24, 6))


class FenceDoor:
    """A fence door that can be opened/closed"""
    
    def __init__(self, grid_col: int, grid_row: int, orientation: str = "horizontal"):
        self.grid_col = grid_col
        self.grid_row = grid_row
        self.orientation = orientation
        self.is_open = False
        
        # Calculate pixel position
        self.x = GRID_OFFSET_X + grid_col * GRID_SIZE + GRID_SIZE // 2
        self.y = GRID_OFFSET_Y + grid_row * GRID_SIZE + GRID_SIZE // 2
        
        # Colors
        self.wood_color = (139, 90, 43)
        self.wood_dark = (101, 67, 33)
        self.wood_light = (160, 110, 60)
        self.metal_color = (200, 200, 200)
        
        # Collision rect (full cell when closed)
        self.collision_rect = pygame.Rect(
            GRID_OFFSET_X + grid_col * GRID_SIZE,
            GRID_OFFSET_Y + grid_row * GRID_SIZE,
            GRID_SIZE,
            GRID_SIZE
        )
    
    @property
    def sort_y(self) -> int:
        return self.y
    
    def toggle(self):
        """Toggle door open/closed state"""
        self.is_open = not self.is_open
    
    def collides_with(self, rect: pygame.Rect) -> bool:
        """Check collision only if door is closed"""
        if self.is_open:
            return False
        return self.collision_rect.colliderect(rect)
    
    def draw(self, screen: pygame.Surface):
        """Draw the fence door"""
        cx = self.x
        cy = self.y
        
        if self.is_open:
            # Draw open door (swung aside)
            if self.orientation == "horizontal":
                door_rect = pygame.Rect(cx + 6, cy - 12, 14, 24)
            else:
                door_rect = pygame.Rect(cx - 12, cy + 6, 24, 14)
        else:
            # Draw closed door
            if self.orientation == "horizontal":
                door_rect = pygame.Rect(cx - 14, cy - 6, 28, 12)
            else:
                door_rect = pygame.Rect(cx - 6, cy - 14, 12, 28)
        
        # Door shadow
        pygame.draw.rect(screen, (40, 40, 40), door_rect.inflate(2, 2))
        # Door body
        pygame.draw.rect(screen, self.wood_color, door_rect)
        # Door highlight
        pygame.draw.line(screen, self.wood_light, door_rect.topleft, door_rect.topright, 1)
        # Hinges/handle
        handle_x = door_rect.right - 4 if not self.is_open else door_rect.left + 2
        handle_y = door_rect.centery
        pygame.draw.circle(screen, self.metal_color, (handle_x, handle_y), 2)


class FencedArea:
    """A fenced area that contains animals"""
    
    def __init__(self, name: str, left: int, top: int, width: int, height: int, animal_type: str,
                 door_col: int, door_row: int, door_orientation: str = "horizontal"):
        """
        Create a fenced area.
        
        Args:
            name: Name of the area (e.g., "Chicken Coop", "Cow Pasture")
            left: Left grid column
            top: Top grid row
            width: Width in grid cells
            height: Height in grid cells
            animal_type: "chicken" or "cow"
            door_col: Grid column for the door
            door_row: Grid row for the door
            door_orientation: "horizontal" or "vertical"
        """
        self.name = name
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.animal_type = animal_type
        self.door_col = door_col
        self.door_row = door_row
        self.door_orientation = door_orientation
        
        # Calculate bounds (inside the fence)
        self.inner_left = GRID_OFFSET_X + (left + 1) * GRID_SIZE
        self.inner_top = GRID_OFFSET_Y + (top + 1) * GRID_SIZE
        self.inner_right = GRID_OFFSET_X + (left + width - 1) * GRID_SIZE
        self.inner_bottom = GRID_OFFSET_Y + (top + height - 1) * GRID_SIZE
        
        # Create fence segments and door
        self.fences: List[Fence] = []
        self.door = FenceDoor(door_col, door_row, door_orientation)
        self._create_fences()
    
    def _create_fences(self):
        """Create all fence segments for this area"""
        right = self.left + self.width - 1
        bottom = self.top + self.height - 1
        
        # Top wall
        for col in range(self.left, self.left + self.width):
            if col == self.left:
                fence_type = "corner_tl"
            elif col == right:
                fence_type = "corner_tr"
            else:
                fence_type = "horizontal"
            # Skip fence segment where the door is placed
            if not (self.door_row == self.top and self.door_col == col):
                self.fences.append(Fence(col, self.top, fence_type))
        
        # Bottom wall
        for col in range(self.left, self.left + self.width):
            if col == self.left:
                fence_type = "corner_bl"
            elif col == right:
                fence_type = "corner_br"
            else:
                fence_type = "horizontal"
            # Skip fence segment where the door is placed
            if not (self.door_row == bottom and self.door_col == col):
                self.fences.append(Fence(col, bottom, fence_type))
        
        # Left wall (excluding corners)
        for row in range(self.top + 1, bottom):
            if not (self.door_col == self.left and self.door_row == row):
                self.fences.append(Fence(self.left, row, "vertical"))
        
        # Right wall (excluding corners)
        for row in range(self.top + 1, bottom):
            if not (self.door_col == right and self.door_row == row):
                self.fences.append(Fence(self.left + self.width - 1, row, "vertical"))
    
    def get_spawn_position(self) -> Tuple[int, int]:
        """Get a random spawn position inside the fenced area"""
        import random
        x = random.randint(self.inner_left + 20, self.inner_right - 20)
        y = random.randint(self.inner_top + 20, self.inner_bottom - 20)
        return (x, y)
    
    def contains_position(self, x: int, y: int) -> bool:
        """Check if a position is inside the fenced area"""
        return (self.inner_left <= x <= self.inner_right and 
                self.inner_top <= y <= self.inner_bottom)
    
    def clamp_position(self, x: int, y: int, margin: int = 15) -> Tuple[int, int]:
        """Clamp a position to stay inside the fenced area"""
        x = max(self.inner_left + margin, min(x, self.inner_right - margin))
        y = max(self.inner_top + margin, min(y, self.inner_bottom - margin))
        return (x, y)
    
    def draw(self, screen: pygame.Surface):
        """Draw all fence segments and the door"""
        for fence in self.fences:
            fence.draw(screen)
        self.door.draw(screen)
    
    def get_obstacles(self) -> List[object]:
        """Get all fence segments and door as obstacles"""
        obstacles: List[object] = []
        obstacles.extend(self.fences)
        if not self.door.is_open:
            obstacles.append(self.door)
        return obstacles
    
    def is_door_clicked(self, mouse_pos: Tuple[int, int]) -> bool:
        """Check if the door was clicked"""
        return self.door.collision_rect.collidepoint(mouse_pos)
    
    def toggle_door(self):
        """Toggle the door open/closed"""
        self.door.toggle()
