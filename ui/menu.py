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
    """Main menu screen"""
    
    def __init__(self, on_start_game: Callable[[str, tuple, Optional[int]], None]):
        self.on_start_game = on_start_game
        
        # Fonts
        self.title_font = pygame.font.SysFont(FONT_NAME, MENU_TITLE_SIZE, bold=True)
        self.button_font = pygame.font.SysFont(FONT_NAME, MENU_BUTTON_SIZE)
        self.input_font = pygame.font.SysFont(FONT_NAME, MENU_BUTTON_SIZE)
        self.save_list_font = pygame.font.SysFont(FONT_NAME, 24)
        
        # Title
        self.title_text = "Farm Life"
        
        # Username input
        input_width = 300
        input_height = 50
        input_x = (SCREEN_WIDTH - input_width) // 2
        input_y = SCREEN_HEIGHT // 2 - 120
        self.username_input = TextInput(input_x, input_y, input_width, input_height)
        
        # Shirt color selection
        self.shirt_colors = [
            (70, 130, 180),  # Steel Blue
            (180, 70, 70),   # Red
            (70, 180, 70),   # Green
            (180, 180, 70),  # Yellow
            (180, 70, 180),  # Purple
            (70, 180, 180)   # Cyan
        ]
        self.selected_color_idx = 0
        self.color_swatches = []
        swatch_size = 40
        swatch_spacing = 15
        total_swatches_width = len(self.shirt_colors) * swatch_size + (len(self.shirt_colors) - 1) * swatch_spacing
        start_x = (SCREEN_WIDTH - total_swatches_width) // 2
        swatch_y = SCREEN_HEIGHT // 2 + 60
        
        for i, color in enumerate(self.shirt_colors):
            rect = pygame.Rect(start_x + i * (swatch_size + swatch_spacing), swatch_y, swatch_size, swatch_size)
            self.color_swatches.append(rect)

        # Start and load buttons
        button_width = 200
        button_height = 50
        button_y = SCREEN_HEIGHT // 2 + 140
        button_spacing = 20
        total_button_width = button_width * 2 + button_spacing
        button_x = (SCREEN_WIDTH - total_button_width) // 2
        self.start_button = Button(
            button_x, button_y, button_width, button_height,
            "Start New Game", GREEN, DARK_GREEN
        )
        self.load_button = Button(
            button_x + button_width + button_spacing, button_y, button_width, button_height,
            "Load Game", (80, 120, 180), (100, 140, 200)
        )

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
    
    def handle_event(self, event: pygame.event.Event):
        """Handle menu events"""
        self.username_input.handle_event(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for i, rect in enumerate(self.color_swatches):
                    if rect.collidepoint(event.pos):
                        self.selected_color_idx = i
                        break

        if self.show_load_panel:
            self._handle_load_panel_event(event)
        
        if self.show_delete_confirm:
            self._handle_confirm_dialog_event(event)
        elif not self.show_load_panel:
            if self.start_button.handle_event(event):
                username = self.username_input.get_text().strip()
                if username:
                    self.on_start_game(username, self.shirt_colors[self.selected_color_idx], None)

            if self.load_button.handle_event(event):
                self._refresh_save_list()
                self.show_load_panel = True
                self.selected_save_index = None

    def _handle_load_panel_event(self, event: pygame.event.Event):
        """Handle events within the load panel overlay."""
        if event.type == pygame.MOUSEMOTION:
            # Update hover states for buttons
            if hasattr(self, 'close_button'):
                self.close_button.is_hovered = self.close_button.rect.collidepoint(event.pos)
            if hasattr(self, 'load_confirm_button'):
                self.load_confirm_button.is_hovered = self.load_confirm_button.rect.collidepoint(event.pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Create buttons if not exists
            if not hasattr(self, 'close_button'):
                self._create_load_panel_buttons()
            
            # Check close button
            if self.close_button.rect.collidepoint(event.pos):
                self.show_load_panel = False
                return
            
            # Check load confirm button
            if self.load_confirm_button.rect.collidepoint(event.pos):
                if self.selected_save_index is not None:
                    save = self.saves[self.selected_save_index]
                    username = save.get("name") or self.username_input.get_text().strip()
                    shirt_color = save.get("shirt_color", self.shirt_colors[self.selected_color_idx])
                    if username:
                        self.on_start_game(username, tuple(shirt_color), save.get("id"))
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
        shadow_rect = title_shadow.get_rect(center=(SCREEN_WIDTH // 2 + 3, 120 + 3))
        screen.blit(title_shadow, shadow_rect)
        
        title_surface = self.title_font.render(self.title_text, True, YELLOW)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 120))
        screen.blit(title_surface, title_rect)
        
        # Draw subtitle
        subtitle_font = pygame.font.SysFont(FONT_NAME, 28)
        subtitle = subtitle_font.render("A Grid-Based Farming Adventure", True, DARK_GREEN)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 180))
        screen.blit(subtitle, subtitle_rect)
        
        # Draw username label
        label_font = pygame.font.SysFont(FONT_NAME, 24)
        label = label_font.render("Enter your name:", True, BLACK)
        label_rect = label.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 130))
        screen.blit(label, label_rect)
        
        # Draw color selection label
        color_label = label_font.render("Select Shirt Color:", True, BLACK)
        color_label_rect = color_label.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        screen.blit(color_label, color_label_rect)

        # Draw swatches
        for i, rect in enumerate(self.color_swatches):
            pygame.draw.rect(screen, self.shirt_colors[i], rect, border_radius=5)
            if i == self.selected_color_idx:
                pygame.draw.rect(screen, WHITE, rect, 3, border_radius=5)
            else:
                pygame.draw.rect(screen, BLACK, rect, 1, border_radius=5)

        # Draw input and buttons
        self.username_input.draw(screen, self.input_font)
        self.start_button.draw(screen, self.button_font)
        self.load_button.draw(screen, self.button_font)
        
        # Draw instructions
        instruction_font = pygame.font.SysFont(FONT_NAME, 20)
        y_start = SCREEN_HEIGHT - 100
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
            shirt_color = payload.get("entities", {}).get("farmer", {}).get("shirt_color", self.shirt_colors[0])
            self.saves.append({
                "id": save_id,
                "name": name,
                "created_at": created_at,
                "updated_at": updated_at,
                "shirt_color": shirt_color
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