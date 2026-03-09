"""
Tasks UI - Beginner task list and progress tracking
"""
import pygame
from typing import List, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, YELLOW


class Task:
    """Represents a single task"""
    
    def __init__(self, task_id: str, description: str, target: int = 1):
        self.task_id = task_id
        self.description = description
        self.target = target
        self.progress = 0
        self.completed = False
    
    def update_progress(self, amount: int = 1):
        """Update task progress"""
        if self.completed:
            return
        self.progress = min(self.target, self.progress + amount)
        if self.progress >= self.target:
            self.completed = True


class TasksUI:
    """UI for displaying and tracking tasks"""
    
    def __init__(self):
        self.is_open = False
        
        # Panel dimensions
        self.width = 500
        self.height = 400
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = (SCREEN_HEIGHT - self.height) // 2
        
        # Fonts
        self.title_font = pygame.font.SysFont('Arial', 26, bold=True)
        self.task_font = pygame.font.SysFont('Arial', 18, bold=True)
        self.small_font = pygame.font.SysFont('Arial', 14)
        
        # Tasks list
        self.tasks: List[Task] = [
            Task("cut_tree", "Cut down a tree", 1),
            Task("smash_stone", "Smash a stone", 1),
            Task("plant_seed", "Plant a seed", 1),
            Task("harvest_crop", "Harvest a crop", 1),
            Task("collect_wood", "Collect wood", 3),
            Task("collect_stone", "Collect stone", 3),
        ]
        
        # Close button
        self.close_button_rect = pygame.Rect(self.x + self.width - 40, self.y + 10, 30, 30)
    
    def toggle(self):
        """Toggle the tasks panel"""
        self.is_open = not self.is_open
    
    def close(self):
        """Close the tasks panel"""
        self.is_open = False
    
    def update_task(self, task_id: str, amount: int = 1):
        """Update a task by id"""
        for task in self.tasks:
            if task.task_id == task_id:
                task.update_progress(amount)
                break
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Handle events for tasks UI. Returns 'close' if should close."""
        if not self.is_open:
            return None
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            
            # Check close button
            if self.close_button_rect.collidepoint(mouse_pos):
                self.close()
                return "close"
            
            # Click outside panel closes it
            panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            if not panel_rect.collidepoint(mouse_pos):
                self.close()
                return "close"
        
        return None
    
    def draw(self, screen: pygame.Surface):
        """Draw the tasks UI"""
        if not self.is_open:
            return
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Draw panel
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, (50, 40, 30), panel_rect, border_radius=10)
        pygame.draw.rect(screen, (139, 90, 43), panel_rect, 3, border_radius=10)
        
        # Draw title
        title_surface = self.title_font.render("Tasks", True, YELLOW)
        title_rect = title_surface.get_rect(centerx=self.x + self.width // 2, top=self.y + 15)
        screen.blit(title_surface, title_rect)
        
        # Draw close button
        pygame.draw.rect(screen, (150, 50, 50), self.close_button_rect, border_radius=5)
        pygame.draw.rect(screen, (200, 80, 80), self.close_button_rect, 2, border_radius=5)
        x_text = self.task_font.render("X", True, WHITE)
        x_rect = x_text.get_rect(center=self.close_button_rect.center)
        screen.blit(x_text, x_rect)
        
        # Draw tasks list
        task_start_y = self.y + 60
        task_height = 45
        
        for i, task in enumerate(self.tasks):
            task_y = task_start_y + i * task_height
            task_rect = pygame.Rect(self.x + 20, task_y, self.width - 40, task_height - 5)
            
            # Task background
            bg_color = (60, 80, 60) if task.completed else (60, 60, 60)
            pygame.draw.rect(screen, bg_color, task_rect, border_radius=5)
            pygame.draw.rect(screen, (90, 120, 90) if task.completed else (90, 90, 90), task_rect, 2, border_radius=5)
            
            # Task text
            status_text = "✓" if task.completed else "○"
            task_text = f"{status_text} {task.description}"
            text_surface = self.task_font.render(task_text, True, WHITE)
            screen.blit(text_surface, (task_rect.x + 10, task_rect.y + 8))
            
            # Progress text
            if task.target > 1:
                progress_text = f"{task.progress}/{task.target}"
                progress_surface = self.small_font.render(progress_text, True, (200, 200, 200))
                progress_rect = progress_surface.get_rect(right=task_rect.right - 10, centery=task_rect.centery)
                screen.blit(progress_surface, progress_rect)
