import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, YELLOW, GREEN, RED

class ConfirmationBox:
    def __init__(self, message, on_yes):
        self.message = message
        self.on_yes = on_yes
        self.is_open = False
        
        self.width = 400
        self.height = 200
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = (SCREEN_HEIGHT - self.height) // 2
        
        self.font = pygame.font.SysFont('Arial', 24, bold=True)
        self.button_font = pygame.font.SysFont('Arial', 20, bold=True)
        
        self.yes_rect = pygame.Rect(self.x + 50, self.y + 120, 120, 50)
        self.no_rect = pygame.Rect(self.x + 230, self.y + 120, 120, 50)
        
    def open(self):
        self.is_open = True
        
    def close(self):
        self.is_open = False
        
    def handle_event(self, event):
        if not self.is_open:
            return None
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.yes_rect.collidepoint(event.pos):
                self.close()
                self.on_yes()
                return "yes"
            elif self.no_rect.collidepoint(event.pos):
                self.close()
                return "no"
        return None

    def draw(self, screen):
        if not self.is_open:
            return
            
        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Box
        pygame.draw.rect(screen, (50, 50, 50), (self.x, self.y, self.width, self.height), border_radius=10)
        pygame.draw.rect(screen, YELLOW, (self.x, self.y, self.width, self.height), 3, border_radius=10)
        
        # Message
        msg_surf = self.font.render(self.message, True, WHITE)
        msg_rect = msg_surf.get_rect(centerx=self.x + self.width // 2, top=self.y + 40)
        screen.blit(msg_surf, msg_rect)
        
        # Yes Button
        pygame.draw.rect(screen, GREEN, self.yes_rect, border_radius=5)
        yes_text = self.button_font.render("YES", True, WHITE)
        yes_text_rect = yes_text.get_rect(center=self.yes_rect.center)
        screen.blit(yes_text, yes_text_rect)
        
        # No Button
        pygame.draw.rect(screen, RED, self.no_rect, border_radius=5)
        no_text = self.button_font.render("NO", True, WHITE)
        no_text_rect = no_text.get_rect(center=self.no_rect.center)
        screen.blit(no_text, no_text_rect)
