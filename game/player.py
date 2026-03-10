"""
Player Controller - Handles player input and movement
"""
import pygame
import math
from typing import Tuple, List
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from entities.farmer import Farmer
from config import PLAYER_MAX_HEALTH


class Player:
    """Handles player input and controls the farmer character"""
    
    def __init__(self, farmer: Farmer):
        self.farmer = farmer
        
        # XP System
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = self._calculate_xp_for_level(self.level)
        
        # Money System
        self.money = 100  # Start with 100 coins
        
        # Health System
        self.max_health = PLAYER_MAX_HEALTH
        self.health = self.max_health
        
        # XP values for different activities
        self.xp_values = {
            'tree_small': 15,
            'tree_medium': 25,
            'tree_large': 40,
            'stone_small': 10,
            'stone_medium': 20,
            'stone_large': 35,
            'plant_seed': 5,
            'harvest_plant': 10,
        }
    
    def _calculate_xp_for_level(self, level: int) -> int:
        """
        Calculate XP required to reach the next level.
        Formula: Base 100 XP for level 1, increasing by 10 XP per level.
        Level 1 -> 2: 100 XP
        Level 10 -> 11: 200 XP (100 + 9*10 + 10)
        """
        return 100 + (level - 1) * 10
    
    def add_xp(self, amount: int) -> bool:
        """
        Add XP to the player. Returns True if player leveled up.
        """
        self.xp += amount
        leveled_up = False
        
        # Check for level ups (can level up multiple times at once)
        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.level += 1
            self.xp_to_next_level = self._calculate_xp_for_level(self.level)
            leveled_up = True
        
        return leveled_up
    
    def add_money(self, amount: int) -> int:
        """
        Add money to the player. Returns the new balance.
        """
        self.money += amount
        return self.money
    
    def spend_money(self, amount: int) -> bool:
        """
        Try to spend money. Returns True if successful, False if not enough money.
        """
        if self.money >= amount:
            self.money -= amount
            return True
        return False
    
    def get_xp_for_activity(self, activity: str) -> int:
        """Get XP value for a specific activity"""
        return self.xp_values.get(activity, 0)
    
    def get_xp_progress_percentage(self) -> float:
        """Get the current XP progress as a percentage (0-100)"""
        if self.xp_to_next_level == 0:
            return 100.0
        return (self.xp / self.xp_to_next_level) * 100
    
    def take_damage(self, amount: int):
        """Decrease player health"""
        self.health = max(0, self.health - amount)
    
    def heal(self, amount: int):
        """Increase player health"""
        self.health = min(self.max_health, self.health + amount)
    
    def move(self, dx: int, dy: int, bounds: pygame.Rect, obstacles: List = None):
        """Move the farmer based on input"""
        self.farmer.move(dx, dy, bounds, obstacles)
    
    def get_position(self) -> Tuple[int, int]:
        """Get the farmer's position"""
        return (self.farmer.x, self.farmer.y)
    
    def get_grid_position(self) -> Tuple[int, int]:
        """Get the grid cell the farmer is on"""
        return self.farmer.get_grid_position()