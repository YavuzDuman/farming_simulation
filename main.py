"""
Farm Life - A 2D Grid-Based Farming Game
Entry point for the game
"""
import pygame
import sys
import os

# Add the current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, SKY_BLUE
from ui.menu import Menu
from game.game_manager import GameManager


def main():
    """Main entry point for the game"""
    # Initialize Pygame
    pygame.init()
    pygame.font.init()
    
    # Create the game window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Farm Life - A Grid-Based Farming Game")
    
    # Set up the clock for controlling frame rate
    clock = pygame.time.Clock()
    
    # Game state
    current_state = "menu"
    username = ""
    game_manager = None
    menu = None
    
    def start_game(player_name: str):
        """Callback to start the game with the given username"""
        nonlocal current_state, username, game_manager
        username = player_name
        game_manager = GameManager(screen, username)
        current_state = "playing"
    
    # Create menu with callback
    menu = Menu(start_game)
    
    # Main game loop
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds
        
        if current_state == "menu":
            # Handle menu events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                menu.handle_event(event)
            
            # Update menu
            menu.update(dt)
            
            # Draw menu
            screen.fill(SKY_BLUE)
            menu.draw(screen)
            pygame.display.flip()
            
        elif current_state == "playing":
            # Run the game
            if game_manager:
                if not game_manager.handle_events():
                    running = False
                game_manager.update()
                game_manager.draw()
            else:
                running = False
    
    # Clean up
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()