"""
Player Controller - Handles player input and movement
"""
import pygame
from typing import Tuple, List
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from entities.farmer import Farmer


class Player:
    """Handles player input and controls the farmer character"""
    
    def __init__(self, farmer: Farmer):
        self.farmer = farmer
    
    def move(self, dx: int, dy: int, bounds: pygame.Rect, obstacles: List = None):
        """Move the farmer based on input"""
        self.farmer.move(dx, dy, bounds, obstacles)
    
    def get_position(self) -> Tuple[int, int]:
        """Get the farmer's position"""
        return (self.farmer.x, self.farmer.y)
    
    def get_grid_position(self) -> Tuple[int, int]:
        """Get the grid cell the farmer is on"""
        return self.farmer.get_grid_position()