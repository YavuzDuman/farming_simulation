"""
Game Manager - Handles game state and main game loop with Y-sorting
"""
import pygame
from typing import Optional, List
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, SKY_BLUE, GREEN,
    GRID_OFFSET_X, GRID_OFFSET_Y, GRID_COLS, GRID_ROWS, GRID_SIZE
)
from game.grid import Grid
from game.player import Player
from entities.farmer import Farmer
from entities.tree import Tree
from entities.house import House
from entities.chest import Chest
from ui.game_ui import GameUI
from game.inventory import Inventory, ToolType


class GameState:
    """Enum for game states"""
    MENU = 0
    PLAYING = 1
    PAUSED = 2


class GameManager:
    """Manages the main game state and logic with Y-sorting for depth"""
    
    def __init__(self, screen: pygame.Surface, username: str):
        self.screen = screen
        self.username = username
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize game components
        self.grid = Grid()
        self.farmer = Farmer(
            x=GRID_OFFSET_X + GRID_COLS * GRID_SIZE // 2 - 18,
            y=GRID_OFFSET_Y + GRID_ROWS * GRID_SIZE // 2 - 20
        )
        self.player = Player(self.farmer)
        self.ui = GameUI(username)
        
        # Initialize inventory system
        self.inventory = Inventory()
        self.inventory.on_slot_click = self._on_inventory_slot_click
        
        # Store inventory rect for click detection
        self.inventory_rect = None
        
        # Create farm objects (trees, house, chest)
        self.trees: List[Tree] = []
        self.house: Optional[House] = None
        self.chest: Optional[Chest] = None
        self._create_farm_objects()
        
        # Game bounds for player movement
        self.game_bounds = pygame.Rect(
            GRID_OFFSET_X,
            GRID_OFFSET_Y,
            GRID_COLS * GRID_SIZE,
            GRID_ROWS * GRID_SIZE
        )
    
    def _create_farm_objects(self):
        """Create trees, house, and chest on the farm"""
        # Create house using grid coordinates (col, row)
        # House is 4 cells wide, so place it at column 1, row 1
        self.house = House(1, 1, GRID_OFFSET_X, GRID_OFFSET_Y)
        
        # Create chest next to house (one grid cell)
        # Place it at column 5, row 2 (next to house)
        self.chest = Chest(5, 2, GRID_OFFSET_X, GRID_OFFSET_Y)
        
        # Create trees scattered around the farm (avoiding house and chest area)
        # Format: (col, row, size) or (col, row) for medium
        tree_positions = [
            # Left side trees
            (0, 0), (0, 5), (0, 10),
            (1, 8), (1, 14),
            # Right side trees  
            (20, 0), (21, 2), (22, 4),
            (20, 8), (21, 12), (22, 14),
            # Bottom trees
            (8, 14), (12, 15), (16, 14),
            # Scattered trees (away from house)
            (8, 6, "large"), (16, 5, "large"),
            (10, 10, "small"), (14, 11, "small"),
            (6, 12), (18, 10),
        ]
        
        for pos in tree_positions:
            col, row = pos[0], pos[1]
            size = pos[2] if len(pos) > 2 else "medium"
            x = GRID_OFFSET_X + col * GRID_SIZE + GRID_SIZE // 2
            y = GRID_OFFSET_Y + row * GRID_SIZE + GRID_SIZE // 2
            self.trees.append(Tree(x, y, size))
    
    def _get_obstacles(self) -> list:
        """Get all objects that the player can't walk through"""
        obstacles = []
        if self.house:
            obstacles.append(self.house)
        if self.chest:
            obstacles.append(self.chest)
        obstacles.extend(self.trees)
        return obstacles
    
    def _on_inventory_slot_click(self, slot_index: int):
        """Called when an inventory slot is clicked"""
        # Update farmer's held tool
        tool = self.inventory.get_selected_tool()
        self.farmer.held_tool = tool
    
    def _use_tool(self, mouse_pos: tuple[int, int]):
        """Use the currently selected tool"""
        tool = self.inventory.get_selected_tool()
        if not tool:
            return
        
        # Start shake animation
        self.inventory.start_shake()
        self.farmer.tool_shake_angle = self.inventory.get_shake_angle()
        
        # Handle hoe tilling
        if tool.tool_type == ToolType.HOE:
            # Get grid cell at mouse position
            cell = self.grid.get_cell_at_position(*mouse_pos)
            if cell:
                # Till the grass (turn it brown)
                cell.is_tilled = True
                cell.is_hovered = False
        
        # Handle axe chopping
        elif tool.tool_type == ToolType.AXE:
            # Check if clicking on a tree
            for tree in self.trees:
                if tree.is_alive:
                    # Check if mouse is near the tree (within tree bounds)
                    tree_rect = tree.render_rect
                    if tree_rect.collidepoint(mouse_pos):
                        # Chop the tree
                        tree_fell = tree.chop()
                        if tree_fell:
                            # Tree fell - wood is now available for pickup
                            pass
                        break
    
    def _check_wood_collection(self, mouse_pos: tuple[int, int]):
        """Check if hovering over wood and collect it"""
        for tree in self.trees:
            if tree.wood_dropped and tree.check_wood_hover(mouse_pos):
                # Collect the wood
                wood_collected = tree.collect_wood()
                if wood_collected > 0:
                    # Add wood to inventory
                    success = self.inventory.add_wood(wood_collected)
                    if not success:
                        # Inventory full - wood stays on ground
                        tree.wood_dropped = True
                        tree.wood_quantity = wood_collected
                break
    
    def handle_events(self) -> bool:
        """Handle game events, returns False if game should quit"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False  # Exit game
                # Number keys for quick slot selection (0-9)
                if pygame.K_0 <= event.key <= pygame.K_9:
                    if event.key == pygame.K_0:
                        slot = 0
                    else:
                        slot = event.key - pygame.K_0
                    self.inventory.select_slot(slot)
                    self.farmer.held_tool = self.inventory.get_selected_tool()
            elif event.type == pygame.MOUSEMOTION:
                self.grid.handle_hover(event.pos)
                # Check for wood collection on hover
                self._check_wood_collection(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Check if inventory was clicked
                    if self.inventory_rect and self.inventory_rect.collidepoint(event.pos):
                        if self.inventory.handle_click(event.pos, self.inventory_rect):
                            self.farmer.held_tool = self.inventory.get_selected_tool()
                    else:
                        # Use tool on grid
                        self._use_tool(event.pos)
                        # Also handle grid selection
                        self.grid.handle_click(event.pos)
        
        # Handle continuous key presses for movement
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = 1
        
        if dx != 0 or dy != 0:
            obstacles = self._get_obstacles()
            self.player.move(dx, dy, self.game_bounds, obstacles)
        
        return True
    
    def update(self):
        """Update game state"""
        # Update UI with selected cell info
        self.ui.update(self.grid.selected_cell)
        
        # Update inventory animations
        self.inventory.update()
        
        # Update farmer's tool shake angle
        self.farmer.tool_shake_angle = self.inventory.get_shake_angle()
        
        # Update trees (for shake animation)
        for tree in self.trees:
            tree.update()
    
    def draw(self):
        """Draw the game with proper Y-sorting for depth"""
        # Draw sky background
        self.screen.fill(SKY_BLUE)
        
        # Draw grass area around grid
        grass_rect = pygame.Rect(
            GRID_OFFSET_X - 20,
            GRID_OFFSET_Y - 20,
            GRID_COLS * GRID_SIZE + 40,
            GRID_ROWS * GRID_SIZE + 40
        )
        pygame.draw.rect(self.screen, GREEN, grass_rect)
        pygame.draw.rect(self.screen, (0, 50, 0), grass_rect, 3)
        
        # Draw grid (ground layer)
        self.grid.draw(self.screen)
        
        # Collect all renderable objects with their Y-sort position
        render_list = []
        
        # Add farmer
        render_list.append(('farmer', self.farmer.sort_y, self.farmer))
        
        # Add trees
        for tree in self.trees:
            render_list.append(('tree', tree.sort_y, tree))
        
        # Add house (draws its own stone path)
        if self.house:
            render_list.append(('house', self.house.sort_y, self.house))
        
        # Add chest
        if self.chest:
            render_list.append(('chest', self.chest.sort_y, self.chest))
        
        # Sort by Y position (objects with lower Y drawn first)
        render_list.sort(key=lambda x: x[1])
        
        # Draw all objects in sorted order
        for obj_type, sort_y, obj in render_list:
            obj.draw(self.screen)
        
        # Draw UI on top
        self.ui.draw(self.screen)
        
        # Draw inventory at bottom of screen (10 slots)
        slot_total_width = 10 * 45 + 9 * 8  # 10 slots with spacing
        inventory_x = SCREEN_WIDTH // 2 - slot_total_width // 2
        inventory_y = SCREEN_HEIGHT - 80
        self.inventory_rect = self.inventory.draw(self.screen, inventory_x, inventory_y)
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            
            if not self.handle_events():
                break
            
            self.update()
            self.draw()
        
        return True  # Game finished normally