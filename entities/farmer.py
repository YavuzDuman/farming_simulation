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
    
    def __init__(self, x: int, y: int, shirt_color: Tuple[int, int, int] = (70, 130, 180),
                 hat_color: Tuple[int, int, int] = (210, 180, 140),
                 pants_color: Tuple[int, int, int] = (85, 85, 85)):
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
        self.pants_color = pants_color  # Custom pants color
        self.pants_shadow = (max(0, pants_color[0]-25), max(0, pants_color[1]-25), max(0, pants_color[2]-25))
        self.boots_color = (101, 67, 33)  # Brown boots
        self.hat_color = hat_color  # Custom hat color
        self.hat_band = (139, 69, 19)  # Brown band
        
        # Tool holding
        self.held_tool = None
        self.tool_swing_angle = 0  # Current swing angle
        self.tool_swing_frame = 0
        self.is_swinging = False
        self.swing_cooldown = 0  # Cooldown timer for sword attacks
        
        # Tool swing animation phases
        self.swing_phase = 'idle'  # idle, windup, swing, follow_through, recover
        self.swing_progress = 0.0  # 0.0 to 1.0 progress through current phase
        
        # Hand positions for tool holding (relative to farmer center) - more natural positions
        self.hand_positions = {
            'down': (6, 12),    # Hand at side
            'up': (6, -8),      # Hand raised
            'left': (-8, 4),    # Hand at side
            'right': (14, 4)    # Hand at side
        }
        
        # Tool rest angles for each direction (natural holding angle)
        self.tool_rest_angles = {
            'down': 75,     # Tool pointing down and slightly forward
            'up': -60,      # Tool raised up
            'left': 160,    # Tool held to left side
            'right': 20     # Tool held to right side
        }
    
    def start_tool_swing(self):
        """Start the tool swing animation with realistic phases"""
        if not self.is_swinging and self.swing_cooldown <= 0:
            self.is_swinging = True
            self.swing_phase = 'windup'
            self.swing_progress = 0.0
            self.tool_swing_frame = 0
            self.swing_cooldown = 25  # 25 frames cooldown
            return True
        return False
    
    def update_swing_cooldown(self):
        """Update swing cooldown each frame"""
        if self.swing_cooldown > 0:
            self.swing_cooldown -= 1
    
    def _update_tool_swing(self):
        """Update the tool swing animation with realistic phases"""
        if not self.is_swinging:
            self.tool_swing_angle = 0
            return
        
        self.tool_swing_frame += 1
        
        # Define phase durations (in frames)
        phase_durations = {
            'windup': 8,          # Pull back/wind up
            'swing': 6,           # Fast swing forward
            'follow_through': 5,  # Continue motion after hit
            'recover': 6          # Return to idle
        }
        
        # Get current phase duration
        current_duration = phase_durations.get(self.swing_phase, 1)
        
        # Update progress
        self.swing_progress += 1.0 / current_duration
        
        if self.swing_progress >= 1.0:
            # Move to next phase
            self.swing_progress = 0.0
            if self.swing_phase == 'windup':
                self.swing_phase = 'swing'
            elif self.swing_phase == 'swing':
                self.swing_phase = 'follow_through'
            elif self.swing_phase == 'follow_through':
                self.swing_phase = 'recover'
            elif self.swing_phase == 'recover':
                self.is_swinging = False
                self.swing_phase = 'idle'
                self.tool_swing_angle = 0
                return
        
        # Calculate swing angle based on phase and direction
        rest_angle = self.tool_rest_angles.get(self.direction, 45)
        
        # Direction multipliers for swing arcs
        if self.direction == 'down':
            # Swing from back to front (downward slash)
            windup_angle = rest_angle - 50   # Pull back
            swing_peak = rest_angle + 60     # Swing through
        elif self.direction == 'up':
            # Upward swing
            windup_angle = rest_angle + 40
            swing_peak = rest_angle - 50
        elif self.direction == 'left':
            # Horizontal swing left
            windup_angle = rest_angle + 50
            swing_peak = rest_angle - 70
        else:  # right
            # Horizontal swing right
            windup_angle = rest_angle - 50
            swing_peak = rest_angle + 70
        
        # Calculate current angle based on phase
        t = self.swing_progress
        if self.swing_phase == 'windup':
            # Smooth ease-out to windup position
            self.tool_swing_angle = rest_angle + (windup_angle - rest_angle) * (1 - (1 - t) ** 2)
        elif self.swing_phase == 'swing':
            # Fast ease-in-out through the swing
            self.tool_swing_angle = windup_angle + (swing_peak - windup_angle) * (t ** 2 * (3 - 2 * t))
        elif self.swing_phase == 'follow_through':
            # Continue past peak and settle
            settle_angle = swing_peak + (rest_angle - swing_peak) * 0.3
            self.tool_swing_angle = swing_peak + (settle_angle - swing_peak) * (1 - (1 - t) ** 2)
        elif self.swing_phase == 'recover':
            # Return to rest position
            current_base = swing_peak + (rest_angle - swing_peak) * 0.3
            self.tool_swing_angle = current_base + (rest_angle - current_base) * t

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
                # Check for collides_with method (used by some obstacles)
                if hasattr(obstacle, 'collides_with'):
                    if obstacle.collides_with(test_rect):
                        can_move = False
                        break
                # Check for collision_rect attribute (used by DarkRock, Stone, etc.)
                elif hasattr(obstacle, 'collision_rect') and obstacle.collision_rect:
                    if test_rect.colliderect(obstacle.collision_rect):
                        can_move = False
                        break
                # Check for rect attribute as fallback
                elif hasattr(obstacle, 'rect') and obstacle.rect:
                    if test_rect.colliderect(obstacle.rect):
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
        
        # Update tool swing animation
        self._update_tool_swing()

        # Walking bob effect
        bob = 0
        leg_offset = 0
        arm_offset = 0
        if self.is_moving:
            bob = int(abs(math.sin(self.walk_cycle * math.pi / 2)) * 2)
            leg_offset = int(math.sin(self.walk_cycle * math.pi) * 5)
            arm_offset = int(math.sin(self.walk_cycle * math.pi) * 4)
        
        cx = self.x + self.width // 2  # Center X
        base_y = self.y + self.height - bob  # Base Y (feet level)
        
        # Shadow under character
        shadow_surf = pygame.Surface((24, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 60), (0, 0, 24, 8))
        screen.blit(shadow_surf, (cx - 12, self.y + self.height - 4))
        
        # === BOOTS ===
        boot_y = base_y - 4
        boots_shadow = (max(0, self.boots_color[0]-30), max(0, self.boots_color[1]-30), max(0, self.boots_color[2]-30))
        
        if self.is_moving:
            # Left boot
            left_boot_x = cx - 8 + (leg_offset if leg_offset > 0 else 0)
            pygame.draw.ellipse(screen, boots_shadow, (left_boot_x - 5, boot_y + abs(leg_offset//2) + 1, 10, 7))
            pygame.draw.ellipse(screen, self.boots_color, (left_boot_x - 5, boot_y + abs(leg_offset//2), 10, 7))
            # Right boot
            right_boot_x = cx + 2 - (leg_offset if leg_offset < 0 else 0)
            pygame.draw.ellipse(screen, boots_shadow, (right_boot_x - 3, boot_y + abs(-leg_offset//2) + 1, 10, 7))
            pygame.draw.ellipse(screen, self.boots_color, (right_boot_x - 3, boot_y + abs(-leg_offset//2), 10, 7))
        else:
            # Standing boots
            pygame.draw.ellipse(screen, boots_shadow, (cx - 10, boot_y + 1, 10, 7))
            pygame.draw.ellipse(screen, self.boots_color, (cx - 10, boot_y, 10, 7))
            pygame.draw.ellipse(screen, boots_shadow, (cx, boot_y + 1, 10, 7))
            pygame.draw.ellipse(screen, self.boots_color, (cx, boot_y, 10, 7))
        
        # === LEGS/PANTS ===
        pants_top = base_y - 18
        pants_bottom = boot_y + 2
        
        if self.is_moving:
            # Animated legs with more realistic shape
            left_leg_offset = leg_offset
            right_leg_offset = -leg_offset
            
            # Left leg
            left_leg_points = [
                (cx - 6, pants_top),
                (cx - 8, pants_top + 8),
                (cx - 9, pants_bottom - abs(left_leg_offset//2)),
                (cx - 3, pants_bottom - abs(left_leg_offset//2)),
                (cx - 2, pants_top + 8),
                (cx - 3, pants_top),
            ]
            pygame.draw.polygon(screen, self.pants_shadow, [(p[0] + 1, p[1]) for p in left_leg_points])
            pygame.draw.polygon(screen, self.pants_color, left_leg_points)
            
            # Right leg
            right_leg_points = [
                (cx + 3, pants_top),
                (cx + 2, pants_top + 8),
                (cx + 3, pants_bottom - abs(right_leg_offset//2)),
                (cx + 9, pants_bottom - abs(right_leg_offset//2)),
                (cx + 8, pants_top + 8),
                (cx + 6, pants_top),
            ]
            pygame.draw.polygon(screen, self.pants_shadow, [(p[0] + 1, p[1]) for p in right_leg_points])
            pygame.draw.polygon(screen, self.pants_color, right_leg_points)
        else:
            # Standing legs
            pygame.draw.rect(screen, self.pants_shadow, (cx - 7, pants_top, 6, 16))
            pygame.draw.rect(screen, self.pants_color, (cx - 8, pants_top, 6, 16))
            pygame.draw.rect(screen, self.pants_shadow, (cx + 3, pants_top, 6, 16))
            pygame.draw.rect(screen, self.pants_color, (cx + 2, pants_top, 6, 16))
        
        # === BODY/TORSO ===
        body_top = base_y - 36 + bob
        
        # Torso - more realistic shape
        torso_points = [
            (cx - 10, body_top + 4),   # left shoulder
            (cx - 11, body_top + 12),  # left side
            (cx - 9, body_top + 20),   # left hip
            (cx + 9, body_top + 20),   # right hip
            (cx + 11, body_top + 12),  # right side
            (cx + 10, body_top + 4),   # right shoulder
        ]
        pygame.draw.polygon(screen, self.shirt_shadow, [(p[0] + 1, p[1] + 1) for p in torso_points])
        pygame.draw.polygon(screen, self.shirt_color, torso_points)
        
        # Collar/V-neck
        collar_points = [
            (cx - 5, body_top),
            (cx, body_top + 8),
            (cx + 5, body_top),
        ]
        pygame.draw.polygon(screen, (220, 220, 220), collar_points)
        
        # === ARMS ===
        arm_y = body_top + 5
        
        if self.is_moving:
            # Swinging arms with elbow joint
            # Left arm
            left_elbow_x = cx - 10 + arm_offset
            left_hand_y = arm_y + 14
            pygame.draw.line(screen, self.shirt_shadow, (cx - 10, arm_y), (left_elbow_x + 1, arm_y + 8), 5)
            pygame.draw.line(screen, self.shirt_color, (cx - 10, arm_y), (left_elbow_x, arm_y + 8), 4)
            pygame.draw.line(screen, self.shirt_shadow, (left_elbow_x + 1, arm_y + 8), (left_elbow_x + 1, left_hand_y), 4)
            pygame.draw.line(screen, self.shirt_color, (left_elbow_x, arm_y + 8), (left_elbow_x, left_hand_y), 3)
            pygame.draw.circle(screen, self.skin_shadow, (int(left_elbow_x) + 1, int(left_hand_y) + 1), 3)
            pygame.draw.circle(screen, self.skin_color, (int(left_elbow_x), int(left_hand_y)), 3)
            
            # Right arm
            right_elbow_x = cx + 10 - arm_offset
            right_hand_y = arm_y + 14
            pygame.draw.line(screen, self.shirt_shadow, (cx + 10, arm_y), (right_elbow_x + 1, arm_y + 8), 5)
            pygame.draw.line(screen, self.shirt_color, (cx + 10, arm_y), (right_elbow_x, arm_y + 8), 4)
            pygame.draw.line(screen, self.shirt_shadow, (right_elbow_x + 1, arm_y + 8), (right_elbow_x + 1, right_hand_y), 4)
            pygame.draw.line(screen, self.shirt_color, (right_elbow_x, arm_y + 8), (right_elbow_x, right_hand_y), 3)
            pygame.draw.circle(screen, self.skin_shadow, (int(right_elbow_x) + 1, int(right_hand_y) + 1), 3)
            pygame.draw.circle(screen, self.skin_color, (int(right_elbow_x), int(right_hand_y)), 3)
        else:
            # Arms at side with elbow
            # Left arm
            pygame.draw.line(screen, self.shirt_shadow, (cx - 10, arm_y), (cx - 11, arm_y + 8), 5)
            pygame.draw.line(screen, self.shirt_color, (cx - 10, arm_y), (cx - 12, arm_y + 8), 4)
            pygame.draw.line(screen, self.shirt_shadow, (cx - 11, arm_y + 8), (cx - 11, arm_y + 14), 4)
            pygame.draw.line(screen, self.shirt_color, (cx - 12, arm_y + 8), (cx - 12, arm_y + 14), 3)
            pygame.draw.circle(screen, self.skin_shadow, (cx - 11, arm_y + 15), 3)
            pygame.draw.circle(screen, self.skin_color, (cx - 12, arm_y + 14), 3)
            
            # Right arm
            pygame.draw.line(screen, self.shirt_shadow, (cx + 10, arm_y), (cx + 11, arm_y + 8), 5)
            pygame.draw.line(screen, self.shirt_color, (cx + 10, arm_y), (cx + 12, arm_y + 8), 4)
            pygame.draw.line(screen, self.shirt_shadow, (cx + 11, arm_y + 8), (cx + 11, arm_y + 14), 4)
            pygame.draw.line(screen, self.shirt_color, (cx + 12, arm_y + 8), (cx + 12, arm_y + 14), 3)
            pygame.draw.circle(screen, self.skin_shadow, (cx + 13, arm_y + 15), 3)
            pygame.draw.circle(screen, self.skin_color, (cx + 12, arm_y + 14), 3)
        
        # === NECK ===
        neck_y = body_top - 6
        pygame.draw.rect(screen, self.skin_shadow, (cx - 3, neck_y + 1, 6, 8))
        pygame.draw.rect(screen, self.skin_color, (cx - 3, neck_y, 6, 8))
        
        # === HEAD ===
        head_y = body_top - 20 + bob
        head_width = 14
        head_height = 16
        
        # Head shadow
        pygame.draw.ellipse(screen, self.skin_shadow,
                           (cx - head_width//2 + 1, head_y + 1, head_width, head_height))
        # Main head
        pygame.draw.ellipse(screen, self.skin_color,
                           (cx - head_width//2, head_y, head_width, head_height))
        
        # === EARS ===
        # Left ear
        pygame.draw.ellipse(screen, self.skin_shadow, (cx - 9, head_y + 5, 3, 5))
        pygame.draw.ellipse(screen, self.skin_color, (cx - 9, head_y + 4, 3, 5))
        # Right ear
        pygame.draw.ellipse(screen, self.skin_shadow, (cx + 6, head_y + 5, 3, 5))
        pygame.draw.ellipse(screen, self.skin_color, (cx + 6, head_y + 4, 3, 5))
        
        # === HAIR ===
        hair_shadow = (max(0, self.hair_color[0]-20), max(0, self.hair_color[1]-20), max(0, self.hair_color[2]-20))
        
        if self.direction != 'down':
            # Hair on top/back
            hair_points = [
                (cx - 6, head_y + 4),
                (cx - 7, head_y - 2),
                (cx - 4, head_y - 4),
                (cx, head_y - 5),
                (cx + 4, head_y - 4),
                (cx + 7, head_y - 2),
                (cx + 6, head_y + 4),
            ]
            pygame.draw.polygon(screen, hair_shadow, [(p[0] + 1, p[1] + 1) for p in hair_points])
            pygame.draw.polygon(screen, self.hair_color, hair_points)
        
        # Side hair (visible from front)
        pygame.draw.ellipse(screen, self.hair_color, (cx - 8, head_y + 2, 4, 7))
        pygame.draw.ellipse(screen, self.hair_color, (cx + 4, head_y + 2, 4, 7))
        
        # === FACE ===
        if self.direction == 'down':
            # Eyes with more detail
            eye_y = head_y + 6
            # Left eye
            pygame.draw.ellipse(screen, (255, 255, 255), (cx - 5, eye_y, 4, 3))
            pygame.draw.circle(screen, (60, 40, 30), (int(cx - 3), int(eye_y + 1)), 1)
            # Right eye
            pygame.draw.ellipse(screen, (255, 255, 255), (cx + 1, eye_y, 4, 3))
            pygame.draw.circle(screen, (60, 40, 30), (int(cx + 3), int(eye_y + 1)), 1)
            
            # Eyebrows
            pygame.draw.line(screen, self.hair_color, (cx - 5, eye_y - 2), (cx - 2, eye_y - 2), 1)
            pygame.draw.line(screen, self.hair_color, (cx + 2, eye_y - 2), (cx + 5, eye_y - 2), 1)
            
            # Nose
            pygame.draw.line(screen, self.skin_shadow, (cx, eye_y + 3), (cx - 1, eye_y + 6), 1)
            pygame.draw.line(screen, self.skin_shadow, (cx - 1, eye_y + 6), (cx + 1, eye_y + 6), 1)
            
            # Mouth (slight smile)
            pygame.draw.arc(screen, (180, 100, 100), (cx - 2, eye_y + 6, 4, 2), 0, math.pi, 1)
        elif self.direction == 'left':
            # Side view - one eye
            pygame.draw.ellipse(screen, (255, 255, 255), (cx - 5, head_y + 6, 3, 3))
            pygame.draw.circle(screen, (60, 40, 30), (int(cx - 4), int(head_y + 7)), 1)
            pygame.draw.line(screen, self.skin_shadow, (cx - 2, head_y + 9), (cx, head_y + 11), 1)
        elif self.direction == 'right':
            # Side view - one eye
            pygame.draw.ellipse(screen, (255, 255, 255), (cx + 2, head_y + 6, 3, 3))
            pygame.draw.circle(screen, (60, 40, 30), (int(cx + 3), int(head_y + 7)), 1)
            pygame.draw.line(screen, self.skin_shadow, (cx, head_y + 9), (cx + 2, head_y + 11), 1)
        # 'up' direction shows back of head (no face features)
        
        # === HAT ===
        hat_base_y = head_y - 4
        hat_shadow = (max(0, self.hat_color[0]-25), max(0, self.hat_color[1]-25), max(0, self.hat_color[2]-25))
        
        # Hat brim (wider ellipse)
        pygame.draw.ellipse(screen, hat_shadow, (cx - 12, hat_base_y + 5, 24, 8))
        pygame.draw.ellipse(screen, self.hat_color, (cx - 12, hat_base_y + 4, 24, 8))
        
        # Hat crown - rounded top
        crown_points = [
            (cx - 8, hat_base_y + 5),
            (cx - 7, hat_base_y - 3),
            (cx - 4, hat_base_y - 6),
            (cx, hat_base_y - 7),
            (cx + 4, hat_base_y - 6),
            (cx + 7, hat_base_y - 3),
            (cx + 8, hat_base_y + 5),
        ]
        pygame.draw.polygon(screen, hat_shadow, [(p[0] + 1, p[1] + 1) for p in crown_points])
        pygame.draw.polygon(screen, self.hat_color, crown_points)
        
        # Hat band
        pygame.draw.ellipse(screen, self.hat_band, (cx - 9, hat_base_y + 2, 18, 4))
        
        # Highlight on hat
        pygame.draw.arc(screen, (min(255, self.hat_color[0] + 30), min(255, self.hat_color[1] + 30), min(255, self.hat_color[2] + 30)),
                       (cx - 5, hat_base_y - 5, 8, 6), 0, math.pi, 1)
        
        # === HELD TOOL ===
        if self.held_tool:
            # Get hand position based on direction
            hand_offset = self.hand_positions.get(self.direction, (6, 4))
            
            # Calculate hand position with bobbing
            hand_x = cx + hand_offset[0]
            hand_y = base_y - 25 + hand_offset[1]
            
            # Apply slight bob to hand when walking
            if self.is_moving:
                hand_y += bob * 0.5
            
            # Calculate the final tool angle
            rest_angle = self.tool_rest_angles.get(self.direction, 45)
            
            # If swinging, use the swing angle; otherwise use rest angle with slight idle sway
            if self.is_swinging:
                final_angle = self.tool_swing_angle
            else:
                # Idle sway - very subtle breathing motion
                idle_sway = math.sin(self.frame_count * 0.05) * 3
                final_angle = rest_angle + idle_sway
            
            # Draw the tool with the calculated angle
            self.held_tool.draw_in_hand(screen, hand_x, hand_y, 
                                       self.direction, final_angle)
    
    def get_grid_position(self) -> Tuple[int, int]:
        """Get the grid cell the farmer is currently on"""
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        col = (center_x - GRID_OFFSET_X) // GRID_SIZE
        row = (center_y - GRID_OFFSET_Y) // GRID_SIZE
        
        col = max(0, min(col, GRID_COLS - 1))
        row = max(0, min(row, GRID_ROWS - 1))
        
        return (col, row)