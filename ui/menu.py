"""
Main Menu UI
"""
import pygame
import sqlite3
import json
from typing import Callable, Optional, List, Dict
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GREEN, DARK_GREEN, 
    YELLOW, GRAY, LIGHT_GRAY, MENU_TITLE_SIZE, MENU_BUTTON_SIZE, FONT_NAME, SKY_BLUE
)


class Button:
    """A clickable button"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 text: str, color: tuple, hover_color: tuple):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events, returns True if clicked"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        """Draw the button"""
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=10)
        
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class TextInput:
    """A text input field"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 placeholder: str = "Enter username..."):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
    
    def handle_event(self, event: pygame.event.Event):
        """Handle input events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False
            elif len(self.text) < 15:  # Limit username length
                if event.unicode.isalnum() or event.unicode in '_-':
                    self.text += event.unicode
    
    def update(self, dt: float):
        """Update cursor blink"""
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        """Draw the input field"""
        # Draw background
        color = WHITE if self.active else LIGHT_GRAY
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        
        # Draw border
        border_color = GREEN if self.active else GRAY
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=5)
        
        # Draw text or placeholder
        if self.text:
            text_surface = font.render(self.text, True, BLACK)
        else:
            text_surface = font.render(self.placeholder, True, GRAY)
        
        text_rect = text_surface.get_rect(midleft=(self.rect.left + 10, self.rect.centery))
        screen.blit(text_surface, text_rect)
        
        # Draw cursor
        if self.active and self.cursor_visible:
            cursor_x = text_rect.right + 2
            pygame.draw.line(screen, BLACK, 
                           (cursor_x, self.rect.top + 5),
                           (cursor_x, self.rect.bottom - 5), 2)
    
    def get_text(self) -> str:
        """Get the current text"""
        return self.text


class Menu:
    """Main menu screen with character design"""
    
    def __init__(self, on_start_game: Callable[[str, tuple, tuple, tuple, Optional[int]], None]):
        self.on_start_game = on_start_game
        
        # Fonts
        self.title_font = pygame.font.SysFont(FONT_NAME, MENU_TITLE_SIZE, bold=True)
        self.button_font = pygame.font.SysFont(FONT_NAME, MENU_BUTTON_SIZE)
        self.input_font = pygame.font.SysFont(FONT_NAME, MENU_BUTTON_SIZE)
        self.save_list_font = pygame.font.SysFont(FONT_NAME, 24)
        self.label_font = pygame.font.SysFont(FONT_NAME, 24)
        
        # Title
        self.title_text = "Farm Life"
        
        # Layout constants
        self.left_panel_width = 500
        self.left_panel_x = 100
        self.right_panel_x = 700
        self.panel_y_start = 250
        
        # Username input (left side)
        input_width = 350
        input_height = 50
        input_x = self.left_panel_x + (self.left_panel_width - input_width) // 2
        input_y = self.panel_y_start
        self.username_input = TextInput(input_x, input_y, input_width, input_height)
        
        # Color palettes for character design
        self.color_palette = [
            (70, 130, 180),   # Steel Blue
            (180, 70, 70),    # Red
            (70, 180, 70),    # Green
            (180, 180, 70),   # Yellow
            (180, 70, 180),   # Purple
            (70, 180, 180),   # Cyan
            (210, 180, 140),  # Tan
            (85, 85, 85),     # Gray
            (200, 120, 50),   # Orange
            (150, 75, 0),     # Brown
            (255, 192, 203),  # Pink
            (50, 50, 50),     # Black
        ]
        
        # Hat color selection
        self.selected_hat_idx = 6  # Default tan
        self.hat_swatches = []
        
        # Shirt color selection
        self.selected_shirt_idx = 0  # Default steel blue
        self.shirt_swatches = []
        
        # Pants color selection
        self.selected_pants_idx = 7  # Default gray
        self.pants_swatches = []
        
        # Create color swatches for each category
        self._create_color_swatches()

        # Start and load buttons (left side, below username)
        button_width = 160
        button_height = 45
        button_y = input_y + 100
        button_spacing = 20
        buttons_total_width = button_width * 2 + button_spacing
        button_x = self.left_panel_x + (self.left_panel_width - buttons_total_width) // 2
        self.start_button = Button(
            button_x, button_y, button_width, button_height,
            "Start New Game", GREEN, DARK_GREEN
        )
        self.load_button = Button(
            button_x + button_width + button_spacing, button_y, button_width, button_height,
            "Load Game", (80, 120, 180), (100, 140, 200)
        )
        
        # Character preview position (left side of the right panel, next to color selectors)
        self.preview_x = self.right_panel_x + 90
        self.preview_y = 380
        self.preview_scale = 1.8  # Smaller scale for the character

        # Saved games list
        self.saves: List[Dict[str, str]] = []
        self.save_buttons: List[Button] = []
        self.delete_buttons: List[Button] = []
        self.selected_save_index: Optional[int] = None
        self.show_load_panel = False
        self.show_delete_confirm = False
        self.pending_delete_save_id: Optional[int] = None
        self.save_area_rect = pygame.Rect(150, 590, SCREEN_WIDTH - 300, 320)
        self._refresh_save_list()
        self.last_save_refresh = 0.0
        self._create_load_panel_buttons()
        self._create_confirm_dialog_buttons()
        
        # Instructions
        self.instructions = [
            "Use WASD keys to move your farmer",
            "Click on grid cells to select them",
            "Press ESC to pause the game"
        ]
    
    def _create_color_swatches(self):
        """Create color swatch rectangles for hat, shirt, and pants - positioned to the right of character preview"""
        swatch_size = 28
        swatch_spacing = 6
        swatches_per_row = 6
        
        # Color swatches start position (to the right of character preview)
        start_x = self.right_panel_x + 200
        
        # Hat swatches - with space for label above
        hat_y = 290  # Adjusted for label space
        for i, color in enumerate(self.color_palette):
            row = i // swatches_per_row
            col = i % swatches_per_row
            x = start_x + col * (swatch_size + swatch_spacing)
            y = hat_y + row * (swatch_size + swatch_spacing)
            self.hat_swatches.append(pygame.Rect(x, y, swatch_size, swatch_size))
        
        # Shirt swatches - with space for label above
        shirt_y = 390  # Adjusted for label space
        for i, color in enumerate(self.color_palette):
            row = i // swatches_per_row
            col = i % swatches_per_row
            x = start_x + col * (swatch_size + swatch_spacing)
            y = shirt_y + row * (swatch_size + swatch_spacing)
            self.shirt_swatches.append(pygame.Rect(x, y, swatch_size, swatch_size))
        
        # Pants swatches - with space for label above
        pants_y = 490  # Adjusted for label space
        for i, color in enumerate(self.color_palette):
            row = i // swatches_per_row
            col = i % swatches_per_row
            x = start_x + col * (swatch_size + swatch_spacing)
            y = pants_y + row * (swatch_size + swatch_spacing)
            self.pants_swatches.append(pygame.Rect(x, y, swatch_size, swatch_size))
    
    def _get_selected_colors(self) -> tuple:
        """Get the currently selected hat, shirt, and pants colors"""
        hat_color = self.color_palette[self.selected_hat_idx]
        shirt_color = self.color_palette[self.selected_shirt_idx]
        pants_color = self.color_palette[self.selected_pants_idx]
        return hat_color, shirt_color, pants_color
    
    def handle_event(self, event: pygame.event.Event):
        """Handle menu events"""
        self.username_input.handle_event(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Check hat color swatches
                for i, rect in enumerate(self.hat_swatches):
                    if rect.collidepoint(event.pos):
                        self.selected_hat_idx = i
                        return
                # Check shirt color swatches
                for i, rect in enumerate(self.shirt_swatches):
                    if rect.collidepoint(event.pos):
                        self.selected_shirt_idx = i
                        return
                # Check pants color swatches
                for i, rect in enumerate(self.pants_swatches):
                    if rect.collidepoint(event.pos):
                        self.selected_pants_idx = i
                        return
        
        # Önce silme onay penceresini kontrol et ki,
        # üstteki dialog, alttaki load panel yerine tıklamaları yakalasın.
        if self.show_delete_confirm:
            self._handle_confirm_dialog_event(event)
            return  # Onay penceresi açıkken diğer eventleri işleme
        
        if self.show_load_panel:
            self._handle_load_panel_event(event)
            return  # Load panel açıkken diğer eventleri işleme
        
        if self.start_button.handle_event(event):
            username = self.username_input.get_text().strip()
            if username:
                hat_color, shirt_color, pants_color = self._get_selected_colors()
                self.on_start_game(username, hat_color, shirt_color, pants_color, None)

        if self.load_button.handle_event(event):
            self._refresh_save_list()
            self.show_load_panel = True
            self.selected_save_index = None
            # Create buttons immediately when panel is shown
            self._create_load_panel_buttons()

    def _handle_load_panel_event(self, event: pygame.event.Event):
        """Handle events within the load panel overlay."""
        # Ensure buttons exist
        if not hasattr(self, 'close_button') or self.close_button is None:
            self._create_load_panel_buttons()
        
        if event.type == pygame.MOUSEMOTION:
            # Update hover states for buttons
            if hasattr(self, 'close_button') and self.close_button:
                self.close_button.is_hovered = self.close_button.rect.collidepoint(event.pos)
            if hasattr(self, 'load_confirm_button') and self.load_confirm_button:
                self.load_confirm_button.is_hovered = self.load_confirm_button.rect.collidepoint(event.pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check close button
            if self.close_button and self.close_button.rect.collidepoint(event.pos):
                self.show_load_panel = False
                return
            
            # Check load confirm button
            if self.load_confirm_button and self.load_confirm_button.rect.collidepoint(event.pos):
                if self.selected_save_index is not None:
                    save = self.saves[self.selected_save_index]
                    username = save.get("name") or self.username_input.get_text().strip()
                    hat_color = save.get("hat_color", self.color_palette[self.selected_hat_idx])
                    shirt_color = save.get("shirt_color", self.color_palette[self.selected_shirt_idx])
                    pants_color = save.get("pants_color", self.color_palette[self.selected_pants_idx])
                    if username:
                        self.on_start_game(username, tuple(hat_color), tuple(shirt_color), tuple(pants_color), save.get("id"))
                return
            
            # Check save item clicks
            panel_width = 700
            panel_height = 450
            panel_x = (SCREEN_WIDTH - panel_width) // 2
            panel_y = (SCREEN_HEIGHT - panel_height) // 2
            list_x = panel_x + 20
            list_y = panel_y + 60
            list_width = panel_width - 40
            item_height = 50
            
            for index, save in enumerate(self.saves):
                item_y = list_y + index * item_height
                if item_y + item_height > panel_y + panel_height - 80:
                    break
                
                # Item rect for selection
                item_rect = pygame.Rect(list_x, item_y, list_width - 100, item_height - 8)
                
                # Delete button rect
                delete_rect = pygame.Rect(list_x + list_width - 90, item_y, 80, item_height - 8)
                
                if delete_rect.collidepoint(event.pos):
                    save_id = self.saves[index]["id"]
                    self.pending_delete_save_id = save_id
                    self.show_delete_confirm = True
                    return
                
                if item_rect.collidepoint(event.pos):
                    self.selected_save_index = index
                    return
    
    def _handle_confirm_dialog_event(self, event: pygame.event.Event):
        """Handle events within the confirmation dialog."""
        if event.type == pygame.MOUSEMOTION:
            if hasattr(self, 'yes_button'):
                self.yes_button.is_hovered = self.yes_button.rect.collidepoint(event.pos)
            if hasattr(self, 'no_button'):
                self.no_button.is_hovered = self.no_button.rect.collidepoint(event.pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if hasattr(self, 'yes_button') and self.yes_button.rect.collidepoint(event.pos):
                if self.pending_delete_save_id is not None:
                    self._delete_save(self.pending_delete_save_id)
                    self.pending_delete_save_id = None
                self.show_delete_confirm = False
                return
            
            if hasattr(self, 'no_button') and self.no_button.rect.collidepoint(event.pos):
                self.pending_delete_save_id = None
                self.show_delete_confirm = False
                return
    
    def update(self, dt: float):
        """Update menu state"""
        self.username_input.update(dt)
        self.last_save_refresh += dt
        if self.last_save_refresh >= 1.0:
            self._refresh_save_list()
            self.last_save_refresh = 0.0

    def _create_load_panel_buttons(self):
        """Create buttons for the load panel overlay."""
        panel_width = 700
        panel_height = 450
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        
        self.close_button = Button(
            panel_x + panel_width - 110,
            panel_y + 15,
            90,
            36,
            "Close",
            (120, 120, 120),
            (150, 150, 150)
        )
        self.load_confirm_button = Button(
            panel_x + panel_width // 2 - 80,
            panel_y + panel_height - 60,
            160,
            40,
            "Load Selected",
            GREEN,
            DARK_GREEN
        )
    
    def _create_confirm_dialog_buttons(self):
        """Create buttons for the confirmation dialog."""
        dialog_width = 400
        dialog_height = 180
        dialog_x = (SCREEN_WIDTH - dialog_width) // 2
        dialog_y = (SCREEN_HEIGHT - dialog_height) // 2
        
        self.yes_button = Button(
            dialog_x + dialog_width // 2 - 130,
            dialog_y + dialog_height - 60,
            100,
            40,
            "Yes",
            (180, 70, 70),
            (200, 90, 90)
        )
        self.no_button = Button(
            dialog_x + dialog_width // 2 + 30,
            dialog_y + dialog_height - 60,
            100,
            40,
            "No",
            (100, 100, 100),
            (130, 130, 130)
        )
    
    def draw(self, screen: pygame.Surface):
        """Draw the menu"""
        # Draw background
        screen.fill(SKY_BLUE)
        self._draw_farm_background(screen)
        
        # Draw title with shadow
        title_shadow = self.title_font.render(self.title_text, True, (0, 50, 0))
        shadow_rect = title_shadow.get_rect(center=(SCREEN_WIDTH // 2 + 3, 80 + 3))
        screen.blit(title_shadow, shadow_rect)
        
        title_surface = self.title_font.render(self.title_text, True, YELLOW)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 80))
        screen.blit(title_surface, title_rect)
        
        # Draw subtitle
        subtitle_font = pygame.font.SysFont(FONT_NAME, 28)
        subtitle = subtitle_font.render("A Grid-Based Farming Adventure", True, DARK_GREEN)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 140))
        screen.blit(subtitle, subtitle_rect)
        
        # === LEFT PANEL: Username and Buttons ===
        # Draw username label
        label = self.label_font.render("Enter your name:", True, BLACK)
        label_rect = label.get_rect(center=(self.left_panel_x + self.left_panel_width // 2, self.panel_y_start - 30))
        screen.blit(label, label_rect)
        
        # Draw input and buttons
        self.username_input.draw(screen, self.input_font)
        self.start_button.draw(screen, self.button_font)
        self.load_button.draw(screen, self.button_font)
        
        # === RIGHT PANEL: Character Design ===
        # Draw panel background
        panel_rect = pygame.Rect(self.right_panel_x, 220, 520, 520)
        pygame.draw.rect(screen, (255, 255, 255, 180), panel_rect, border_radius=15)
        pygame.draw.rect(screen, (100, 100, 100), panel_rect, 3, border_radius=15)
        
        # Draw "Character Design" header
        design_title = self.label_font.render("Character Design", True, BLACK)
        design_title_rect = design_title.get_rect(center=(self.right_panel_x + 260, 250))
        screen.blit(design_title, design_title_rect)
        
        # Draw character preview (left side)
        self._draw_character_preview(screen)
        
        # Draw color selection labels and swatches (right side of preview)
        # Hat colors
        hat_label = self.label_font.render("Hat Color:", True, BLACK)
        screen.blit(hat_label, (self.right_panel_x + 200, 268))
        self._draw_color_swatches(screen, self.hat_swatches, self.selected_hat_idx)
        
        # Shirt colors
        shirt_label = self.label_font.render("Shirt Color:", True, BLACK)
        screen.blit(shirt_label, (self.right_panel_x + 200, 368))
        self._draw_color_swatches(screen, self.shirt_swatches, self.selected_shirt_idx)
        
        # Pants colors
        pants_label = self.label_font.render("Pants Color:", True, BLACK)
        screen.blit(pants_label, (self.right_panel_x + 200, 468))
        self._draw_color_swatches(screen, self.pants_swatches, self.selected_pants_idx)
        
        # Draw instructions
        instruction_font = pygame.font.SysFont(FONT_NAME, 20)
        y_start = SCREEN_HEIGHT - 80
        for i, instruction in enumerate(self.instructions):
            inst_surface = instruction_font.render(instruction, True, BLACK)
            inst_rect = inst_surface.get_rect(center=(SCREEN_WIDTH // 2, y_start + i * 25))
            screen.blit(inst_surface, inst_rect)
        
        # Draw load panel overlay if active
        if self.show_load_panel:
            self._draw_load_panel(screen)
        
        # Draw confirmation dialog if active
        if self.show_delete_confirm:
            self._draw_confirm_dialog(screen)
    
    def _draw_color_swatches(self, screen: pygame.Surface, swatches: list, selected_idx: int):
        """Draw color swatches with selection indicator"""
        for i, rect in enumerate(swatches):
            color = self.color_palette[i]
            pygame.draw.rect(screen, color, rect, border_radius=5)
            if i == selected_idx:
                pygame.draw.rect(screen, WHITE, rect, 3, border_radius=5)
                pygame.draw.rect(screen, BLACK, rect, 1, border_radius=5)
            else:
                pygame.draw.rect(screen, BLACK, rect, 1, border_radius=5)
    
    def _draw_character_preview(self, screen: pygame.Surface):
        """Draw a realistic preview of the character with selected colors"""
        cx = self.preview_x
        cy = self.preview_y
        scale = self.preview_scale
        
        hat_color = self.color_palette[self.selected_hat_idx]
        shirt_color = self.color_palette[self.selected_shirt_idx]
        pants_color = self.color_palette[self.selected_pants_idx]
        
        # Calculate shadow colors
        shirt_shadow = (max(0, shirt_color[0]-35), max(0, shirt_color[1]-35), max(0, shirt_color[2]-35))
        pants_shadow = (max(0, pants_color[0]-25), max(0, pants_color[1]-25), max(0, pants_color[2]-25))
        hat_shadow = (max(0, hat_color[0]-25), max(0, hat_color[1]-25), max(0, hat_color[2]-25))
        
        # Skin and other colors
        skin_color = (255, 218, 185)
        skin_shadow = (235, 190, 155)
        skin_highlight = (255, 230, 200)
        hair_color = (101, 67, 33)
        hair_shadow = (80, 50, 25)
        boots_color = (101, 67, 33)
        boots_shadow = (70, 45, 20)
        hat_band = (139, 69, 19)
        
        # Shadow under character
        shadow_surf = pygame.Surface((60 * scale, 20 * scale), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 60), (0, 0, 60 * scale, 20 * scale))
        screen.blit(shadow_surf, (cx - 30 * scale, cy + 95 * scale))
        
        # === BOOTS ===
        boot_y = cy + 85 * scale
        # Left boot
        pygame.draw.ellipse(screen, boots_shadow, (cx - 16 * scale, boot_y + 2, 14 * scale, 10 * scale))
        pygame.draw.ellipse(screen, boots_color, (cx - 17 * scale, boot_y, 14 * scale, 10 * scale))
        # Right boot
        pygame.draw.ellipse(screen, boots_shadow, (cx + 3 * scale, boot_y + 2, 14 * scale, 10 * scale))
        pygame.draw.ellipse(screen, boots_color, (cx + 2 * scale, boot_y, 14 * scale, 10 * scale))
        
        # === LEGS/PANTS ===
        pants_top = cy + 45 * scale
        pants_bottom = boot_y + 2
        
        # Left leg - slightly bent pose
        left_leg_points = [
            (cx - 10 * scale, pants_top),
            (cx - 14 * scale, pants_top + 20 * scale),
            (cx - 12 * scale, pants_bottom),
            (cx - 4 * scale, pants_bottom),
            (cx - 2 * scale, pants_top + 20 * scale),
            (cx - 4 * scale, pants_top),
        ]
        pygame.draw.polygon(screen, pants_shadow, [(p[0] + 2, p[1]) for p in left_leg_points])
        pygame.draw.polygon(screen, pants_color, left_leg_points)
        
        # Right leg
        right_leg_points = [
            (cx + 4 * scale, pants_top),
            (cx + 2 * scale, pants_top + 20 * scale),
            (cx + 4 * scale, pants_bottom),
            (cx + 12 * scale, pants_bottom),
            (cx + 14 * scale, pants_top + 20 * scale),
            (cx + 10 * scale, pants_top),
        ]
        pygame.draw.polygon(screen, pants_shadow, [(p[0] + 2, p[1]) for p in right_leg_points])
        pygame.draw.polygon(screen, pants_color, right_leg_points)
        
        # === BODY/TORSO ===
        body_top = cy - 5 * scale
        
        # Torso - more realistic shape
        torso_points = [
            (cx - 14 * scale, body_top + 5 * scale),  # left shoulder
            (cx - 16 * scale, body_top + 25 * scale),  # left side
            (cx - 12 * scale, body_top + 50 * scale),  # left hip
            (cx + 12 * scale, body_top + 50 * scale),  # right hip
            (cx + 16 * scale, body_top + 25 * scale),  # right side
            (cx + 14 * scale, body_top + 5 * scale),   # right shoulder
        ]
        pygame.draw.polygon(screen, shirt_shadow, [(p[0] + 2, p[1] + 2) for p in torso_points])
        pygame.draw.polygon(screen, shirt_color, torso_points)
        
        # Collar/V-neck
        collar_points = [
            (cx - 8 * scale, body_top),
            (cx, body_top + 15 * scale),
            (cx + 8 * scale, body_top),
        ]
        pygame.draw.polygon(screen, (220, 220, 220), collar_points)
        pygame.draw.lines(screen, (180, 180, 180), False, [(cx - 8 * scale, body_top), (cx, body_top + 15 * scale), (cx + 8 * scale, body_top)], 2)
        
        # === ARMS ===
        # Left arm
        arm_left_start = (cx - 14 * scale, body_top + 8 * scale)
        arm_left_elbow = (cx - 22 * scale, body_top + 30 * scale)
        arm_left_end = (cx - 20 * scale, body_top + 50 * scale)
        pygame.draw.line(screen, shirt_shadow, 
                        (arm_left_start[0] + 2, arm_left_start[1]), 
                        (arm_left_elbow[0] + 2, arm_left_elbow[1]), int(8 * scale))
        pygame.draw.line(screen, shirt_color, arm_left_start, arm_left_elbow, int(7 * scale))
        pygame.draw.line(screen, shirt_shadow,
                        (arm_left_elbow[0] + 2, arm_left_elbow[1]),
                        (arm_left_end[0] + 2, arm_left_end[1]), int(6 * scale))
        pygame.draw.line(screen, shirt_color, arm_left_elbow, arm_left_end, int(5 * scale))
        # Left hand
        pygame.draw.circle(screen, skin_shadow, (int(arm_left_end[0]) + 1, int(arm_left_end[1]) + 1), int(5 * scale))
        pygame.draw.circle(screen, skin_color, (int(arm_left_end[0]), int(arm_left_end[1])), int(5 * scale))
        
        # Right arm
        arm_right_start = (cx + 14 * scale, body_top + 8 * scale)
        arm_right_elbow = (cx + 22 * scale, body_top + 30 * scale)
        arm_right_end = (cx + 20 * scale, body_top + 50 * scale)
        pygame.draw.line(screen, shirt_shadow,
                        (arm_right_start[0] + 2, arm_right_start[1]),
                        (arm_right_elbow[0] + 2, arm_right_elbow[1]), int(8 * scale))
        pygame.draw.line(screen, shirt_color, arm_right_start, arm_right_elbow, int(7 * scale))
        pygame.draw.line(screen, shirt_shadow,
                        (arm_right_elbow[0] + 2, arm_right_elbow[1]),
                        (arm_right_end[0] + 2, arm_right_end[1]), int(6 * scale))
        pygame.draw.line(screen, shirt_color, arm_right_elbow, arm_right_end, int(5 * scale))
        # Right hand
        pygame.draw.circle(screen, skin_shadow, (int(arm_right_end[0]) + 1, int(arm_right_end[1]) + 1), int(5 * scale))
        pygame.draw.circle(screen, skin_color, (int(arm_right_end[0]), int(arm_right_end[1])), int(5 * scale))
        
        # === NECK ===
        neck_rect = pygame.Rect(cx - 4 * scale, body_top - 8 * scale, 8 * scale, 10 * scale)
        pygame.draw.rect(screen, skin_shadow, (neck_rect.x + 1, neck_rect.y + 1, neck_rect.width, neck_rect.height))
        pygame.draw.rect(screen, skin_color, neck_rect)
        
        # === HEAD ===
        head_y = body_top - 35 * scale
        head_width = 28 * scale
        head_height = 32 * scale
        
        # Head shape - more oval and realistic
        pygame.draw.ellipse(screen, skin_shadow,
                           (cx - head_width//2 + 2, head_y + 2, head_width, head_height))
        pygame.draw.ellipse(screen, skin_color,
                           (cx - head_width//2, head_y, head_width, head_height))
        
        # === HAIR ===
        # Hair on top
        hair_points = [
            (cx - 12 * scale, head_y + 8 * scale),
            (cx - 14 * scale, head_y - 2 * scale),
            (cx - 8 * scale, head_y - 6 * scale),
            (cx, head_y - 8 * scale),
            (cx + 8 * scale, head_y - 6 * scale),
            (cx + 14 * scale, head_y - 2 * scale),
            (cx + 12 * scale, head_y + 8 * scale),
        ]
        pygame.draw.polygon(screen, hair_shadow, [(p[0] + 1, p[1] + 1) for p in hair_points])
        pygame.draw.polygon(screen, hair_color, hair_points)
        
        # Side hair
        pygame.draw.ellipse(screen, hair_color, (cx - 14 * scale, head_y + 5 * scale, 8 * scale, 15 * scale))
        pygame.draw.ellipse(screen, hair_color, (cx + 6 * scale, head_y + 5 * scale, 8 * scale, 15 * scale))
        
        # === FACE ===
        # Eyes - more detailed
        eye_y = head_y + 12 * scale
        # Left eye
        pygame.draw.ellipse(screen, (255, 255, 255), (cx - 10 * scale, eye_y, 8 * scale, 6 * scale))
        pygame.draw.circle(screen, (60, 40, 30), (int(cx - 6 * scale), int(eye_y + 3 * scale)), int(2.5 * scale))
        pygame.draw.circle(screen, (255, 255, 255), (int(cx - 7 * scale), int(eye_y + 2 * scale)), int(1 * scale))
        # Right eye
        pygame.draw.ellipse(screen, (255, 255, 255), (cx + 2 * scale, eye_y, 8 * scale, 6 * scale))
        pygame.draw.circle(screen, (60, 40, 30), (int(cx + 6 * scale), int(eye_y + 3 * scale)), int(2.5 * scale))
        pygame.draw.circle(screen, (255, 255, 255), (int(cx + 5 * scale), int(eye_y + 2 * scale)), int(1 * scale))
        
        # Eyebrows
        pygame.draw.line(screen, hair_color, 
                        (cx - 11 * scale, eye_y - 3 * scale), 
                        (cx - 4 * scale, eye_y - 4 * scale), 2)
        pygame.draw.line(screen, hair_color, 
                        (cx + 4 * scale, eye_y - 4 * scale), 
                        (cx + 11 * scale, eye_y - 3 * scale), 2)
        
        # Nose
        pygame.draw.line(screen, skin_shadow, 
                        (cx, eye_y + 6 * scale), 
                        (cx - 2 * scale, eye_y + 12 * scale), 2)
        pygame.draw.line(screen, skin_shadow,
                        (cx - 2 * scale, eye_y + 12 * scale),
                        (cx + 2 * scale, eye_y + 12 * scale), 2)
        
        # Mouth
        pygame.draw.arc(screen, (180, 100, 100),
                       (cx - 5 * scale, eye_y + 14 * scale, 10 * scale, 5 * scale), 3.14, 6.28, 2)
        
        # Ears
        pygame.draw.ellipse(screen, skin_shadow, (cx - 15 * scale, head_y + 10 * scale, 5 * scale, 8 * scale))
        pygame.draw.ellipse(screen, skin_color, (cx - 16 * scale, head_y + 9 * scale, 5 * scale, 8 * scale))
        pygame.draw.ellipse(screen, skin_shadow, (cx + 10 * scale, head_y + 10 * scale, 5 * scale, 8 * scale))
        pygame.draw.ellipse(screen, skin_color, (cx + 11 * scale, head_y + 9 * scale, 5 * scale, 8 * scale))
        
        # === HAT ===
        hat_base_y = head_y - 5 * scale
        
        # Hat brim - wider ellipse
        pygame.draw.ellipse(screen, hat_shadow,
                           (cx - 22 * scale, hat_base_y + 6 * scale, 44 * scale, 12 * scale))
        pygame.draw.ellipse(screen, hat_color,
                           (cx - 23 * scale, hat_base_y + 4 * scale, 44 * scale, 12 * scale))
        
        # Hat crown - rounded top
        crown_points = [
            (cx - 16 * scale, hat_base_y + 6 * scale),
            (cx - 14 * scale, hat_base_y - 8 * scale),
            (cx - 8 * scale, hat_base_y - 14 * scale),
            (cx, hat_base_y - 16 * scale),
            (cx + 8 * scale, hat_base_y - 14 * scale),
            (cx + 14 * scale, hat_base_y - 8 * scale),
            (cx + 16 * scale, hat_base_y + 6 * scale),
        ]
        pygame.draw.polygon(screen, hat_shadow, [(p[0] + 2, p[1] + 2) for p in crown_points])
        pygame.draw.polygon(screen, hat_color, crown_points)
        
        # Hat band
        pygame.draw.ellipse(screen, hat_band,
                           (cx - 17 * scale, hat_base_y + 2 * scale, 34 * scale, 6 * scale))
        
        # Highlight on hat
        pygame.draw.arc(screen, (min(255, hat_color[0] + 30), min(255, hat_color[1] + 30), min(255, hat_color[2] + 30)),
                       (cx - 10 * scale, hat_base_y - 12 * scale, 16 * scale, 12 * scale), 0, 3.14, 2)

    def _draw_load_panel(self, screen: pygame.Surface):
        """Draw the load game panel overlay."""
        panel_width = 700
        panel_height = 450
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        
        # Semi-transparent background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, (50, 50, 60), panel_rect, border_radius=15)
        pygame.draw.rect(screen, WHITE, panel_rect, 3, border_radius=15)
        
        # Title
        title_font = pygame.font.SysFont(FONT_NAME, 32, bold=True)
        title = title_font.render("Load Game", True, WHITE)
        screen.blit(title, (panel_x + 20, panel_y + 15))
        
        # Draw close and load buttons
        self.close_button.draw(screen, self.button_font)
        self.load_confirm_button.draw(screen, self.button_font)
        
        # Save list area
        list_x = panel_x + 20
        list_y = panel_y + 60
        list_width = panel_width - 40
        item_height = 50
        
        if self.saves:
            for index, save in enumerate(self.saves):
                item_y = list_y + index * item_height
                if item_y + item_height > panel_y + panel_height - 80:
                    break
                
                # Item background
                item_rect = pygame.Rect(list_x, item_y, list_width - 100, item_height - 8)
                if index == self.selected_save_index:
                    pygame.draw.rect(screen, (80, 120, 160), item_rect, border_radius=8)
                    pygame.draw.rect(screen, (255, 215, 0), item_rect, 3, border_radius=8)
                else:
                    pygame.draw.rect(screen, (70, 70, 80), item_rect, border_radius=8)
                
                # Save info
                name_text = self.save_list_font.render(f"{save['name']} (Save {save['id']})", True, WHITE)
                screen.blit(name_text, (list_x + 10, item_y + 5))
                
                date_text = pygame.font.SysFont(FONT_NAME, 18).render(
                    f"Last played: {save['updated_at'].split('T')[0]}", True, LIGHT_GRAY
                )
                screen.blit(date_text, (list_x + 10, item_y + 28))
                
                # Delete button
                delete_rect = pygame.Rect(list_x + list_width - 90, item_y, 80, item_height - 8)
                delete_color = (200, 80, 80) if delete_rect.collidepoint(pygame.mouse.get_pos()) else (160, 60, 60)
                pygame.draw.rect(screen, delete_color, delete_rect, border_radius=5)
                delete_text = pygame.font.SysFont(FONT_NAME, 20).render("Delete", True, WHITE)
                delete_text_rect = delete_text.get_rect(center=delete_rect.center)
                screen.blit(delete_text, delete_text_rect)
        else:
            empty_text = self.save_list_font.render("No saved games found", True, LIGHT_GRAY)
            screen.blit(empty_text, (panel_x + 20, list_y + 20))

    def _draw_confirm_dialog(self, screen: pygame.Surface):
        """Draw the confirmation dialog for delete."""
        dialog_width = 400
        dialog_height = 180
        dialog_x = (SCREEN_WIDTH - dialog_width) // 2
        dialog_y = (SCREEN_HEIGHT - dialog_height) // 2
        
        # Semi-transparent background overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Dialog background
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        pygame.draw.rect(screen, (60, 60, 70), dialog_rect, border_radius=15)
        pygame.draw.rect(screen, WHITE, dialog_rect, 3, border_radius=15)
        
        # Warning icon (triangle with exclamation)
        icon_x = dialog_x + dialog_width // 2
        icon_y = dialog_y + 40
        pygame.draw.polygon(screen, (255, 200, 50), [
            (icon_x, icon_y - 20),
            (icon_x - 20, icon_y + 15),
            (icon_x + 20, icon_y + 15)
        ])
        pygame.draw.polygon(screen, (200, 150, 30), [
            (icon_x, icon_y - 20),
            (icon_x - 20, icon_y + 15),
            (icon_x + 20, icon_y + 15)
        ], 2)
        # Exclamation mark
        pygame.draw.line(screen, (60, 60, 70), (icon_x, icon_y - 5), (icon_x, icon_y + 5), 3)
        pygame.draw.circle(screen, (60, 60, 70), (icon_x, icon_y + 10), 2)
        
        # Message text
        message_font = pygame.font.SysFont(FONT_NAME, 24, bold=True)
        message = message_font.render("Are you sure?", True, WHITE)
        message_rect = message.get_rect(center=(dialog_x + dialog_width // 2, dialog_y + 80))
        screen.blit(message, message_rect)
        
        sub_message_font = pygame.font.SysFont(FONT_NAME, 18)
        sub_message = sub_message_font.render("This action cannot be undone.", True, LIGHT_GRAY)
        sub_message_rect = sub_message.get_rect(center=(dialog_x + dialog_width // 2, dialog_y + 105))
        screen.blit(sub_message, sub_message_rect)
        
        # Draw buttons
        if hasattr(self, 'yes_button'):
            self.yes_button.draw(screen, self.button_font)
        if hasattr(self, 'no_button'):
            self.no_button.draw(screen, self.button_font)

    def _get_save_db_path(self) -> str:
        """Get the sqlite path for saves."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, "saves.db")

    def _refresh_save_list(self):
        """Load saved games from sqlite and build buttons."""
        db_path = self._get_save_db_path()
        if not os.path.exists(db_path):
            self.saves = []
            self.save_buttons = []
            self.delete_buttons = []
            return
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS saves (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    data TEXT NOT NULL
                )
                """
            )
            rows = conn.execute(
                "SELECT id, name, created_at, updated_at, data FROM saves ORDER BY updated_at DESC"
            ).fetchall()
        self.saves = []
        self.save_buttons = []
        self.delete_buttons = []
        button_width = self.save_area_rect.width - 140
        button_height = 36
        start_x = self.save_area_rect.x + 20
        start_y = self.save_area_rect.y + 50
        delete_width = 80
        for index, row in enumerate(rows[:6]):
            save_id, name, created_at, updated_at, data = row
            payload = json.loads(data)
            farmer_data = payload.get("entities", {}).get("farmer", {})
            hat_color = farmer_data.get("hat_color", self.color_palette[6])  # Default tan
            shirt_color = farmer_data.get("shirt_color", self.color_palette[0])  # Default steel blue
            pants_color = farmer_data.get("pants_color", self.color_palette[7])  # Default gray
            self.saves.append({
                "id": save_id,
                "name": name,
                "created_at": created_at,
                "updated_at": updated_at,
                "hat_color": hat_color,
                "shirt_color": shirt_color,
                "pants_color": pants_color
            })
            button = Button(
                start_x,
                start_y + index * 48,
                button_width,
                button_height,
                f"{name} (Save {save_id})",
                (70, 130, 180),
                (90, 150, 200)
            )
            delete_button = Button(
                start_x + button_width + 20,
                start_y + index * 48,
                delete_width,
                button_height,
                "Delete",
                (180, 70, 70),
                (200, 90, 90)
            )
            self.save_buttons.append(button)
            self.delete_buttons.append(delete_button)
        if self.selected_save_index is not None and self.selected_save_index >= len(self.saves):
            self.selected_save_index = None

    def _delete_save(self, save_id: int):
        """Delete a save by id."""
        db_path = self._get_save_db_path()
        if not os.path.exists(db_path):
            return
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS saves (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    data TEXT NOT NULL
                )
                """
            )
            conn.execute("DELETE FROM saves WHERE id = ?", (save_id,))
            conn.commit()
        self._refresh_save_list()

    def _draw_farm_background(self, screen: pygame.Surface):
        """Draw a scenic farm background with animals and trees."""
        horizon_y = int(SCREEN_HEIGHT * 0.52)
        # Far hills
        pygame.draw.ellipse(screen, (120, 190, 120), (-120, horizon_y - 140, 520, 240))
        pygame.draw.ellipse(screen, (110, 180, 110), (260, horizon_y - 160, 620, 280))
        pygame.draw.ellipse(screen, (100, 170, 100), (760, horizon_y - 150, 620, 260))

        # Tree line
        for x in range(60, SCREEN_WIDTH, 220):
            self._draw_background_tree(screen, x, horizon_y + 20, scale=0.7)
            self._draw_background_tree(screen, x + 80, horizon_y + 10, scale=0.8)

        # Farmland bands
        pygame.draw.rect(screen, (78, 155, 78), (0, horizon_y, SCREEN_WIDTH, 120))
        pygame.draw.rect(screen, (92, 168, 92), (0, horizon_y + 110, SCREEN_WIDTH, 120))

        # Main grass foreground
        grass_rect = pygame.Rect(0, SCREEN_HEIGHT - 160, SCREEN_WIDTH, 160)
        pygame.draw.rect(screen, (34, 139, 34), grass_rect)
        pygame.draw.rect(screen, (20, 110, 20), grass_rect, 4)

        # Farm houses
        self._draw_background_house(screen, 220, horizon_y + 40)
        self._draw_background_house(screen, SCREEN_WIDTH - 320, horizon_y + 30, scale=0.9)

        # Pasture fence
        self._draw_fence_line(screen, 0, horizon_y + 140, SCREEN_WIDTH)

        # Animals
        self._draw_cow(screen, 520, horizon_y + 160)
        self._draw_cow(screen, 700, horizon_y + 170, scale=0.9)
        self._draw_chicken(screen, 980, horizon_y + 190)
        self._draw_chicken(screen, 1060, horizon_y + 200, scale=0.8)

        # Crops in foreground
        for i in range(12):
            self._draw_crop(screen, 420 + i * 60, SCREEN_HEIGHT - 120)

        # Soft haze for depth
        haze_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(haze_surface, (255, 255, 255, 25), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(haze_surface, (0, 0))

    def _draw_background_tree(self, screen: pygame.Surface, x: int, y: int, scale: float = 1.0):
        """Draw a stylized tree for background"""
        trunk_width = int(20 * scale)
        trunk_height = int(40 * scale)
        pygame.draw.rect(screen, (101, 67, 33), (x - trunk_width // 2, y, trunk_width, trunk_height))
        pygame.draw.circle(screen, (34, 139, 34), (x, y - int(10 * scale)), int(35 * scale))
        pygame.draw.circle(screen, (50, 180, 50), (x - int(15 * scale), y - int(20 * scale)), int(25 * scale))
        pygame.draw.circle(screen, (50, 180, 50), (x + int(15 * scale), y - int(20 * scale)), int(25 * scale))

    def _draw_background_house(self, screen: pygame.Surface, x: int, y: int, scale: float = 1.0):
        """Draw a simple house silhouette in the background."""
        house_width = int(160 * scale)
        house_height = int(100 * scale)
        wall_rect = pygame.Rect(x, y, house_width, house_height)
        pygame.draw.rect(screen, (220, 200, 170), wall_rect)
        pygame.draw.rect(screen, (170, 140, 110), wall_rect, 3)

        roof_points = [
            (x - int(10 * scale), y),
            (x + house_width // 2, y - int(60 * scale)),
            (x + house_width + int(10 * scale), y)
        ]
        pygame.draw.polygon(screen, (180, 90, 50), roof_points)
        pygame.draw.polygon(screen, (140, 70, 40), roof_points, 2)

        door_rect = pygame.Rect(
            x + house_width // 2 - int(16 * scale),
            y + house_height - int(44 * scale),
            int(32 * scale),
            int(44 * scale)
        )
        pygame.draw.rect(screen, (120, 70, 40), door_rect)
        pygame.draw.rect(screen, (80, 50, 30), door_rect, 2)

        window_rect = pygame.Rect(
            x + int(20 * scale),
            y + int(24 * scale),
            int(30 * scale),
            int(24 * scale)
        )
        pygame.draw.rect(screen, (190, 220, 250), window_rect)
        pygame.draw.rect(screen, (120, 90, 70), window_rect, 2)

    def _draw_fence_line(self, screen: pygame.Surface, x: int, y: int, width: int):
        """Draw a simple fence line across the scene."""
        post_color = (210, 180, 140)
        rail_color = (190, 160, 120)
        for i in range(x, x + width, 80):
            pygame.draw.rect(screen, post_color, (i, y - 12, 10, 30))
        pygame.draw.rect(screen, rail_color, (x, y - 6, width, 6))
        pygame.draw.rect(screen, rail_color, (x, y + 8, width, 6))

    def _draw_cow(self, screen: pygame.Surface, x: int, y: int, scale: float = 1.0):
        """Draw a simple cow figure."""
        body_width = int(70 * scale)
        body_height = int(40 * scale)
        body_rect = pygame.Rect(x, y, body_width, body_height)
        pygame.draw.ellipse(screen, (245, 245, 245), body_rect)
        pygame.draw.ellipse(screen, (30, 30, 30), (x + int(10 * scale), y + int(8 * scale), int(18 * scale), int(14 * scale)))
        pygame.draw.ellipse(screen, (30, 30, 30), (x + int(36 * scale), y + int(12 * scale), int(20 * scale), int(12 * scale)))

        head_rect = pygame.Rect(x - int(18 * scale), y + int(8 * scale), int(20 * scale), int(18 * scale))
        pygame.draw.ellipse(screen, (245, 245, 245), head_rect)
        pygame.draw.circle(screen, (30, 30, 30), (x - int(6 * scale), y + int(16 * scale)), int(3 * scale))

        for leg_offset in [10, 24, 44, 58]:
            pygame.draw.line(
                screen,
                (90, 70, 50),
                (x + int(leg_offset * scale), y + body_height),
                (x + int(leg_offset * scale), y + body_height + int(16 * scale)),
                4
            )

    def _draw_chicken(self, screen: pygame.Surface, x: int, y: int, scale: float = 1.0):
        """Draw a simple chicken figure."""
        pygame.draw.circle(screen, (255, 255, 255), (x, y), int(12 * scale))
        pygame.draw.circle(screen, (255, 255, 255), (x + int(12 * scale), y - int(4 * scale)), int(8 * scale))
        pygame.draw.circle(screen, (220, 50, 50), (x + int(18 * scale), y - int(6 * scale)), int(3 * scale))
        pygame.draw.polygon(screen, (255, 200, 0), [
            (x + int(20 * scale), y),
            (x + int(28 * scale), y - int(4 * scale)),
            (x + int(20 * scale), y - int(8 * scale))
        ])
        pygame.draw.line(
            screen,
            (150, 100, 50),
            (x - int(4 * scale), y + int(12 * scale)),
            (x - int(8 * scale), y + int(18 * scale)),
            2
        )
        pygame.draw.line(
            screen,
            (150, 100, 50),
            (x + int(4 * scale), y + int(12 * scale)),
            (x + int(8 * scale), y + int(18 * scale)),
            2
        )

    def _draw_crop(self, screen, x, y):
        """Draw a small crop figure"""
        pygame.draw.line(screen, (100, 200, 100), (x, y), (x, y - 15), 3)
        pygame.draw.ellipse(screen, (218, 165, 32), (x - 4, y - 25, 8, 12))