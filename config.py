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
GRID_SIZE = 50  # Grid cell size
GRID_COLS = 32  # 32 columns = 1600 pixels (full screen width)
GRID_ROWS = 18  # 18 rows = 900 pixels (leaves room for UI)
GRID_OFFSET_X = 0  # Start from left edge
GRID_OFFSET_Y = 90  # Leave space for UI at top

# Player settings - Adjusted for smaller grid
PLAYER_SPEED = 4
PLAYER_SIZE = 36  # Slightly smaller to fit better
PLAYER_MAX_HEALTH = 100

# Zombie settings
ZOMBIE_SPEED = 1.5
ZOMBIE_DAMAGE = 10
ZOMBIE_REGEN_TIME = 5.0

# Dark Side colors
DARK_SIDE_BG = (8, 8, 15)  # Very dark blue-black
DARK_SIDE_GROUND = (15, 12, 20)  # Dark purple-black ground
DARK_SIDE_BORDER = (30, 20, 35)  # Subtle border
DARK_PURPLE = (48, 25, 52)

# Fog colors for dark side
FOG_COLOR = (20, 18, 30)  # Dark fog
FOG_PARTICLE_COLOR = (40, 35, 50)  # Slightly lighter fog particles

# Zombie colors (more realistic/rotted look)
ZOMBIE_SKIN = (72, 85, 65)  # Grayish-green rotting flesh
ZOMBIE_SKIN_DARK = (45, 55, 42)  # Darker skin shadows
ZOMBIE_SKIN_LIGHT = (95, 105, 85)  # Lighter skin highlights
ZOMBIE_CLOTHES = (35, 30, 28)  # Dark tattered clothes
ZOMBIE_EYE = (180, 20, 20)  # Glowing red eyes
ZOMBIE_BLOOD = (60, 10, 10)  # Dried blood stains

# Health bar colors
HEALTH_RED = (200, 30, 30)
HEALTH_BG = (60, 20, 20)

# Font settings
FONT_NAME = 'Arial'
MENU_TITLE_SIZE = 72
MENU_BUTTON_SIZE = 32
GAME_UI_SIZE = 24

# Seed growth times (in seconds)
SEED_GROWTH_TIMES = {
    'wheat': 30,        # Regular wheat
    'carrot': 30,       # Carrots
    'tomato': 35,       # Tomatoes
    'pumpkin': 45,      # Pumpkins
    'strawberry': 40,   # Strawberries
    'golden_wheat': 60  # Golden wheat (rare)
}

# Grass reset time - tilled grass reverts to green after this many seconds of inactivity
GRASS_RESET_TIME = 30.0  # seconds
