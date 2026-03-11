"""
Cow Entity - A farm animal that walks around
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


class Cow:
    """A cow animal that walks around the farm"""
    
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 30
        
        # Movement
        self.speed = 0.5
        self.direction = random.choice(['left', 'right', 'up', 'down'])
        self.walk_timer = 0
        self.walk_duration = random.uniform(2.0, 4.0)
        self.idle_timer = 0
        self.idle_duration = random.uniform(1.0, 3.0)
        self.is_walking = False
        self.animation_frame = 0
        self.animation_timer = 0
        
        # Fenced area constraint (set by game_manager when spawned)
        self.fenced_area = None
        
        # Colors - classic black and white cow
        self.body_color = (255, 255, 255)  # White
        self.spot_color = (40, 40, 40)  # Black spots
        self.body_shadow = (230, 230, 230)
        self.nose_color = (255, 200, 200)  # Pink nose
        self.horn_color = (230, 210, 180)  # Horn color
        self.hoof_color = (60, 50, 40)  # Dark hooves
        
        # Random variation
        self.size_variation = random.uniform(0.9, 1.1)
        
        # Feeding/affection state
        self.is_fed = False
        self.heart_timer = 0.0
        
        # Generate random spots
        self.spots = self._generate_spots()
        
    def _generate_spots(self) -> list:
        """Generate random cow spots"""
        spots = []
        num_spots = random.randint(3, 6)
        for _ in range(num_spots):
            spot = {
                'x': random.randint(-12, 12),
                'y': random.randint(-6, 6),
                'width': random.randint(6, 12),
                'height': random.randint(4, 8)
            }
            spots.append(spot)
        return spots
        
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
        """Update cow movement and animation"""
        # Update animation
        self.animation_timer += dt
        if self.animation_timer > 0.15:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4
        
        if self.heart_timer > 0:
            self.heart_timer = max(0.0, self.heart_timer - dt)
            if self.heart_timer == 0:
                self.is_fed = False
        
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
                self.idle_duration = random.uniform(1.0, 3.0)
        else:
            self.idle_timer += dt
            
            # Check if idle duration is over
            if self.idle_timer >= self.idle_duration:
                self.is_walking = True
                self.walk_timer = 0
                self.walk_duration = random.uniform(2.0, 4.0)
                # Random new direction
                self.direction = random.choice(['left', 'right', 'up', 'down'])
    
    def draw(self, screen: pygame.Surface):
        """Draw the cow with realistic appearance"""
        scale = self.size_variation
        
        # Animation offset for walking
        bob_offset = 0
        head_bob = 0
        tail_swing = 0
        if self.is_walking:
            bob_offset = int(math.sin(self.animation_frame * math.pi / 2) * 1)
            head_bob = int(math.sin(self.animation_frame * math.pi) * 1)
            tail_swing = int(math.sin(self.animation_frame * math.pi / 2) * 3)
        
        cx = int(self.x)
        cy = int(self.y) + bob_offset
        
        # Determine facing direction
        facing_right = self.direction != 'left'
        
        # === SHADOW ===
        pygame.draw.ellipse(screen, (25, 25, 25), 
                           (cx - 22, cy + 12, 44, 12))
        
        # === LEGS ===
        # Realistic cow legs with proper anatomy
        leg_color = self.body_color
        leg_shadow = self.body_shadow
        
        if self.is_walking:
            leg_offset = int(math.sin(self.animation_frame * math.pi) * 4)
            # Back left leg
            self._draw_cow_leg(screen, cx - 14, cy + 6, leg_color, leg_shadow, False)
            # Back right leg
            self._draw_cow_leg(screen, cx + 8, cy + 6, leg_color, leg_shadow, False)
            # Front left leg (animated)
            self._draw_cow_leg(screen, cx - 8 + leg_offset, cy + 6, leg_color, leg_shadow, True)
            # Front right leg (animated opposite)
            self._draw_cow_leg(screen, cx + 2 - leg_offset, cy + 6, leg_color, leg_shadow, True)
        else:
            # Standing legs
            self._draw_cow_leg(screen, cx - 14, cy + 6, leg_color, leg_shadow, False)
            self._draw_cow_leg(screen, cx - 6, cy + 6, leg_color, leg_shadow, False)
            self._draw_cow_leg(screen, cx + 2, cy + 6, leg_color, leg_shadow, True)
            self._draw_cow_leg(screen, cx + 10, cy + 6, leg_color, leg_shadow, True)
        
        # === UDDER ===
        # Realistic udder (for female cow)
        udder_color = (255, 220, 220)
        udder_shadow = (240, 200, 200)
        udder_x = cx - 4
        pygame.draw.ellipse(screen, udder_shadow, (udder_x, cy + 4, 12, 8))
        pygame.draw.ellipse(screen, udder_color, (udder_x + 1, cy + 3, 10, 7))
        # Teats
        for i in range(4):
            tat_x = udder_x + 2 + (i % 2) * 5
            tat_y = cy + 9 + (i // 2) * 2
            pygame.draw.ellipse(screen, udder_shadow, (tat_x, tat_y, 3, 4))
        
        # === BODY ===
        # Large, realistic barrel-shaped body
        body_width = int(44 * scale)
        body_height = int(26 * scale)
        
        # Body base
        pygame.draw.ellipse(screen, self.body_color, 
                           (cx - body_width // 2, cy - body_height // 2 + 2, 
                            body_width, body_height))
        
        # Body shading (darker underside)
        shade_color = tuple(max(0, c - 20) for c in self.body_color)
        pygame.draw.ellipse(screen, shade_color, 
                           (cx - body_width // 2 + 4, cy + 2, 
                            body_width - 12, body_height - 8))
        
        # === SPOTS ===
        # Irregular black spots
        for spot in self.spots:
            spot_x = cx + spot['x']
            spot_y = cy + spot['y']
            # Main spot
            pygame.draw.ellipse(screen, self.spot_color,
                              (spot_x - spot['width'] // 2, spot_y - spot['height'] // 2,
                               spot['width'], spot['height']))
            # Spot edge (slightly darker for depth)
            spot_edge = tuple(max(0, c - 20) for c in self.spot_color)
            pygame.draw.ellipse(screen, spot_edge,
                              (spot_x - spot['width'] // 2, spot_y - spot['height'] // 2,
                               spot['width'], spot['height']), 1)
        
        # === TAIL ===
        tail_base_x = cx - body_width // 2 + 4 if facing_right else cx + body_width // 2 - 8
        tail_dir = -1 if facing_right else 1
        
        # Tail segments (more realistic)
        tail_points = []
        for i in range(5):
            tx = tail_base_x + tail_dir * i * 2
            ty = cy - 2 + i * 3 + int(math.sin(i + tail_swing * 0.1) * 2)
            tail_points.append((tx, ty))
        
        # Draw tail as connected segments
        for i in range(len(tail_points) - 1):
            pygame.draw.line(screen, self.body_color, tail_points[i], tail_points[i + 1], 3)
        
        # Tail tuft (switch)
        tuft_x = tail_points[-1][0]
        tuft_y = tail_points[-1][1]
        pygame.draw.ellipse(screen, self.spot_color, (tuft_x - 4, tuft_y - 2, 8, 10))
        
        # === NECK ===
        # Muscular neck
        neck_x = cx + 16 if facing_right else cx - 20
        pygame.draw.ellipse(screen, self.body_color, (neck_x - 4, cy - 4, 14, 16))
        # Neck dewlap (loose skin)
        pygame.draw.ellipse(screen, shade_color, (neck_x - 2, cy + 4, 10, 8))
        
        # === HEAD ===
        head_x = cx + 22 if facing_right else cx - 22
        head_y = cy - 6 + head_bob
        
        # Head base (wider, more bovine)
        pygame.draw.ellipse(screen, self.body_color, (head_x - 10, head_y - 6, 20, 16))
        
        # Forehead
        pygame.draw.ellipse(screen, self.body_color, (head_x - 8, head_y - 10, 16, 10))
        
        # === EARS ===
        ear_color = self.body_color
        ear_inner = (255, 200, 200)
        
        # Left ear
        ear_lx = head_x - 10 if facing_right else head_x - 8
        pygame.draw.ellipse(screen, ear_color, (ear_lx, head_y - 8, 10, 6))
        pygame.draw.ellipse(screen, ear_inner, (ear_lx + 2, head_y - 7, 6, 4))
        
        # Right ear
        ear_rx = head_x + 4 if facing_right else head_x + 2
        pygame.draw.ellipse(screen, ear_color, (ear_rx, head_y - 8, 10, 6))
        pygame.draw.ellipse(screen, ear_inner, (ear_rx + 2, head_y - 7, 6, 4))
        
        # === HORNS ===
        horn_base = (210, 190, 160)
        horn_tip = (180, 160, 130)
        
        # Left horn
        horn_lx = head_x - 6 if facing_right else head_x - 4
        pygame.draw.ellipse(screen, horn_base, (horn_lx, head_y - 14, 5, 10))
        pygame.draw.ellipse(screen, horn_tip, (horn_lx + 1, head_y - 16, 3, 6))
        
        # Right horn
        horn_rx = head_x + 4 if facing_right else head_x + 2
        pygame.draw.ellipse(screen, horn_base, (horn_rx, head_y - 14, 5, 10))
        pygame.draw.ellipse(screen, horn_tip, (horn_rx + 1, head_y - 16, 3, 6))
        
        # === FACE ===
        # White face blaze (common in Holstein)
        pygame.draw.ellipse(screen, (255, 255, 255), (head_x - 4, head_y - 4, 8, 10))
        
        # === EYES ===
        # Left eye
        eye_lx = head_x - 6 if facing_right else head_x - 4
        pygame.draw.ellipse(screen, (255, 255, 255), (eye_lx, head_y - 3, 6, 5))
        pygame.draw.ellipse(screen, (40, 30, 20), (eye_lx + 1, head_y - 2, 4, 4))
        pygame.draw.ellipse(screen, (255, 255, 255), (eye_lx + 2, head_y - 2, 2, 2))
        
        # Right eye
        eye_rx = head_x + 2 if facing_right else head_x
        pygame.draw.ellipse(screen, (255, 255, 255), (eye_rx, head_y - 3, 6, 5))
        pygame.draw.ellipse(screen, (40, 30, 20), (eye_rx + 1, head_y - 2, 4, 4))
        pygame.draw.ellipse(screen, (255, 255, 255), (eye_rx + 2, head_y - 2, 2, 2))
        
        # === NOSE/MUZZLE ===
        muzzle_x = head_x + 6 if facing_right else head_x - 12
        muzzle_color = (255, 200, 200)
        muzzle_dark = (230, 170, 170)
        
        # Muzzle base
        pygame.draw.ellipse(screen, muzzle_color, (muzzle_x - 6, head_y + 2, 12, 8))
        
        # Nostrils
        pygame.draw.ellipse(screen, muzzle_dark, (muzzle_x - 3, head_y + 4, 3, 3))
        pygame.draw.ellipse(screen, muzzle_dark, (muzzle_x + 1, head_y + 4, 3, 3))
        
        # Nose highlight
        pygame.draw.ellipse(screen, (255, 230, 230), (muzzle_x - 4, head_y + 3, 4, 3))
        
        # === MOUTH ===
        mouth_y = head_y + 8
        pygame.draw.arc(screen, muzzle_dark, (muzzle_x - 4, mouth_y - 2, 8, 4), 0, math.pi, 1)
        
        # Draw heart if fed
        if self.heart_timer > 0:
            self._draw_heart(screen, cx, cy - 28)
    
    def _draw_cow_leg(self, screen, x, y, leg_color, leg_shadow, is_front):
        """Draw a realistic cow leg with hoof"""
        # Upper leg (thigh/gaskin)
        pygame.draw.ellipse(screen, leg_color, (x - 4, y - 2, 8, 12))
        
        # Lower leg (cannon bone)
        pygame.draw.ellipse(screen, leg_shadow, (x - 3, y + 6, 6, 10))
        
        # Hoof
        hoof_color = (50, 40, 35)
        hoof_light = (70, 60, 50)
        
        # Hoof wall
        pygame.draw.ellipse(screen, hoof_color, (x - 4, y + 14, 8, 5))
        # Hoof sole (slightly lighter)
        pygame.draw.ellipse(screen, hoof_light, (x - 3, y + 15, 6, 3))
        
        # Dewclaw (small bump above hoof)
        pygame.draw.ellipse(screen, hoof_color, (x - 5, y + 12, 3, 3))
    
    def feed(self, duration: float = 3.0):
        """Feed the cow and show a heart"""
        self.is_fed = True
        self.heart_timer = duration
    
    def _draw_heart(self, screen: pygame.Surface, x: int, y: int):
        """Draw a heart above the cow"""
        heart_color = (255, 80, 120)
        pygame.draw.circle(screen, heart_color, (x - 5, y), 5)
        pygame.draw.circle(screen, heart_color, (x + 5, y), 5)
        pygame.draw.polygon(screen, heart_color, [(x - 10, y + 2), (x + 10, y + 2), (x, y + 12)])
