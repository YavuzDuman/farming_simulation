import pygame
import random
import math
from config import (
    GRID_SIZE, ZOMBIE_SPEED, ZOMBIE_SKIN, ZOMBIE_SKIN_DARK, 
    ZOMBIE_SKIN_LIGHT, ZOMBIE_CLOTHES, ZOMBIE_EYE, ZOMBIE_BLOOD
)

class Zombie:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 36
        self.height = 48
        self.speed = ZOMBIE_SPEED
        self.health = 50
        self.damage = 10
        self.last_attack_time = 0
        self.attack_cooldown = 1.0  # seconds
        
        # Animation state
        self.walk_frame = 0
        self.walk_timer = 0
        self.arm_swing = 0
        
        # Randomize appearance slightly
        self.skin_tint = random.randint(-10, 10)
        self.height_offset = random.randint(-3, 3)
        self.walk_speed_variation = random.uniform(0.8, 1.2)
        
    @property
    def rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, self.width, self.height)
        
    @property
    def sort_y(self):
        return self.y + self.height // 2

    def update(self, player_pos, dt, obstacles=None):
        # Move towards player
        px, py = player_pos
        dx = px - self.x
        dy = py - self.y
        dist = math.sqrt(dx**2 + dy**2)
        
        # Update walk animation
        self.walk_timer += dt
        if self.walk_timer > 0.1:
            self.walk_timer = 0
            self.walk_frame = (self.walk_frame + 1) % 4
        self.arm_swing = math.sin(self.walk_timer * 20) * 5
        
        if dist > 0:
            speed = self.speed * self.walk_speed_variation
            vx = (dx / dist) * speed
            vy = (dy / dist) * speed
            
            new_x = self.x + vx
            new_y = self.y + vy
            
            # Simple collision check with obstacles
            can_move = True
            if obstacles:
                z_rect = pygame.Rect(new_x - self.width // 2, new_y - self.height // 2, self.width, self.height)
                for obs in obstacles:
                    if hasattr(obs, 'collision_rect') and z_rect.colliderect(obs.collision_rect):
                        can_move = False
                        break
            
            if can_move:
                self.x = new_x
                self.y = new_y

    def draw(self, screen):
        # Calculate positions
        body_x = int(self.x)
        body_y = int(self.y) + self.height_offset
        
        # Colors with slight variation
        skin_color = tuple(max(0, min(255, c + self.skin_tint)) for c in ZOMBIE_SKIN)
        skin_dark = tuple(max(0, min(255, c + self.skin_tint)) for c in ZOMBIE_SKIN_DARK)
        skin_light = tuple(max(0, min(255, c + self.skin_tint)) for c in ZOMBIE_SKIN_LIGHT)
        
        # Draw shadow
        shadow_rect = pygame.Rect(body_x - 15, body_y + 18, 30, 8)
        pygame.draw.ellipse(screen, (10, 10, 15), shadow_rect)
        
        # Draw legs (tattered pants)
        leg_spread = 3 + (self.walk_frame % 2) * 2
        # Left leg
        pygame.draw.rect(screen, ZOMBIE_CLOTHES, 
                        (body_x - 8 - leg_spread, body_y + 10, 7, 18))
        pygame.draw.rect(screen, (25, 22, 20), 
                        (body_x - 8 - leg_spread, body_y + 22, 7, 8))  # Feet
        # Right leg
        pygame.draw.rect(screen, ZOMBIE_CLOTHES, 
                        (body_x + 1 + leg_spread, body_y + 10, 7, 18))
        pygame.draw.rect(screen, (25, 22, 20), 
                        (body_x + 1 + leg_spread, body_y + 22, 7, 8))  # Feet
        
        # Draw tattered clothes/torso
        pygame.draw.rect(screen, ZOMBIE_CLOTHES, 
                        (body_x - 10, body_y - 8, 20, 20))
        # Tattered edges
        pygame.draw.polygon(screen, ZOMBIE_CLOTHES, [
            (body_x - 10, body_y + 12),
            (body_x - 12, body_y + 8),
            (body_x - 8, body_y + 15)
        ])
        
        # Draw arms (reaching out, zombie-style)
        arm_offset = int(self.arm_swing)
        # Left arm
        pygame.draw.rect(screen, skin_color, 
                        (body_x - 18 - arm_offset, body_y - 5, 10, 6))
        pygame.draw.rect(screen, skin_dark, 
                        (body_x - 20 - arm_offset, body_y - 3, 8, 12))  # Forearm
        pygame.draw.circle(screen, skin_dark, 
                          (body_x - 18 - arm_offset, body_y + 10), 4)  # Hand
        # Right arm
        pygame.draw.rect(screen, skin_color, 
                        (body_x + 8 + arm_offset, body_y - 5, 10, 6))
        pygame.draw.rect(screen, skin_dark, 
                        (body_x + 12 + arm_offset, body_y - 3, 8, 12))  # Forearm
        pygame.draw.circle(screen, skin_dark, 
                          (body_x + 16 + arm_offset, body_y + 10), 4)  # Hand
        
        # Draw head (rotted, slightly misshapen)
        head_y = body_y - 18
        # Main head shape
        pygame.draw.ellipse(screen, skin_color, 
                           (body_x - 9, head_y - 2, 18, 20))
        # Shadow on head
        pygame.draw.ellipse(screen, skin_dark, 
                           (body_x - 6, head_y + 5, 12, 10))
        
        # Draw glowing eyes
        eye_y = head_y + 5
        # Eye glow effect
        for i in range(3):
            glow_alpha = 100 - i * 30
            glow_size = 4 + i * 2
            glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*ZOMBIE_EYE, glow_alpha), 
                             (glow_size, glow_size), glow_size)
            screen.blit(glow_surf, (body_x - 7 - glow_size, eye_y - glow_size))
            screen.blit(glow_surf, (body_x + 3 - glow_size, eye_y - glow_size))
        # Actual eyes
        pygame.draw.circle(screen, ZOMBIE_EYE, (body_x - 5, eye_y), 3)
        pygame.draw.circle(screen, ZOMBIE_EYE, (body_x + 5, eye_y), 3)
        # Pupils (darker center)
        pygame.draw.circle(screen, (100, 0, 0), (body_x - 5, eye_y), 1)
        pygame.draw.circle(screen, (100, 0, 0), (body_x + 5, eye_y), 1)
        
        # Draw mouth (gaping, scary)
        pygame.draw.ellipse(screen, (30, 20, 20), 
                           (body_x - 4, head_y + 10, 8, 5))
        
        # Draw some blood stains
        pygame.draw.circle(screen, ZOMBIE_BLOOD, (body_x - 6, body_y), 2)
        pygame.draw.circle(screen, ZOMBIE_BLOOD, (body_x + 4, body_y + 5), 2)
        pygame.draw.circle(screen, ZOMBIE_BLOOD, (body_x - 2, head_y + 12), 1)
