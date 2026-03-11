"""
Chicken Entity - A farm animal that walks around
"""
import pygame
import random
import math
from typing import Tuple, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    GRID_SIZE, GRID_OFFSET_X, GRID_OFFSET_Y, GRID_COLS, GRID_ROWS
)


class Chicken:
    """A chicken animal that walks around the farm"""
    
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.width = 24
        self.height = 20
        
        # Movement
        self.speed = 0.8
        self.direction = random.choice(['left', 'right', 'up', 'down'])
        self.walk_timer = 0
        self.walk_duration = random.uniform(1.0, 3.0)
        self.idle_timer = 0
        self.idle_duration = random.uniform(0.5, 2.0)
        self.is_walking = False
        self.animation_frame = 0
        self.animation_timer = 0
        
        # Fenced area constraint (set by game_manager when spawned)
        self.fenced_area = None
        
        # Colors
        self.body_color = (255, 255, 255)  # White chicken
        self.body_shadow = (220, 220, 220)
        self.comb_color = (220, 50, 50)  # Red comb
        self.beak_color = (255, 180, 50)  # Orange beak
        self.feet_color = (255, 180, 50)
        self.eye_color = (30, 30, 30)
        
        # Random variation
        self.body_tint = random.randint(-15, 15)
        self.size_variation = random.uniform(0.9, 1.1)
        
        # Feeding/affection state
        self.is_fed = False
        self.heart_timer = 0.0
        
        # Egg production state
        self.egg_production_timer = 0.0
        self.egg_ready = False
        self.egg_drop_position = None
        
    @property
    def sort_y(self) -> int:
        """Y position for depth sorting"""
        return self.y + self.height // 2
    
    @property
    def rect(self) -> pygame.Rect:
        """Get collision rectangle"""
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, 
                          self.width, self.height)
    
    def update(self, dt: float, obstacles: list = None):
        """Update chicken movement and animation"""
        # Update animation
        self.animation_timer += dt
        if self.animation_timer > 0.1:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4
        
        if self.heart_timer > 0:
            self.heart_timer = max(0.0, self.heart_timer - dt)
            if self.heart_timer == 0:
                self.is_fed = False
        
        # Egg production timer
        if self.egg_production_timer > 0:
            self.egg_production_timer = max(0.0, self.egg_production_timer - dt)
            if self.egg_production_timer == 0 and not self.egg_ready:
                self.egg_ready = True
                self.egg_drop_position = (int(self.x), int(self.y + 10))
        
        if self.is_walking:
            self.walk_timer += dt
            
            # Move in current direction
            dx, dy = 0, 0
            if self.direction == 'left':
                dx = -self.speed
            elif self.direction == 'right':
                dx = self.speed
            elif self.direction == 'up':
                dy = -self.speed
            elif self.direction == 'down':
                dy = self.speed
            
            new_x = self.x + dx
            new_y = self.y + dy
            
            # Check bounds - use fenced area if available, otherwise use grid bounds
            if self.fenced_area:
                # Constrain to fenced area
                min_x = self.fenced_area.inner_left + self.width // 2 + 5
                max_x = self.fenced_area.inner_right - self.width // 2 - 5
                min_y = self.fenced_area.inner_top + self.height // 2 + 5
                max_y = self.fenced_area.inner_bottom - self.height // 2 - 5
            else:
                # Use grid bounds
                min_x = GRID_OFFSET_X + self.width
                max_x = GRID_OFFSET_X + GRID_COLS * GRID_SIZE - self.width
                min_y = GRID_OFFSET_Y + self.height
                max_y = GRID_OFFSET_Y + GRID_ROWS * GRID_SIZE - self.height
            
            # Check if can move
            can_move = True
            if new_x < min_x or new_x > max_x or new_y < min_y or new_y > max_y:
                can_move = False
            
            # Check obstacle collision
            if can_move and obstacles:
                test_rect = pygame.Rect(new_x - self.width // 2, new_y - self.height // 2,
                                       self.width, self.height)
                for obs in obstacles:
                    if hasattr(obs, 'collision_rect') and test_rect.colliderect(obs.collision_rect):
                        can_move = False
                        break
            
            if can_move:
                self.x = new_x
                self.y = new_y
            else:
                # Change direction when hitting obstacle
                self.direction = random.choice(['left', 'right', 'up', 'down'])
            
            # Check if walk duration is over
            if self.walk_timer >= self.walk_duration:
                self.is_walking = False
                self.idle_timer = 0
                self.idle_duration = random.uniform(0.5, 2.0)
        else:
            self.idle_timer += dt
            
            # Check if idle duration is over
            if self.idle_timer >= self.idle_duration:
                self.is_walking = True
                self.walk_timer = 0
                self.walk_duration = random.uniform(1.0, 3.0)
                # Random new direction
                self.direction = random.choice(['left', 'right', 'up', 'down'])
    
    def draw(self, screen: pygame.Surface):
        """Draw the chicken with realistic appearance"""
        scale = self.size_variation
        
        # Animation offset for walking
        bob_offset = 0
        head_bob = 0
        if self.is_walking:
            bob_offset = int(math.sin(self.animation_frame * math.pi / 2) * 2)
            head_bob = int(math.sin(self.animation_frame * math.pi) * 1)
        
        cx = int(self.x)
        cy = int(self.y) + bob_offset
        
        # Determine facing direction
        facing_right = self.direction != 'left'
        
        # Shadow on ground
        pygame.draw.ellipse(screen, (25, 25, 25, 128), 
                           (cx - 12, cy + 8, 24, 8))
        
        # === FEET/LEGS ===
        # Realistic chicken feet with 3 toes
        feet_color = (255, 180, 80)
        feet_dark = (220, 150, 60)
        
        if self.is_walking:
            leg_offset = int(math.sin(self.animation_frame * math.pi) * 4)
            # Left leg
            self._draw_chicken_foot(screen, cx - 4 + leg_offset, cy + 6, feet_color, feet_dark)
            # Right leg
            self._draw_chicken_foot(screen, cx + 4 - leg_offset, cy + 6, feet_color, feet_dark)
        else:
            # Standing feet
            self._draw_chicken_foot(screen, cx - 4, cy + 6, feet_color, feet_dark)
            self._draw_chicken_foot(screen, cx + 4, cy + 6, feet_color, feet_dark)
        
        # === BODY ===
        # Realistic rounded body
        body_width = int(22 * scale)
        body_height = int(16 * scale)
        
        # Body base (plumage)
        body_color = tuple(max(0, min(255, c + self.body_tint)) for c in self.body_color)
        
        # Lower body (fuller)
        pygame.draw.ellipse(screen, body_color, 
                           (cx - body_width // 2, cy - 2, body_width, body_height + 4))
        
        # Body shading
        shade_color = tuple(max(0, c - 25) for c in body_color)
        pygame.draw.ellipse(screen, shade_color, 
                           (cx - body_width // 2 + 2, cy + 2, body_width - 8, body_height - 2))
        
        # Feather texture (subtle lines)
        for i in range(3):
            feather_y = cy + i * 3
            pygame.draw.arc(screen, shade_color, 
                           (cx - 8, feather_y - 2, 16, 6), 0, math.pi, 1)
        
        # === TAIL FEATHERS ===
        # More realistic tail feathers
        tail_x = cx - body_width // 2 if facing_right else cx + body_width // 2 - 6
        tail_dir = -1 if facing_right else 1
        
        # Multiple tail feathers
        for i in range(3):
            offset_y = -4 + i * 3
            feather_color = tuple(max(0, c - 20 + i * 5) for c in body_color)
            pygame.draw.ellipse(screen, feather_color, 
                               (tail_x + tail_dir * i * 2, cy + offset_y, 8, 14))
        
        # === WING ===
        # Folded wing with feather detail
        wing_x = cx - 2 if facing_right else cx - 8
        wing_color = tuple(max(0, c - 15) for c in body_color)
        
        # Wing base
        pygame.draw.ellipse(screen, wing_color, (wing_x, cy - 2, 10, 12))
        
        # Wing feather lines
        for i in range(3):
            pygame.draw.line(screen, shade_color, 
                            (wing_x + 2, cy + i * 3), (wing_x + 8, cy + i * 3), 1)
        
        # === NECK ===
        # Graceful neck connecting body to head
        neck_x = cx + 6 if facing_right else cx - 8
        pygame.draw.ellipse(screen, body_color, (neck_x - 3, cy - 6, 8, 10))
        
        # === HEAD ===
        head_x = cx + 8 if facing_right else cx - 8
        head_y = cy - 8 + head_bob
        
        # Head shape (slightly elongated)
        pygame.draw.ellipse(screen, body_color, (head_x - 5, head_y - 4, 10, 9))
        
        # === COMB ===
        # Realistic serrated comb
        comb_color = (220, 40, 40)
        comb_highlight = (255, 80, 80)
        
        # Comb base
        pygame.draw.ellipse(screen, comb_color, (head_x - 4, head_y - 8, 8, 5))
        
        # Comb points (serrations)
        for i in range(3):
            point_x = head_x - 3 + i * 3
            pygame.draw.ellipse(screen, comb_color, (point_x - 1, head_y - 12, 3, 5))
        
        # Comb highlight
        pygame.draw.ellipse(screen, comb_highlight, (head_x - 2, head_y - 10, 3, 3))
        
        # === WATTLE ===
        # Red wattle under beak
        wattle_x = head_x + 3 if facing_right else head_x - 5
        pygame.draw.ellipse(screen, comb_color, (wattle_x, head_y + 2, 4, 6))
        
        # === BEAK ===
        # Realistic curved beak
        beak_color = (255, 200, 100)
        beak_dark = (200, 150, 50)
        
        beak_x = head_x + 5 if facing_right else head_x - 7
        
        # Upper beak
        pygame.draw.polygon(screen, beak_color, [
            (beak_x, head_y - 1),
            (beak_x + 5 if facing_right else beak_x - 5, head_y + 1),
            (beak_x, head_y + 3)
        ])
        
        # Lower beak (smaller)
        pygame.draw.polygon(screen, beak_dark, [
            (beak_x, head_y + 2),
            (beak_x + 3 if facing_right else beak_x - 3, head_y + 3),
            (beak_x, head_y + 4)
        ])
        
        # === EYE ===
        eye_x = head_x + 2 if facing_right else head_x - 3
        
        # Eye ring
        pygame.draw.circle(screen, (255, 255, 200), (eye_x, head_y - 1), 3)
        # Pupil
        pygame.draw.circle(screen, (20, 20, 20), (eye_x, head_y - 1), 2)
        # Eye highlight
        pygame.draw.circle(screen, (255, 255, 255), (eye_x - 1, head_y - 2), 1)
        
        # === EAR (small patch) ===
        ear_x = head_x - 2 if facing_right else head_x + 2
        pygame.draw.ellipse(screen, (255, 220, 200), (ear_x, head_y, 3, 4))
        
        # Draw heart if fed
        if self.heart_timer > 0:
            self._draw_heart(screen, cx, cy - 20)
        
        # Draw egg if ready
        if self.egg_ready and self.egg_drop_position:
            self._draw_egg(screen, self.egg_drop_position[0], self.egg_drop_position[1])
    
    def _draw_egg(self, screen: pygame.Surface, x: int, y: int):
        """Draw an egg on the ground near the chicken"""
        # Shadow
        pygame.draw.ellipse(screen, (30, 30, 30), (x - 6, y + 4, 12, 4))
        # Egg body
        pygame.draw.ellipse(screen, (255, 250, 240), (x - 5, y - 6, 10, 12))
        # Egg highlight
        pygame.draw.ellipse(screen, (255, 255, 255), (x - 3, y - 4, 4, 5))
    
    def _draw_chicken_foot(self, screen, x, y, main_color, dark_color):
        """Draw a realistic chicken foot with three toes"""
        # Main toe (forward)
        pygame.draw.polygon(screen, main_color, [
            (x, y), (x + 6, y + 6), (x + 4, y + 7), (x - 1, y + 2)
        ])
        # Left toe
        pygame.draw.polygon(screen, main_color, [
            (x, y), (x - 5, y + 5), (x - 4, y + 6), (x + 1, y + 2)
        ])
        # Right toe
        pygame.draw.polygon(screen, main_color, [
            (x, y), (x + 3, y + 5), (x + 2, y + 6), (x - 1, y + 2)
        ])
        # Back toe (hallux)
        pygame.draw.polygon(screen, dark_color, [
            (x - 1, y - 1), (x - 6, y + 2), (x - 5, y + 3), (x - 1, y + 1)
        ])
    
    def feed(self, duration: float = 3.0):
        """Feed the chicken and show a heart"""
        self.is_fed = True
        self.heart_timer = duration
        # Start egg production timer (30 seconds)
        if self.egg_production_timer <= 0 and not self.egg_ready:
            self.egg_production_timer = 30.0
    
    def collect_egg(self):
        """Collect the ready egg and reset state"""
        if self.egg_ready:
            self.egg_ready = False
            pos = self.egg_drop_position
            self.egg_drop_position = None
            return pos
        return None
    
    def _draw_heart(self, screen: pygame.Surface, x: int, y: int):
        """Draw a heart above the chicken"""
        heart_color = (255, 80, 120)
        # Left circle
        pygame.draw.circle(screen, heart_color, (x - 4, y), 4)
        # Right circle
        pygame.draw.circle(screen, heart_color, (x + 4, y), 4)
        # Triangle bottom
        pygame.draw.polygon(screen, heart_color, [(x - 8, y + 2), (x + 8, y + 2), (x, y + 10)])
