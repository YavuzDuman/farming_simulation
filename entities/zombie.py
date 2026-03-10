import pygame
import random
import math
from config import (
    GRID_SIZE, ZOMBIE_SPEED, ZOMBIE_SKIN, ZOMBIE_SKIN_DARK, 
    ZOMBIE_SKIN_LIGHT, ZOMBIE_CLOTHES, ZOMBIE_EYE, ZOMBIE_BLOOD,
    HEALTH_RED, HEALTH_BG
)


class Zombie:
    """Regular zombie with 2 health (2 hits with wooden sword)"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 36
        self.height = 48
        self.speed = ZOMBIE_SPEED
        self.max_health = 2  # 2 hits to die
        self.health = self.max_health
        self.damage = 10
        self.last_attack_time = 0
        self.attack_cooldown = 1.0  # seconds
        self.is_alive = True
        self.zombie_type = "regular"  # For distinguishing types
        
        # Animation state
        self.walk_frame = 0
        self.walk_timer = 0
        self.arm_swing = 0
        
        # Hit animation state
        self.is_hit = False
        self.hit_timer = 0
        self.hit_duration = 0.2  # seconds
        self.hit_flash_color = None
        self.knockback_x = 0
        self.knockback_y = 0
        self.knockback_decay = 0.9
        
        # Death animation
        self.is_dying = False
        self.death_timer = 0
        self.death_duration = 0.5  # seconds
        self.death_fade = 255
        
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
        # Handle death animation
        if self.is_dying:
            self.death_timer += dt
            self.death_fade = max(0, int(255 * (1 - self.death_timer / self.death_duration)))
            if self.death_timer >= self.death_duration:
                self.is_alive = False
            return
        
        # Handle hit animation
        if self.is_hit:
            self.hit_timer += dt
            if self.hit_timer >= self.hit_duration:
                self.is_hit = False
                self.hit_timer = 0
                self.hit_flash_color = None
        
        # Apply knockback
        if abs(self.knockback_x) > 0.1 or abs(self.knockback_y) > 0.1:
            self.x += self.knockback_x
            self.y += self.knockback_y
            self.knockback_x *= self.knockback_decay
            self.knockback_y *= self.knockback_decay
        
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
        
        if dist > 0 and not self.is_hit:  # Don't move while being hit
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
    
    def take_damage(self, damage, attacker_x, attacker_y):
        """Take damage from an attack. Returns True if zombie died."""
        if self.is_dying:
            return False
        
        self.health -= damage
        self.is_hit = True
        self.hit_timer = 0
        self.hit_flash_color = (255, 100, 100)  # Red flash
        
        # Calculate knockback direction (away from attacker)
        dx = self.x - attacker_x
        dy = self.y - attacker_y
        dist = max(1, math.sqrt(dx**2 + dy**2))
        knockback_strength = 15
        self.knockback_x = (dx / dist) * knockback_strength
        self.knockback_y = (dy / dist) * knockback_strength
        
        if self.health <= 0:
            self.is_dying = True
            self.death_timer = 0
            return True
        return False

    def draw(self, screen):
        # Handle death animation - fade out
        if self.is_dying:
            self._draw_dying_zombie(screen)
            return
        
        # Calculate positions
        body_x = int(self.x)
        body_y = int(self.y) + self.height_offset
        
        # Colors with slight variation
        skin_color = tuple(max(0, min(255, c + self.skin_tint)) for c in ZOMBIE_SKIN)
        skin_dark = tuple(max(0, min(255, c + self.skin_tint)) for c in ZOMBIE_SKIN_DARK)
        skin_light = tuple(max(0, min(255, c + self.skin_tint)) for c in ZOMBIE_SKIN_LIGHT)
        
        # Apply hit flash effect
        if self.is_hit and self.hit_flash_color:
            # Pulsing flash effect
            flash_intensity = 1 - (self.hit_timer / self.hit_duration)
            skin_color = tuple(int(skin_color[i] * (1 - flash_intensity) + self.hit_flash_color[i] * flash_intensity) for i in range(3))
            skin_dark = tuple(int(skin_dark[i] * (1 - flash_intensity) + self.hit_flash_color[i] * flash_intensity) for i in range(3))
            skin_light = tuple(int(skin_light[i] * (1 - flash_intensity) + self.hit_flash_color[i] * flash_intensity) for i in range(3))
        
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
        
        # Draw health bar above zombie
        self._draw_health_bar(screen, body_x, body_y - 30)
    
    def _draw_health_bar(self, screen, x, y):
        """Draw health bar above zombie"""
        bar_width = 30
        bar_height = 5
        health_ratio = self.health / self.max_health
        
        # Background
        pygame.draw.rect(screen, HEALTH_BG, 
                        (x - bar_width // 2, y, bar_width, bar_height))
        # Health fill
        health_width = int(bar_width * health_ratio)
        if health_width > 0:
            # Color based on health
            if health_ratio > 0.5:
                color = (50, 200, 50)  # Green
            else:
                color = HEALTH_RED
            pygame.draw.rect(screen, color,
                            (x - bar_width // 2, y, health_width, bar_height))
        # Border
        pygame.draw.rect(screen, (100, 100, 100),
                        (x - bar_width // 2, y, bar_width, bar_height), 1)
        
        # Draw hit indicator (damage number)
        if self.is_hit:
            font = pygame.font.SysFont('Arial', 16, bold=True)
            damage_text = font.render("-1", True, (255, 50, 50))
            # Float up animation
            float_offset = int(self.hit_timer * 30)
            screen.blit(damage_text, (x - 8, y - 15 - float_offset))
    
    def _draw_dying_zombie(self, screen):
        """Draw zombie death animation"""
        body_x = int(self.x)
        body_y = int(self.y) + self.height_offset
        
        # Create a surface for the dying zombie with alpha
        death_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
        
        # Calculate alpha based on death timer
        alpha = self.death_fade
        
        # Draw fading zombie on surface
        skin_color = (*ZOMBIE_SKIN, alpha)
        skin_dark = (*ZOMBIE_SKIN_DARK, alpha)
        
        # Draw collapsed zombie (lying down)
        # Body collapsed
        pygame.draw.ellipse(death_surf, skin_color, (10, 25, 40, 20))
        # Head
        pygame.draw.ellipse(death_surf, skin_color, (5, 20, 15, 15))
        # Fading eyes
        eye_alpha = max(0, alpha - 50)
        pygame.draw.circle(death_surf, (*ZOMBIE_EYE, eye_alpha), (12, 28), 3)
        pygame.draw.circle(death_surf, (*ZOMBIE_EYE, eye_alpha), (18, 28), 3)
        
        # Blood pool expanding
        blood_alpha = min(150, int(200 * (self.death_timer / self.death_duration)))
        pygame.draw.ellipse(death_surf, (*ZOMBIE_BLOOD, blood_alpha), (5, 35, 50, 15))
        
        screen.blit(death_surf, (body_x - 30, body_y - 10))


class BruteZombie(Zombie):
    """A larger, tougher zombie with 5 health (5 hits with wooden sword)"""
    
    def __init__(self, x, y):
        super().__init__(x, y)
        # Override for brute stats
        self.width = 48  # Larger
        self.height = 60  # Taller
        self.max_health = 5  # 5 hits to die with wooden sword
        self.health = self.max_health
        self.speed = ZOMBIE_SPEED * 0.7  # Slower but more menacing
        self.damage = 20  # More damage
        self.zombie_type = "brute"
        
        # Larger knockback
        self.knockback_decay = 0.85  # Slower knockback decay
        
        # Death animation longer
        self.death_duration = 0.8
    
    def draw(self, screen):
        """Draw the brute zombie - larger and more menacing"""
        # Handle death animation - fade out
        if self.is_dying:
            self._draw_dying_zombie(screen)
            return
        
        # Calculate positions
        body_x = int(self.x)
        body_y = int(self.y) + self.height_offset
        
        # Brute colors - darker, more decayed look
        brute_skin = (60, 80, 50)  # Darker green-gray
        brute_skin_dark = (40, 60, 35)
        brute_skin_light = (80, 100, 65)
        brute_clothes = (35, 30, 40)  # Dark torn clothes
        
        # Colors with slight variation
        skin_color = tuple(max(0, min(255, c + self.skin_tint)) for c in brute_skin)
        skin_dark = tuple(max(0, min(255, c + self.skin_tint)) for c in brute_skin_dark)
        skin_light = tuple(max(0, min(255, c + self.skin_tint)) for c in brute_skin_light)
        
        # Apply hit flash effect
        if self.is_hit and self.hit_flash_color:
            flash_intensity = 1 - (self.hit_timer / self.hit_duration)
            skin_color = tuple(int(skin_color[i] * (1 - flash_intensity) + self.hit_flash_color[i] * flash_intensity) for i in range(3))
            skin_dark = tuple(int(skin_dark[i] * (1 - flash_intensity) + self.hit_flash_color[i] * flash_intensity) for i in range(3))
            skin_light = tuple(int(skin_light[i] * (1 - flash_intensity) + self.hit_flash_color[i] * flash_intensity) for i in range(3))
        
        # Draw shadow (larger)
        shadow_rect = pygame.Rect(body_x - 22, body_y + 25, 44, 12)
        pygame.draw.ellipse(screen, (10, 10, 15), shadow_rect)
        
        # Draw legs (larger, more muscular)
        leg_spread = 4 + (self.walk_frame % 2) * 3
        # Left leg
        pygame.draw.rect(screen, brute_clothes, 
                        (body_x - 12 - leg_spread, body_y + 12, 10, 24))
        pygame.draw.rect(screen, (25, 22, 20), 
                        (body_x - 12 - leg_spread, body_y + 30, 10, 10))
        # Right leg
        pygame.draw.rect(screen, brute_clothes, 
                        (body_x + 2 + leg_spread, body_y + 12, 10, 24))
        pygame.draw.rect(screen, (25, 22, 20), 
                        (body_x + 2 + leg_spread, body_y + 30, 10, 10))
        
        # Draw torso (larger, bulkier)
        pygame.draw.rect(screen, brute_clothes, 
                        (body_x - 14, body_y - 10, 28, 26))
        # Muscular shoulders
        pygame.draw.circle(screen, skin_dark, (body_x - 12, body_y - 5), 8)
        pygame.draw.circle(screen, skin_dark, (body_x + 12, body_y - 5), 8)
        
        # Draw arms (thicker, more menacing)
        arm_offset = int(self.arm_swing * 0.7)
        # Left arm
        pygame.draw.rect(screen, skin_color, 
                        (body_x - 26 - arm_offset, body_y - 8, 14, 8))
        pygame.draw.rect(screen, skin_dark, 
                        (body_x - 28 - arm_offset, body_y - 4, 12, 16))
        pygame.draw.circle(screen, skin_dark, 
                          (body_x - 24 - arm_offset, body_y + 14), 6)
        # Right arm
        pygame.draw.rect(screen, skin_color, 
                        (body_x + 12 + arm_offset, body_y - 8, 14, 8))
        pygame.draw.rect(screen, skin_dark, 
                        (body_x + 16 + arm_offset, body_y - 4, 12, 16))
        pygame.draw.circle(screen, skin_dark, 
                          (body_x + 22 + arm_offset, body_y + 14), 6)
        
        # Draw head (larger, more menacing)
        head_y = body_y - 22
        # Main head shape
        pygame.draw.ellipse(screen, skin_color, 
                           (body_x - 12, head_y - 4, 24, 26))
        # Shadow on head
        pygame.draw.ellipse(screen, skin_dark, 
                           (body_x - 8, head_y + 6, 16, 12))
        
        # Draw glowing eyes (larger, more intense)
        eye_y = head_y + 6
        # Eye glow effect
        for i in range(3):
            glow_alpha = 120 - i * 35
            glow_size = 5 + i * 2
            glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 50, 50, glow_alpha), 
                             (glow_size, glow_size), glow_size)
            screen.blit(glow_surf, (body_x - 9 - glow_size, eye_y - glow_size))
            screen.blit(glow_surf, (body_x + 3 - glow_size, eye_y - glow_size))
        # Actual eyes (red, more menacing)
        pygame.draw.circle(screen, (255, 80, 80), (body_x - 6, eye_y), 4)
        pygame.draw.circle(screen, (255, 80, 80), (body_x + 6, eye_y), 4)
        # Pupils
        pygame.draw.circle(screen, (150, 0, 0), (body_x - 6, eye_y), 2)
        pygame.draw.circle(screen, (150, 0, 0), (body_x + 6, eye_y), 2)
        
        # Draw mouth (larger, scarier)
        pygame.draw.ellipse(screen, (30, 20, 20), 
                           (body_x - 6, head_y + 14, 12, 6))
        
        # Draw blood stains
        pygame.draw.circle(screen, ZOMBIE_BLOOD, (body_x - 8, body_y + 2), 3)
        pygame.draw.circle(screen, ZOMBIE_BLOOD, (body_x + 6, body_y + 8), 3)
        
        # Draw health bar above zombie (wider for brute)
        self._draw_health_bar(screen, body_x, body_y - 35)
    
    def _draw_health_bar(self, screen, x, y):
        """Draw health bar above brute zombie"""
        bar_width = 40  # Wider for brute
        bar_height = 6
        health_ratio = self.health / self.max_health
        
        # Background
        pygame.draw.rect(screen, HEALTH_BG, 
                        (x - bar_width // 2, y, bar_width, bar_height))
        # Health fill
        health_width = int(bar_width * health_ratio)
        if health_width > 0:
            # Color based on health - brute has more gradient
            if health_ratio > 0.6:
                color = (50, 200, 50)  # Green
            elif health_ratio > 0.3:
                color = (200, 200, 50)  # Yellow
            else:
                color = HEALTH_RED
            pygame.draw.rect(screen, color,
                            (x - bar_width // 2, y, health_width, bar_height))
        # Border
        pygame.draw.rect(screen, (100, 100, 100),
                        (x - bar_width // 2, y, bar_width, bar_height), 1)
        
        # Draw hit indicator (damage number)
        if self.is_hit:
            font = pygame.font.SysFont('Arial', 18, bold=True)
            damage_text = font.render("-1", True, (255, 50, 50))
            float_offset = int(self.hit_timer * 30)
            screen.blit(damage_text, (x - 8, y - 18 - float_offset))
    
    def _draw_dying_zombie(self, screen):
        """Draw brute zombie death animation"""
        body_x = int(self.x)
        body_y = int(self.y) + self.height_offset
        
        # Create a surface for the dying zombie with alpha
        death_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
        
        # Calculate alpha based on death timer
        alpha = self.death_fade
        
        # Brute colors
        brute_skin = (60, 80, 50, alpha)
        brute_skin_dark = (40, 60, 35, alpha)
        
        # Draw collapsed brute (lying down, larger)
        pygame.draw.ellipse(death_surf, brute_skin, (10, 30, 60, 25))
        pygame.draw.ellipse(death_surf, brute_skin_dark, (5, 25, 20, 20))
        
        # Fading eyes
        eye_alpha = max(0, alpha - 50)
        pygame.draw.circle(death_surf, (255, 80, 80, eye_alpha), (18, 35), 4)
        pygame.draw.circle(death_surf, (255, 80, 80, eye_alpha), (28, 35), 4)
        
        # Blood pool expanding (larger)
        blood_alpha = min(180, int(220 * (self.death_timer / self.death_duration)))
        pygame.draw.ellipse(death_surf, (*ZOMBIE_BLOOD, blood_alpha), (5, 45, 70, 20))
        
        screen.blit(death_surf, (body_x - 40, body_y - 15))


class HealthDrop:
    """A health pickup item that rarely drops from zombies"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 24
        self.height = 24
        self.heal_amount = 25  # Heal 25 HP
        self.is_collected = False
        
        # Animation
        self.bob_timer = 0
        self.bob_speed = 3.0
        self.bob_amount = 3
        self.spawn_time = 0
        self.despawn_time = 15.0  # Despawn after 15 seconds
        
        # Glow effect
        self.glow_pulse = 0
    
    @property
    def rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, 
                          self.width, self.height)
    
    @property
    def sort_y(self):
        return self.y + self.height // 2
    
    def update(self, dt):
        """Update animation and despawn timer"""
        self.bob_timer += dt * self.bob_speed
        self.spawn_time += dt
        self.glow_pulse += dt * 4
        
        # Despawn check
        if self.spawn_time >= self.despawn_time:
            self.is_collected = True
    
    def draw(self, screen):
        """Draw the health pickup"""
        if self.is_collected:
            return
        
        # Bob animation
        bob_offset = math.sin(self.bob_timer) * self.bob_amount
        draw_y = self.y + bob_offset
        
        # Glow effect
        glow_intensity = (math.sin(self.glow_pulse) + 1) / 2
        glow_size = int(20 + glow_intensity * 8)
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        glow_alpha = int(80 + glow_intensity * 60)
        pygame.draw.circle(glow_surf, (255, 100, 150, glow_alpha), 
                          (glow_size, glow_size), glow_size)
        screen.blit(glow_surf, (int(self.x) - glow_size, int(draw_y) - glow_size))
        
        # Health pack body (red cross on white background)
        # Background circle
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(draw_y)), 12)
        pygame.draw.circle(screen, (200, 200, 200), (int(self.x), int(draw_y)), 12, 2)
        
        # Red cross
        cross_color = (255, 50, 50)
        # Vertical bar
        pygame.draw.rect(screen, cross_color, 
                        (int(self.x) - 3, int(draw_y) - 8, 6, 16))
        # Horizontal bar
        pygame.draw.rect(screen, cross_color, 
                        (int(self.x) - 8, int(draw_y) - 3, 16, 6))
        
        # Shine effect
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x) - 4, int(draw_y) - 4), 3)
        
        # Despawn warning (flash when about to disappear)
        if self.spawn_time > self.despawn_time - 3:
            flash_alpha = int((math.sin(self.spawn_time * 10) + 1) / 2 * 150)
            flash_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(flash_surf, (255, 255, 255, flash_alpha), (15, 15), 15)
            screen.blit(flash_surf, (int(self.x) - 15, int(draw_y) - 15))
