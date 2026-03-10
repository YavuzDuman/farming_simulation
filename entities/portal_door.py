import pygame
import math
import time
from config import GRID_SIZE, BROWN, DARK_BROWN, WHITE, BLACK

class PortalDoor:
    def __init__(self, col, row, x_offset, y_offset, side="right"):
        self.grid_col = col
        self.grid_row = row
        self.side = side
        
        self.width = GRID_SIZE
        self.height = GRID_SIZE * 2
        
        self.x = x_offset + col * GRID_SIZE
        self.y = y_offset + row * GRID_SIZE
        
        self.collision_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.render_rect = self.collision_rect
        
        # Animation
        self.pulse_time = 0
        
    @property
    def sort_y(self):
        return self.y + self.height

    def draw(self, screen):
        self.pulse_time += 0.05
        pulse = (math.sin(self.pulse_time) + 1) / 2  # 0 to 1
        
        # Draw shadow beneath door
        shadow_rect = pygame.Rect(self.x - 5, self.y + self.height - 5, self.width + 10, 10)
        pygame.draw.ellipse(screen, (5, 5, 8), shadow_rect)
        
        # Draw door frame (stone-like ancient portal)
        frame_color = (40, 35, 45) if self.side == "left" else (35, 40, 50)
        pygame.draw.rect(screen, frame_color, self.render_rect, border_radius=5)
        
        # Draw frame details (stone blocks)
        inner_rect = self.render_rect.inflate(-6, -6)
        pygame.draw.rect(screen, (25, 22, 30), inner_rect, border_radius=3)
        
        # Draw inner portal (swirling void)
        portal_rect = inner_rect.inflate(-8, -8)
        
        # Create portal surface with transparency
        portal_surf = pygame.Surface((portal_rect.width, portal_rect.height), pygame.SRCALPHA)
        
        if self.side == "right":
            # Blue/purple portal to dark side (mysterious)
            base_color = (60, 40, 100)
            glow_color = (100, 80, 180)
            particle_color = (150, 120, 255)
        else:
            # Red/orange portal back to farm (warm, inviting)
            base_color = (80, 30, 20)
            glow_color = (150, 60, 30)
            particle_color = (255, 120, 60)
        
        # Draw swirling portal effect
        for i in range(5):
            offset = math.sin(self.pulse_time * 2 + i) * 3
            r = portal_rect.width // 2 - i * 4
            if r > 0:
                alpha = int(150 - i * 25 + pulse * 30)
                pygame.draw.circle(portal_surf, (*glow_color, alpha), 
                                 (portal_rect.width // 2 + int(offset), portal_rect.height // 2), r)
        
        # Draw center void
        pygame.draw.circle(portal_surf, (*base_color, 200), 
                         (portal_rect.width // 2, portal_rect.height // 2), 
                         portal_rect.width // 4)
        
        # Draw floating particles
        for i in range(8):
            angle = self.pulse_time * 2 + i * 0.8
            px = portal_rect.width // 2 + math.cos(angle) * (portal_rect.width // 3)
            py = portal_rect.height // 2 + math.sin(angle) * (portal_rect.height // 3)
            particle_alpha = int(150 + pulse * 50)
            pygame.draw.circle(portal_surf, (*particle_color, particle_alpha), 
                             (int(px), int(py)), 2)
        
        screen.blit(portal_surf, (portal_rect.x, portal_rect.y))
        
        # Draw frame border highlight
        border_color = (60, 55, 70) if self.side == "left" else (55, 60, 75)
        pygame.draw.rect(screen, border_color, self.render_rect, 2, border_radius=5)
        
        # Draw rune-like symbols on frame
        rune_color = (80, 75, 90) if self.side == "left" else (75, 80, 95)
        rune_y_positions = [self.y + 15, self.y + self.height // 2, self.y + self.height - 20]
        for ry in rune_y_positions:
            # Simple rune marks
            pygame.draw.line(screen, rune_color, 
                           (self.x + 5, ry), (self.x + 10, ry - 5), 2)
            pygame.draw.line(screen, rune_color, 
                           (self.x + self.width - 5, ry), (self.x + self.width - 10, ry + 5), 2)
