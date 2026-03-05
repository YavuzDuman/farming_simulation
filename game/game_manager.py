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
from game.inventory import Inventory, ToolType, ItemType, Item


class GameState:
    """Enum for game states"""
    MENU = 0
    PLAYING = 1
    PAUSED = 2


class GameManager:
    """Manages the main game state and logic with Y-sorting for depth"""
    
    def __init__(self, screen: pygame.Surface, username: str, shirt_color: tuple = (70, 130, 180)):
        self.screen = screen
        self.username = username
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize game components
        self.grid = Grid()
        self.farmer = Farmer(
            x=GRID_OFFSET_X + GRID_COLS * GRID_SIZE // 2 - 18,
            y=GRID_OFFSET_Y + GRID_ROWS * GRID_SIZE // 2 - 20,
            shirt_color=shirt_color
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
        # Update farmer's held tool/item
        self.farmer.held_tool = self.inventory.get_selected_tool()
    
    def _use_tool(self, mouse_pos: tuple[int, int]):
        """Use the currently selected tool/item"""
        selected = self.inventory.get_selected_tool()
        if not selected:
            return
        
        # Check if it's a seed item
        if isinstance(selected, Item) and selected.item_type == ItemType.SEED:
            # Try to plant seed on tilled cell
            cell = self.grid.get_cell_at_position(*mouse_pos)
            if cell and cell.is_tilled and cell.plant_state == 0:  # EMPTY = 0
                if cell.plant_seed():
                    # Consume one seed
                    selected.quantity -= 1
                    if selected.quantity <= 0:
                        # Remove seed from inventory
                        self.inventory.slots[self.inventory.selected_slot] = None
                        self.farmer.held_tool = None
                    return
            return
        
        # Only allow using tools (not items like wood or wheat)
        if not hasattr(selected, 'tool_type'):
            return
        
        tool = selected
        # Start swing animation
        self.farmer.start_tool_swing()
        
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

    def _harvest_plant(self, mouse_pos: tuple[int, int]):
        """Harvest a grown plant on right-click"""
        cell = self.grid.get_cell_at_position(*mouse_pos)
        if cell and cell.plant_state == 3:  # GROWN = 3
            wheat_qty = cell.harvest()
            if wheat_qty > 0:
                # Wheat is now on the ground in this cell
                pass

    def _check_wheat_collection(self, mouse_pos: tuple[int, int]):
        """Check if hovering over wheat on ground and collect it"""
        cell = self.grid.get_cell_at_position(*mouse_pos)
        if cell and cell.has_wheat_dropped:
            wheat_qty = cell.collect_wheat()
            if wheat_qty > 0:
                # Add wheat to inventory
                wheat_item = Item(ItemType.WHEAT, wheat_qty)
                success = self.inventory.add_item(wheat_item)
                if not success:
                    # Return wheat to ground if inventory full
                    cell.has_wheat_dropped = True
                    cell.wheat_quantity = wheat_qty
    
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
                # Check for wheat collection on hover
                self._check_wheat_collection(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Check if chest inventory is open and clicked
                    if self.chest and self.chest.is_open:
                        item = self.chest.handle_click(event.pos)
                        if item:
                            # Transfer to player inventory
                            success = self.inventory.add_item(item)
                            if not success:
                                # Return to chest if inventory full
                                for i in range(10):
                                    if self.chest.slots[i] is None:
                                        self.chest.slots[i] = item
                                        break
                            # Update farmer's hand
                            self.farmer.held_tool = self.inventory.get_selected_tool()
                            continue

                    # Check if inventory was clicked
                    if self.inventory_rect and self.inventory_rect.collidepoint(event.pos):
                        if self.inventory.handle_click(event.pos, self.inventory_rect):
                            self.farmer.held_tool = self.inventory.get_selected_tool()
                    else:
                        # Use tool on grid
                        self._use_tool(event.pos)
                        # Also handle grid selection
                        self.grid.handle_click(event.pos)
                
                elif event.button == 3:  # Right click
                    # Check if clicking on chest
                    if self.chest:
                        if self.chest.render_rect.collidepoint(event.pos):
                            self.chest.toggle_inventory()
                            continue
                    
                    # Try to harvest a grown plant
                    self._harvest_plant(event.pos)
        
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
        
        # Update trees (for shake animation)
        for tree in self.trees:
            tree.update()
        
        # Update grid (plant growth)
        import time
        self.grid.update(time.time())
    
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
        
        # Draw chest inventory if open
        if self.chest and self.chest.is_open:
            self.chest.draw_inventory(self.screen)
        
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