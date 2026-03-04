"""
Game Configuration and Constants
"""
import pygame

# Screen settings - BIGGER SCREEN
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 1000
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)  # Forest green for grass
LIGHT_GREEN = (144, 238, 144)  # Light green for hover
DARK_GREEN = (0, 100, 0)  # Dark green for selected
BROWN = (139, 69, 19)  # Saddle brown for dirt/soil
LIGHT_BROWN = (205, 133, 63)  # Tan for hover on soil
DARK_BROWN = (101, 67, 33)  # Dark brown for selected soil
SKY_BLUE = (135, 206, 235)  # Sky blue for background
YELLOW = (255, 215, 0)  # Gold for highlights
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
ORANGE = (255, 140, 0)
RED = (220, 20, 60)

# Tree colors
TREE_TRUNK = (101, 67, 33)
TREE_LEAVES_DARK = (0, 80, 0)
TREE_LEAVES_MEDIUM = (34, 139, 34)
TREE_LEAVES_LIGHT = (50, 180, 50)

# House colors
HOUSE_WALL = (245, 222, 179)  # Wheat color
HOUSE_ROOF = (160, 82, 45)    # Sienna
HOUSE_DOOR = (139, 69, 19)    # Brown
HOUSE_WINDOW = (135, 206, 250) # Light sky blue

# Chest colors
CHEST_WOOD = (160, 82, 45)
CHEST_GOLD = (255, 215, 0)

# Grid settings - SMALLER GRID BOXES
GRID_SIZE = 48  # Reduced from 64 to 48 pixels
GRID_COLS = 24  # More columns for bigger screen
GRID_ROWS = 16  # More rows for bigger screen
GRID_OFFSET_X = (SCREEN_WIDTH - GRID_COLS * GRID_SIZE) // 2
GRID_OFFSET_Y = 100  # Leave space for UI at top

# Player settings - Adjusted for smaller grid
PLAYER_SPEED = 4
PLAYER_SIZE = 36  # Slightly smaller to fit better

# Font settings
FONT_NAME = 'Arial'
MENU_TITLE_SIZE = 72
MENU_BUTTON_SIZE = 32
GAME_UI_SIZE = 24
