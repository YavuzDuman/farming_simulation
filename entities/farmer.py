"""
Farmer Character Entity - Realistic walking character
"""
import pygame
import math
from typing import Tuple, List
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PLAYER_SPEED, PLAYER_SIZE, GRID_SIZE, GRID_COLS, GRID_ROWS, GRID_OFFSET_X, GRID_OFFSET_Y


class Farmer:
    """The player-controlled farmer character with realistic appearance"""
    
    def __init__(self, x: int, y: int, shirt_color: Tuple[int, int, int] = (70, 130, 180)):
        self.x = x
        self.y = y
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE + 8  # Slightly taller for better proportions
        self.speed = PLAYER_SPEED
        self.direction = 'down'
        self.walk_cycle = 0.0
        self.is_moving = False
        self.frame_count = 0
        
        # Colors for realistic farmer
        self.skin_color = (255, 218, 185)  # Peach skin
        self.skin_shadow = (235, 190, 155)
        self.hair_color = (101, 67, 33)  # Brown hair
        self.shirt_color = shirt_color  # Custom shirt color
        self.shirt_shadow = (max(0, shirt_color[0]-30), max(0, shirt_color[1]-30), max(0, shirt_color[2]-30))
        self.pants_color = (85, 85, 85)  # Dark gray pants
        self.pants_shadow = (60, 60, 60)
        self.boots_color = (101, 67, 33)  # Brown boots
        self.hat_color = (210, 180, 140)  # Tan straw hat
        self.hat_band = (139, 69, 19)  # Brown band
        
        # Tool holding
        self.held_tool = None
        self.tool_shake_angle = 0
        self.tool_swing_frame = 0
        self.is_swinging = False
        self.swing_cooldown = 0  # Cooldown timer for sword attacks
        
        # Hand positions for tool holding (relative to farmer center)
        self.hand_positions = {
            'down': (0, 8),
            'up': (0, -12),
            'left': (-10, 0),
            'right': (10, 0)
        }
    
    def start_tool_swing(self):
        """Start the tool swing animation"""
        if not self.is_swinging and self.swing_cooldown <= 0:
            self.is_swinging = True
            self.tool_swing_frame = 0
            self.swing_cooldown = 20  # 20 frames cooldown (~0.33 seconds at 60fps)
            return True
        return False
    
    def update_swing_cooldown(self):
        """Update swing cooldown each frame"""
        if self.swing_cooldown > 0:
            self.swing_cooldown -= 1

    @property
    def render_rect(self) -> pygame.Rect:
        """Get the full rendering rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    @property
    def rect(self) -> pygame.Rect:
        """Get the rectangle for collision detection (feet area)"""
        return pygame.Rect(
            self.x + 6, 
            self.y + self.height - 12, 
            self.width - 12, 
            10
        )
    
    @property
    def sort_y(self) -> int:
        """Y position for depth sorting (feet position)"""
        return self.y + self.height
    
    def move(self, dx: int, dy: int, bounds: pygame.Rect, obstacles: list = None):
        """Move the farmer, respecting boundaries and obstacles"""
        if dx > 0:
            self.direction = 'right'
        elif dx < 0:
            self.direction = 'left'
        elif dy > 0:
            self.direction = 'down'
        elif dy < 0:
            self.direction = 'up'
        
        self.is_moving = dx != 0 or dy != 0
        if self.is_moving:
            self.walk_cycle = (self.walk_cycle + 0.15) % 4
        
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        
        # Create test rect for collision
        test_rect = pygame.Rect(
            new_x + 6,
            new_y + self.height - 12,
            self.width - 12,
            10
        )
        
        can_move = True
        if obstacles:
            for obstacle in obstacles:
                if hasattr(obstacle, 'collides_with'):
                    if obstacle.collides_with(test_rect):
                        can_move = False
                        break
        
        if can_move:
            if bounds.left <= new_x <= bounds.right - self.width:
                self.x = new_x
            if bounds.top <= new_y <= bounds.bottom - self.height:
                self.y = new_y
    
    def draw(self, screen: pygame.Surface):
        """Draw the realistic farmer character"""
        self.frame_count += 1
        
        # Handle tool swinging animation
        if self.is_swinging:
            self.tool_swing_frame += 1
            # Enhanced swing logic for more realistic motion
            # Fast windup, powerful swing through, quick recovery
            total_frames = 15  # Slightly longer animation
            if self.tool_swing_frame <= 4:
                # Windup phase: raise the weapon (0 to 50 degrees)
                progress = self.tool_swing_frame / 4.0
                self.tool_shake_angle = int(50 * progress)
            elif self.tool_swing_frame <= 9:
                # Swing phase: slash through (50 to -30 degrees)
                progress = (self.tool_swing_frame - 4) / 5.0
                self.tool_shake_angle = int(50 - 80 * progress)
            elif self.tool_swing_frame <= 12:
                # Follow through: continue momentum (-30 to -10 degrees)
                progress = (self.tool_swing_frame - 9) / 3.0
                self.tool_shake_angle = int(-30 + 20 * progress)
            elif self.tool_swing_frame <= total_frames:
                # Recovery: return to neutral
                progress = (self.tool_swing_frame - 12) / 3.0
                self.tool_shake_angle = int(-10 * (1 - progress))
            else:
                self.is_swinging = False
                self.tool_swing_frame = 0
                self.tool_shake_angle = 0

        # Walking bob effect
        bob = 0
        leg_offset = 0
        arm_offset = 0
        if self.is_moving:
            bob = int(abs(math.sin(self.walk_cycle * math.pi / 2)) * 2) # Increased bob for realism
            leg_offset = int(math.sin(self.walk_cycle * math.pi) * 5) # Slightly wider stride
            arm_offset = int(math.sin(self.walk_cycle * math.pi) * 4)
        
        cx = self.x + self.width // 2  # Center X
        base_y = self.y + self.height - bob  # Base Y (feet level)
        
        # Shadow
        pygame.draw.ellipse(screen, (30, 30, 30), 
                           (cx - 10, self.y + self.height - 4, 20, 6))
        
        # === FEET/BOOTS ===
        boot_y = base_y - 4
        if self.is_moving:
            # Left boot
            left_boot_x = cx - 8 + (leg_offset if leg_offset > 0 else 0)
            pygame.draw.ellipse(screen, self.boots_color, 
                              (left_boot_x - 4, boot_y + abs(leg_offset//2), 8, 6))
            # Right boot
            right_boot_x = cx + 2 - (leg_offset if leg_offset < 0 else 0)
            pygame.draw.ellipse(screen, self.boots_color, 
                              (right_boot_x - 4, boot_y + abs(-leg_offset//2), 8, 6))
        else:
            pygame.draw.ellipse(screen, self.boots_color, (cx - 9, boot_y, 8, 6))
            pygame.draw.ellipse(screen, self.boots_color, (cx + 1, boot_y, 8, 6))
        
        # === LEGS/PANTS ===
        pants_top = base_y - 16
        if self.is_moving:
            # Animated legs
            left_leg_offset = leg_offset
            right_leg_offset = -leg_offset
            
            # Left leg
            left_points = [
                (cx - 6, pants_top),
                (cx - 8, boot_y - 2 + abs(left_leg_offset//2)),
            ]
            pygame.draw.line(screen, self.pants_color, left_points[0], left_points[1], 6)
            pygame.draw.line(screen, self.pants_shadow, 
                           (left_points[0][0] + 2, left_points[0][1]), 
                           (left_points[1][0] + 2, left_points[1][1]), 2)
            
            # Right leg
            right_points = [
                (cx + 6, pants_top),
                (cx + 8, boot_y - 2 + abs(right_leg_offset//2)),
            ]
            pygame.draw.line(screen, self.pants_color, right_points[0], right_points[1], 6)
            pygame.draw.line(screen, self.pants_shadow,
                           (right_points[0][0] + 2, right_points[0][1]),
                           (right_points[1][0] + 2, right_points[1][1]), 2)
        else:
            # Standing legs
            pygame.draw.rect(screen, self.pants_color, (cx - 8, pants_top, 6, 14))
            pygame.draw.rect(screen, self.pants_color, (cx + 2, pants_top, 6, 14))
            pygame.draw.rect(screen, self.pants_shadow, (cx - 2, pants_top, 4, 14))
        
        # === BODY/TORSO ===
        body_top = base_y - 32 + bob
        body_width = 16
        body_height = 18
        
        # Body shadow (3D effect)
        pygame.draw.ellipse(screen, self.shirt_shadow,
                           (cx - body_width//2 + 2, body_top + 2, body_width, body_height))
        # Main body
        pygame.draw.ellipse(screen, self.shirt_color,
                           (cx - body_width//2, body_top, body_width, body_height))
        
        # Collar
        pygame.draw.ellipse(screen, (200, 200, 200),
                           (cx - 5, body_top - 2, 10, 6))
        
        # === ARMS ===
        arm_y = body_top + 4
        
        if self.is_moving:
            # Swinging arms
            left_arm_angle = math.sin(self.walk_cycle * math.pi) * 0.3
            right_arm_angle = -left_arm_angle
            
            # Left arm
            pygame.draw.line(screen, self.shirt_color,
                           (cx - 8, arm_y),
                           (cx - 12 + arm_offset, arm_y + 12), 5)
            # Left hand
            pygame.draw.circle(screen, self.skin_color, 
                             (int(cx - 12 + arm_offset), int(arm_y + 14)), 4)
            
            # Right arm
            pygame.draw.line(screen, self.shirt_color,
                           (cx + 8, arm_y),
                           (cx + 12 - arm_offset, arm_y + 12), 5)
            # Right hand
            pygame.draw.circle(screen, self.skin_color,
                             (int(cx + 12 - arm_offset), int(arm_y + 14)), 4)
        else:
            # Arms at side
            pygame.draw.line(screen, self.shirt_color, (cx - 8, arm_y), (cx - 9, arm_y + 10), 5)
            pygame.draw.line(screen, self.shirt_color, (cx + 8, arm_y), (cx + 9, arm_y + 10), 5)
            pygame.draw.circle(screen, self.skin_color, (cx - 9, arm_y + 12), 4)
            pygame.draw.circle(screen, self.skin_color, (cx + 9, arm_y + 12), 4)
        
        # === HEAD ===
        head_y = body_top - 14 + bob
        head_width = 14
        head_height = 16
        
        # Head shadow
        pygame.draw.ellipse(screen, self.skin_shadow,
                           (cx - head_width//2 + 1, head_y + 1, head_width, head_height))
        # Main head
        pygame.draw.ellipse(screen, self.skin_color,
                           (cx - head_width//2, head_y, head_width, head_height))
        
        # === HAIR ===
        if self.direction != 'down':
            # Hair on top/back
            pygame.draw.arc(screen, self.hair_color,
                           (cx - 8, head_y - 2, 16, 12), 0, math.pi, 3)
        
        # === FACE ===
        if self.direction == 'down':
            # Eyes
            pygame.draw.circle(screen, (60, 40, 30), (cx - 3, head_y + 6), 2)
            pygame.draw.circle(screen, (60, 40, 30), (cx + 3, head_y + 6), 2)
            # Eyebrows
            pygame.draw.line(screen, self.hair_color, (cx - 5, head_y + 3), (cx - 1, head_y + 4), 1)
            pygame.draw.line(screen, self.hair_color, (cx + 1, head_y + 4), (cx + 5, head_y + 3), 1)
            # Nose
            pygame.draw.line(screen, self.skin_shadow, (cx, head_y + 7), (cx, head_y + 10), 2)
            # Mouth (slight smile)
            pygame.draw.arc(screen, (180, 100, 100),
                           (cx - 3, head_y + 9, 6, 4), 0, math.pi, 1)
        elif self.direction == 'left':
            # Side view - one eye
            pygame.draw.circle(screen, (60, 40, 30), (cx - 4, head_y + 6), 2)
            pygame.draw.line(screen, self.skin_shadow, (cx - 2, head_y + 8), (cx, head_y + 10), 1)
        elif self.direction == 'right':
            # Side view - one eye
            pygame.draw.circle(screen, (60, 40, 30), (cx + 4, head_y + 6), 2)
            pygame.draw.line(screen, self.skin_shadow, (cx, head_y + 8), (cx + 2, head_y + 10), 1)
        # 'up' direction shows back of head (no face features)
        
        # === HAT ===
        hat_base_y = head_y - 4
        
        # Hat brim (wider ellipse)
        pygame.draw.ellipse(screen, self.hat_color,
                           (cx - 12, hat_base_y + 4, 24, 8))
        # Hat crown
        pygame.draw.ellipse(screen, self.hat_color,
                           (cx - 8, hat_base_y - 4, 16, 12))
        # Hat band
        pygame.draw.ellipse(screen, self.hat_band,
                           (cx - 9, hat_base_y + 2, 18, 4))
        
        # Straw texture lines on hat
        for i in range(-4, 5, 2):
            pygame.draw.line(screen, (190, 160, 120),
                           (cx + i - 1, hat_base_y - 2),
                           (cx + i + 1, hat_base_y + 6), 1)
        
        # === HELD TOOL ===
        if self.held_tool:
            hand_offset = self.hand_positions.get(self.direction, (0, 0))
            hand_x = cx + hand_offset[0]
            hand_y = base_y - 20 + hand_offset[1]  # Position at hand level
            self.held_tool.draw_in_hand(screen, hand_x, hand_y, 
                                       self.direction, self.tool_shake_angle)
    
    def get_grid_position(self) -> Tuple[int, int]:
        """Get the grid cell the farmer is currently on"""
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        col = (center_x - GRID_OFFSET_X) // GRID_SIZE
        row = (center_y - GRID_OFFSET_Y) // GRID_SIZE
        
        col = max(0, min(col, GRID_COLS - 1))
        row = max(0, min(row, GRID_ROWS - 1))
        
        return (col, row)