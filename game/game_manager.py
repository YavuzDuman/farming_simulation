"""
Game Manager - Handles game state and main game loop with Y-sorting
"""
import pygame
import random
import time
import json
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, SKY_BLUE, GREEN,
    GRID_OFFSET_X, GRID_OFFSET_Y, GRID_COLS, GRID_ROWS, GRID_SIZE
)
from game.grid import Grid, PlantType
from game.player import Player
from entities.farmer import Farmer
from entities.tree import Tree
from entities.house import House
from entities.chest import Chest
from entities.stone import Stone
from entities.shop import Shop
from ui.game_ui import GameUI
from game.inventory import Inventory, ToolType, ItemType, Item
from ui.shop_ui import ShopUI
from ui.extended_inventory import ExtendedInventoryUI
from ui.tasks_ui import TasksUI


# Regeneration settings
TARGET_TREE_COUNT = 20
TARGET_STONE_COUNT = 10
REGENERATION_DELAY = 60.0  # seconds


class GameState:
    """Enum for game states"""
    MENU = 0
    PLAYING = 1
    PAUSED = 2


class GameManager:
    """Manages the main game state and logic with Y-sorting for depth"""
    
    def __init__(self, screen: pygame.Surface, username: str, shirt_color: tuple = (70, 130, 180), save_id: Optional[int] = None):
        self.screen = screen
        self.username = username
        self.clock = pygame.time.Clock()
        self.running = True
        self.save_id = save_id
        
        # Initialize game components
        self.grid = Grid()
        self.farmer = Farmer(
            x=GRID_OFFSET_X + GRID_COLS * GRID_SIZE // 2 - 18,
            y=GRID_OFFSET_Y + GRID_ROWS * GRID_SIZE // 2 - 20,
            shirt_color=shirt_color
        )
        self.player = Player(self.farmer)
        self.ui = GameUI(username)
        if self.save_id is not None:
            self.ui.save_button.text = "Save Update"
        
        # Initialize inventory system
        self.inventory = Inventory()
        self.inventory.on_slot_click = self._on_inventory_slot_click
        
        # Store inventory rect for click detection
        self.inventory_rect = None
        
        # Initialize shop UI
        self.shop_ui = ShopUI()
        self.shop_ui.on_buy = self._on_shop_buy
        self.shop_ui.on_sell = self._on_shop_sell
        
        # Initialize extended inventory UI
        self.extended_inventory_ui = ExtendedInventoryUI(self.inventory)
        
        # Initialize tasks UI
        self.tasks_ui = TasksUI()
        
        # Create farm objects (trees, house, chest, stones, shop)
        self.trees: List[Tree] = []
        self.stones: List[Stone] = []
        self.house: Optional[House] = None
        self.chest: Optional[Chest] = None
        self.shop: Optional[Shop] = None
        
        # Regeneration tracking
        self.tree_regeneration_timer = 0.0
        self.stone_regeneration_timer = 0.0
        self.last_tree_count = 0
        self.last_stone_count = 0
        
        self._create_farm_objects()
        
        # Game bounds for player movement
        self.game_bounds = pygame.Rect(
            GRID_OFFSET_X,
            GRID_OFFSET_Y,
            GRID_COLS * GRID_SIZE,
            GRID_ROWS * GRID_SIZE
        )

        if self.save_id is not None:
            self.load_game(self.save_id)
    
    def _create_farm_objects(self):
        """Create trees, house, chest, stones, and shop on the farm"""
        # Create house using grid coordinates (col, row)
        # House is 4 cells wide, so place it at column 1, row 1
        self.house = House(1, 1, GRID_OFFSET_X, GRID_OFFSET_Y)
        
        # Create chest next to house (one grid cell)
        # Place it at column 5, row 2 (next to house)
        self.chest = Chest(5, 2, GRID_OFFSET_X, GRID_OFFSET_Y)
        
        # Create shop on the top right of the grid
        # Shop is 4 cells wide, 3 cells tall
        # Place it at column GRID_COLS - 4, row 0 (top right area)
        self.shop = Shop(GRID_COLS - 4, 0, GRID_OFFSET_X, GRID_OFFSET_Y)
        
        # Get occupied cells (house, chest, and shop area)
        occupied_cells = self._get_occupied_cells()
        
        # Create trees scattered around the farm
        self._spawn_trees(TARGET_TREE_COUNT, occupied_cells)
        
        # Create stones scattered on the farm
        self._spawn_stones(TARGET_STONE_COUNT, occupied_cells)
        
        # Initialize last counts
        self.last_tree_count = self._count_alive_trees()
        self.last_stone_count = self._count_alive_stones()
    
    def _get_occupied_cells(self) -> set:
        """Get cells that are occupied by house, chest, shop, or other objects"""
        occupied = set()
        # Mark house and chest areas as occupied
        for hc in range(0, 6):
            for hr in range(0, 4):
                occupied.add((hc, hr))
        # Mark shop area as occupied (4 cells wide, 3 cells tall)
        for sc in range(GRID_COLS - 4, GRID_COLS):
            for sr in range(0, 3):
                occupied.add((sc, sr))
        return occupied
    
    def _count_alive_trees(self) -> int:
        """Count living trees"""
        return sum(1 for tree in self.trees if tree.is_alive)
    
    def _count_alive_stones(self) -> int:
        """Count living stones"""
        return sum(1 for stone in self.stones if stone.is_alive)
    
    def _spawn_trees(self, count: int, occupied_cells: set = None):
        """Spawn trees randomly on the farm"""
        if occupied_cells is None:
            occupied_cells = self._get_occupied_cells()
        
        # Add existing tree positions to occupied cells
        for tree in self.trees:
            if tree.is_alive:
                occupied_cells.add((tree.grid_col, tree.grid_row))
        
        # Add existing stone positions to occupied cells
        for stone in self.stones:
            if stone.is_alive:
                occupied_cells.add((stone.grid_col, stone.grid_row))
        
        placed = 0
        attempts = 0
        max_attempts = count * 10
        
        while placed < count and attempts < max_attempts:
            col = random.randint(0, GRID_COLS - 1)
            row = random.randint(0, GRID_ROWS - 1)
            
            if (col, row) not in occupied_cells:
                # Random size with weighted distribution
                size = random.choices(
                    ["small", "medium", "large"],
                    weights=[2, 5, 3]  # More medium trees
                )[0]
                
                x = GRID_OFFSET_X + col * GRID_SIZE + GRID_SIZE // 2
                y = GRID_OFFSET_Y + row * GRID_SIZE + GRID_SIZE // 2
                self.trees.append(Tree(x, y, size))
                occupied_cells.add((col, row))
                placed += 1
            
            attempts += 1
    
    def _spawn_stones(self, count: int, occupied_cells: set = None):
        """Spawn stones randomly on the farm"""
        if occupied_cells is None:
            occupied_cells = self._get_occupied_cells()
        
        # Add existing tree positions to occupied cells
        for tree in self.trees:
            if tree.is_alive:
                occupied_cells.add((tree.grid_col, tree.grid_row))
        
        # Add existing stone positions to occupied cells
        for stone in self.stones:
            if stone.is_alive:
                occupied_cells.add((stone.grid_col, stone.grid_row))
        
        placed = 0
        attempts = 0
        max_attempts = count * 10
        
        while placed < count and attempts < max_attempts:
            col = random.randint(0, GRID_COLS - 1)
            row = random.randint(0, GRID_ROWS - 1)
            
            if (col, row) not in occupied_cells:
                # Random size with weighted distribution
                size = random.choices(
                    ["small", "medium", "large"],
                    weights=[3, 4, 3]  # Slightly more medium stones
                )[0]
                
                self.stones.append(Stone(col, row, size))
                occupied_cells.add((col, row))
                placed += 1
            
            attempts += 1
    
    def _get_obstacles(self) -> list:
        """Get all objects that the player can't walk through"""
        obstacles = []
        if self.house:
            obstacles.append(self.house)
        if self.chest:
            obstacles.append(self.chest)
        if self.shop:
            obstacles.append(self.shop)
        obstacles.extend(self.trees)
        obstacles.extend([s for s in self.stones if s.is_alive])
        return obstacles
    
    def _on_inventory_slot_click(self, slot_index: int):
        """Called when an inventory slot is clicked"""
        # Update farmer's held tool/item
        self.farmer.held_tool = self.inventory.get_selected_tool()
    
    def _on_shop_buy(self, shop_item) -> bool:
        """Handle buying an item from the shop. Returns True if successful."""
        from ui.shop_ui import ShopItem
        if not isinstance(shop_item, ShopItem):
            return False
        
        # Check if player has enough money
        if self.player.money < shop_item.price:
            return False
        
        # Deduct money
        self.player.spend_money(shop_item.price)
        
        # Add item to inventory (try hotbar first, then extended)
        new_item = Item(shop_item.item_type, 1)
        success = self.inventory.add_item(new_item)
        
        if not success:
            # Try extended inventory
            success = self.extended_inventory_ui.add_item(new_item)
        
        if not success:
            # Refund money if both inventories are full
            self.player.add_money(shop_item.price)
            self.shop_ui.show_message("Inventory full!", (255, 100, 100))
            return False
        
        # Update farmer's held tool
        self.farmer.held_tool = self.inventory.get_selected_tool()
        return True
    
    def _on_shop_sell(self, sell_info) -> bool:
        """Handle selling an item to the shop. Returns True if successful."""
        if not isinstance(sell_info, tuple) or len(sell_info) != 3:
            return False
        
        slot_idx, item, price = sell_info
        
        if not isinstance(item, Item):
            return False
        
        # Remove one item from the stack
        if item.quantity > 1:
            item.quantity -= 1
        else:
            # Remove the item completely from the slot
            self.inventory.slots[slot_idx] = None
        
        # Add money to player
        self.player.add_money(price)
        
        # Update farmer's held tool
        self.farmer.held_tool = self.inventory.get_selected_tool()
        
        self.shop_ui.show_message(f"Sold for {price} coins!", GREEN)
        return True
    
    def _get_seed_xp(self, seed_type: ItemType) -> int:
        """Get XP for planting a seed based on its shop price."""
        seed_prices = {
            ItemType.SEED: 10,
            ItemType.CARROT_SEED: 15,
            ItemType.TOMATO_SEED: 25,
            ItemType.PUMPKIN_SEED: 35,
            ItemType.STRAWBERRY_SEED: 50,
            ItemType.GOLDEN_SEED: 100,
        }
        base_price = seed_prices.get(ItemType.SEED, 10)
        price = seed_prices.get(seed_type, base_price)
        base_xp = self.player.get_xp_for_activity('plant_seed')
        ratio = price / base_price
        return max(1, int(base_xp * ratio))
    
    def _get_allowed_grid_coords(self) -> set[tuple[int, int]]:
        """Get grid coordinates adjacent to the farmer (including current cell)."""
        farmer_col, farmer_row = self.player.get_grid_position()
        allowed_coords = set()
        for dcol in (-1, 0, 1):
            for drow in (-1, 0, 1):
                col = farmer_col + dcol
                row = farmer_row + drow
                if 0 <= col < GRID_COLS and 0 <= row < GRID_ROWS:
                    allowed_coords.add((col, row))
        return allowed_coords

    def _get_save_db_path(self) -> str:
        """Get the sqlite path for saves."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, "saves.db")

    def _ensure_save_table(self, conn: sqlite3.Connection):
        """Ensure the saves table exists."""
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
        conn.commit()

    def _serialize_inventory(self) -> List[Dict[str, Any]]:
        """Serialize inventory slots for saving."""
        slots_data: List[Dict[str, Any]] = []
        for slot in self.inventory.slots:
            if slot is None:
                slots_data.append({"type": None})
            elif isinstance(slot, Item):
                slots_data.append({
                    "type": "item",
                    "item_type": slot.item_type.value,
                    "quantity": slot.quantity
                })
            else:
                slots_data.append({
                    "type": "tool",
                    "tool_type": slot.tool_type.value
                })
        return slots_data

    def _apply_inventory_state(self, slots_data: List[Dict[str, Any]]):
        """Apply inventory slots from saved data."""
        if not slots_data:
            return
        new_slots: List[Optional[object]] = []
        for slot in slots_data:
            if slot.get("type") is None:
                new_slots.append(None)
            elif slot.get("type") == "item":
                item_type = ItemType(slot["item_type"])
                new_slots.append(Item(item_type, slot.get("quantity", 1)))
            elif slot.get("type") == "tool":
                tool_type = ToolType(slot["tool_type"])
                new_slots.append(self.inventory._create_tool_from_type(tool_type))
        if len(new_slots) == len(self.inventory.slots):
            self.inventory.slots = new_slots
            self.inventory.selected_slot = min(self.inventory.selected_slot, len(new_slots) - 1)
            self.farmer.held_tool = self.inventory.get_selected_tool()

    def _serialize_grid(self) -> List[Dict[str, Any]]:
        """Serialize grid cell state for saving."""
        grid_data: List[Dict[str, Any]] = []
        for row in self.grid.cells:
            for cell in row:
                grid_data.append({
                    "col": cell.col,
                    "row": cell.row,
                    "is_tilled": cell.is_tilled,
                    "plant_state": cell.plant_state,
                    "plant_type": cell.plant_type,
                    "plant_time": cell.plant_time,
                    "has_wheat_dropped": cell.has_wheat_dropped,
                    "wheat_quantity": cell.wheat_quantity,
                    "has_carrot_dropped": cell.has_carrot_dropped,
                    "carrot_quantity": cell.carrot_quantity,
                    "has_seed_dropped": cell.has_seed_dropped,
                    "seed_quantity": cell.seed_quantity,
                    "has_carrot_seed_dropped": cell.has_carrot_seed_dropped,
                    "carrot_seed_quantity": cell.carrot_seed_quantity
                })
        return grid_data

    def _apply_grid_state(self, grid_data: List[Dict[str, Any]]):
        """Apply grid cell state from saved data."""
        for cell_data in grid_data:
            col = cell_data.get("col")
            row = cell_data.get("row")
            if col is None or row is None:
                continue
            cell = self.grid.get_cell(col, row)
            if not cell:
                continue
            cell.is_tilled = cell_data.get("is_tilled", False)
            cell.plant_state = cell_data.get("plant_state", 0)
            cell.plant_type = cell_data.get("plant_type", "wheat")
            cell.plant_time = cell_data.get("plant_time", 0)
            cell.has_wheat_dropped = cell_data.get("has_wheat_dropped", False)
            cell.wheat_quantity = cell_data.get("wheat_quantity", 0)
            cell.has_carrot_dropped = cell_data.get("has_carrot_dropped", False)
            cell.carrot_quantity = cell_data.get("carrot_quantity", 0)
            cell.has_seed_dropped = cell_data.get("has_seed_dropped", False)
            cell.seed_quantity = cell_data.get("seed_quantity", 0)
            cell.has_carrot_seed_dropped = cell_data.get("has_carrot_seed_dropped", False)
            cell.carrot_seed_quantity = cell_data.get("carrot_seed_quantity", 0)

    def _serialize_entities(self) -> Dict[str, Any]:
        """Serialize trees, stones, chest, and farmer state."""
        return {
            "farmer": {
                "x": self.farmer.x,
                "y": self.farmer.y,
                "direction": self.farmer.direction,
                "shirt_color": self.farmer.shirt_color
            },
            "player": {
                "level": self.player.level,
                "xp": self.player.xp,
                "money": self.player.money
            },
            "trees": [
                {
                    "x": tree.x,
                    "y": tree.y,
                    "size": tree.size,
                    "is_alive": tree.is_alive,
                    "current_hits": tree.current_hits,
                    "wood_dropped": tree.wood_dropped,
                    "wood_quantity": tree.wood_quantity,
                    "grid_col": tree.grid_col,
                    "grid_row": tree.grid_row
                }
                for tree in self.trees
            ],
            "stones": [
                {
                    "grid_col": stone.grid_col,
                    "grid_row": stone.grid_row,
                    "size": stone.size,
                    "is_alive": stone.is_alive,
                    "current_hits": stone.current_hits,
                    "stone_dropped": stone.stone_dropped,
                    "stone_quantity": stone.stone_quantity
                }
                for stone in self.stones
            ],
            "chest": {
                "grid_col": self.chest.grid_col if self.chest else 0,
                "grid_row": self.chest.grid_row if self.chest else 0,
                "is_open": self.chest.is_open if self.chest else False,
                "slots": [
                    None if slot is None else {
                        "item_type": slot.item_type.value,
                        "quantity": slot.quantity
                    }
                    for slot in (self.chest.slots if self.chest else [])
                ]
            }
        }

    def _apply_entities_state(self, data: Dict[str, Any]):
        """Apply entity state from saved data."""
        farmer_data = data.get("farmer", {})
        if farmer_data:
            self.farmer.x = farmer_data.get("x", self.farmer.x)
            self.farmer.y = farmer_data.get("y", self.farmer.y)
            self.farmer.direction = farmer_data.get("direction", self.farmer.direction)
            shirt_color = farmer_data.get("shirt_color")
            if shirt_color and isinstance(shirt_color, (list, tuple)) and len(shirt_color) == 3:
                # Validate each color component is in valid range 0-255
                valid_color = all(isinstance(c, (int, float)) and 0 <= c <= 255 for c in shirt_color)
                if valid_color:
                    self.farmer.shirt_color = tuple(int(c) for c in shirt_color)
        
        # Load player level and XP
        player_data = data.get("player", {})
        if player_data:
            self.player.level = player_data.get("level", 1)
            self.player.xp = player_data.get("xp", 0)
            self.player.money = player_data.get("money", 100)
            self.player.xp_to_next_level = self.player._calculate_xp_for_level(self.player.level)

        self.trees = []
        for tree_data in data.get("trees", []):
            tree = Tree(tree_data["x"], tree_data["y"], tree_data.get("size", "medium"))
            tree.is_alive = tree_data.get("is_alive", True)
            tree.current_hits = tree_data.get("current_hits", 0)
            tree.wood_dropped = tree_data.get("wood_dropped", False)
            tree.wood_quantity = tree_data.get("wood_quantity", tree.wood_quantity)
            tree.grid_col = tree_data.get("grid_col", tree.grid_col)
            tree.grid_row = tree_data.get("grid_row", tree.grid_row)
            if tree.wood_dropped:
                tree.wood_x = tree.x
                tree.wood_y = tree.y
            self.trees.append(tree)

        self.stones = []
        for stone_data in data.get("stones", []):
            stone = Stone(stone_data["grid_col"], stone_data["grid_row"], stone_data.get("size", "medium"))
            stone.is_alive = stone_data.get("is_alive", True)
            stone.current_hits = stone_data.get("current_hits", 0)
            stone.stone_dropped = stone_data.get("stone_dropped", False)
            stone.stone_quantity = stone_data.get("stone_quantity", stone.stone_quantity)
            if stone.stone_dropped:
                stone.stone_x = stone.x
                stone.stone_y = stone.y
            self.stones.append(stone)

        chest_data = data.get("chest")
        if chest_data and self.chest:
            self.chest.grid_col = chest_data.get("grid_col", self.chest.grid_col)
            self.chest.grid_row = chest_data.get("grid_row", self.chest.grid_row)
            self.chest.x = GRID_OFFSET_X + self.chest.grid_col * GRID_SIZE + GRID_SIZE // 2
            self.chest.y = GRID_OFFSET_Y + self.chest.grid_row * GRID_SIZE + GRID_SIZE // 2
            self.chest.render_rect = pygame.Rect(
                self.chest.x - self.chest.width // 2,
                self.chest.y - self.chest.height // 2,
                self.chest.width,
                self.chest.height
            )
            self.chest.collision_rect = pygame.Rect(
                GRID_OFFSET_X + self.chest.grid_col * GRID_SIZE,
                GRID_OFFSET_Y + self.chest.grid_row * GRID_SIZE,
                GRID_SIZE,
                GRID_SIZE
            )
            self.chest.is_open = chest_data.get("is_open", False)
            slots_data = chest_data.get("slots", [])
            if slots_data:
                new_slots = []
                for slot in slots_data:
                    if slot is None:
                        new_slots.append(None)
                    else:
                        new_slots.append(Item(ItemType(slot["item_type"]), slot.get("quantity", 1)))
                if len(new_slots) == len(self.chest.slots):
                    self.chest.slots = new_slots

    def _build_save_payload(self) -> Dict[str, Any]:
        """Build the save payload for persistence."""
        return {
            "player": {
                "username": self.username
            },
            "inventory": self._serialize_inventory(),
            "grid": self._serialize_grid(),
            "entities": self._serialize_entities(),
            "selected_slot": self.inventory.selected_slot
        }

    def save_game(self):
        """Save current game state to sqlite."""
        db_path = self._get_save_db_path()
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        payload = self._build_save_payload()
        now = datetime.utcnow().isoformat()
        with sqlite3.connect(db_path) as conn:
            self._ensure_save_table(conn)
            if self.save_id is None:
                cursor = conn.execute(
                    "INSERT INTO saves (name, created_at, updated_at, data) VALUES (?, ?, ?, ?)",
                    (self.username, now, now, json.dumps(payload))
                )
                self.save_id = cursor.lastrowid
                self.ui.save_button.text = "Save Update"
            else:
                conn.execute(
                    "UPDATE saves SET name = ?, updated_at = ?, data = ? WHERE id = ?",
                    (self.username, now, json.dumps(payload), self.save_id)
                )
            conn.commit()

    def load_game(self, save_id: int) -> bool:
        """Load game state from sqlite."""
        db_path = self._get_save_db_path()
        if not os.path.exists(db_path):
            return False
        with sqlite3.connect(db_path) as conn:
            self._ensure_save_table(conn)
            row = conn.execute(
                "SELECT data FROM saves WHERE id = ?",
                (save_id,)
            ).fetchone()
        if not row:
            return False
        data = json.loads(row[0])
        self.username = data.get("player", {}).get("username", self.username)
        self.ui.username = self.username
        self.inventory.selected_slot = data.get("selected_slot", self.inventory.selected_slot)
        self._apply_inventory_state(data.get("inventory", []))
        self._apply_grid_state(data.get("grid", []))
        self._apply_entities_state(data.get("entities", {}))
        self.ui.save_button.text = "Save Update"
        return True

    def _use_tool(self, mouse_pos: tuple[int, int]):
        """Use the currently selected tool/item"""
        selected = self.inventory.get_selected_tool()
        if not selected:
            return
        
        # Check if it's a seed item
        seed_to_plant = {
            ItemType.SEED: PlantType.WHEAT,
            ItemType.CARROT_SEED: PlantType.CARROT,
            ItemType.TOMATO_SEED: PlantType.TOMATO,
            ItemType.PUMPKIN_SEED: PlantType.PUMPKIN,
            ItemType.STRAWBERRY_SEED: PlantType.STRAWBERRY,
            ItemType.GOLDEN_SEED: PlantType.GOLDEN_WHEAT,
        }
        if isinstance(selected, Item) and selected.item_type in seed_to_plant:
            # Try to plant seed on tilled cell
            cell = self.grid.get_cell_at_position(*mouse_pos)
            if cell and (cell.col, cell.row) in self._get_allowed_grid_coords() and cell.is_tilled and cell.plant_state == 0:  # EMPTY = 0
                plant_type = seed_to_plant[selected.item_type]
                if cell.plant_seed(plant_type):
                    # Award XP for planting seed
                    xp_gained = self._get_seed_xp(selected.item_type)
                    self.player.add_xp(xp_gained)
                    # Show XP message
                    self.ui.add_xp_message('plant_seed', xp_gained)
                    self.tasks_ui.update_task("plant_seed", 1)
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
            if cell and (cell.col, cell.row) in self._get_allowed_grid_coords():
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
                        # Check if farmer is close enough to the tree
                        farmer_center_x = self.farmer.x + self.farmer.width // 2
                        farmer_center_y = self.farmer.y + self.farmer.height // 2
                        distance = ((farmer_center_x - tree.x) ** 2 + (farmer_center_y - tree.y) ** 2) ** 0.5
                        max_distance = GRID_SIZE * 1.5  # Within 1.5 grid cells
                        if distance <= max_distance:
                            # Chop the tree
                            tree_fell = tree.chop()
                            if tree_fell:
                                # Award XP based on tree size
                                xp_activity = f"tree_{tree.size}"
                                xp_gained = self.player.get_xp_for_activity(xp_activity)
                                self.player.add_xp(xp_gained)
                                # Show XP message
                                self.ui.add_xp_message(xp_activity, xp_gained)
                                self.tasks_ui.update_task("cut_tree", 1)
                        break
        
        # Handle hammer smashing stones
        elif tool.tool_type == ToolType.HAMMER:
            # Check if clicking on a stone
            for stone in self.stones:
                if stone.is_alive:
                    # Check if mouse is near the stone
                    stone_rect = stone.render_rect
                    if stone_rect.collidepoint(mouse_pos):
                        # Check if farmer is close enough to the stone
                        farmer_center_x = self.farmer.x + self.farmer.width // 2
                        farmer_center_y = self.farmer.y + self.farmer.height // 2
                        distance = ((farmer_center_x - stone.x) ** 2 + (farmer_center_y - stone.y) ** 2) ** 0.5
                        max_distance = GRID_SIZE * 1.5  # Within 1.5 grid cells
                        if distance <= max_distance:
                            # Smash the stone
                            stone_broke = stone.smash()
                            if stone_broke:
                                # Award XP based on stone size
                                xp_activity = f"stone_{stone.size}"
                                xp_gained = self.player.get_xp_for_activity(xp_activity)
                                self.player.add_xp(xp_gained)
                                # Show XP message
                                self.ui.add_xp_message(xp_activity, xp_gained)
                                self.tasks_ui.update_task("smash_stone", 1)
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
                    else:
                        self.tasks_ui.update_task("collect_wood", wood_collected)
                break

    def _check_stone_collection(self, mouse_pos: tuple[int, int]):
        """Check if hovering over stones and collect them"""
        for stone in self.stones:
            if stone.stone_dropped and stone.check_stone_hover(mouse_pos):
                # Collect the stones
                stone_collected = stone.collect_stone()
                if stone_collected > 0:
                    # Add stones to inventory
                    success = self.inventory.add_stone(stone_collected)
                    if not success:
                        # Inventory full - stones stay on ground
                        stone.stone_dropped = True
                        stone.stone_quantity = stone_collected
                    else:
                        self.tasks_ui.update_task("collect_stone", stone_collected)
                break

    def _harvest_plant(self, mouse_pos: tuple[int, int]):
        """Harvest a grown plant on right-click"""
        cell = self.grid.get_cell_at_position(*mouse_pos)
        if cell and (cell.col, cell.row) in self._get_allowed_grid_coords() and cell.plant_state == 3:  # GROWN = 3
            harvested_qty = cell.harvest()
            if harvested_qty > 0:
                self.tasks_ui.update_task("harvest_crop", 1)
                # Crops are now on the ground in this cell
                pass

    def _check_wheat_collection(self, mouse_pos: tuple[int, int]):
        """Check if hovering over wheat on ground and collect it"""
        cell = self.grid.get_cell_at_position(*mouse_pos)
        if cell and (cell.col, cell.row) in self._get_allowed_grid_coords() and cell.has_wheat_dropped:
            wheat_qty = cell.collect_wheat()
            if wheat_qty > 0:
                # Add wheat to inventory
                wheat_item = Item(ItemType.WHEAT, wheat_qty)
                success = self.inventory.add_item(wheat_item)
                if not success:
                    # Return wheat to ground if inventory full
                    cell.has_wheat_dropped = True
                    cell.wheat_quantity = wheat_qty
    
    def _check_tomato_collection(self, mouse_pos: tuple[int, int]):
        """Check if hovering over tomatoes on ground and collect them"""
        cell = self.grid.get_cell_at_position(*mouse_pos)
        if cell and (cell.col, cell.row) in self._get_allowed_grid_coords() and cell.has_tomato_dropped:
            tomato_qty = cell.collect_tomato()
            if tomato_qty > 0:
                tomato_item = Item(ItemType.TOMATO, tomato_qty)
                success = self.inventory.add_item(tomato_item)
                if not success:
                    cell.has_tomato_dropped = True
                    cell.tomato_quantity = tomato_qty
    
    def _check_pumpkin_collection(self, mouse_pos: tuple[int, int]):
        """Check if hovering over pumpkins on ground and collect them"""
        cell = self.grid.get_cell_at_position(*mouse_pos)
        if cell and (cell.col, cell.row) in self._get_allowed_grid_coords() and cell.has_pumpkin_dropped:
            pumpkin_qty = cell.collect_pumpkin()
            if pumpkin_qty > 0:
                pumpkin_item = Item(ItemType.PUMPKIN, pumpkin_qty)
                success = self.inventory.add_item(pumpkin_item)
                if not success:
                    cell.has_pumpkin_dropped = True
                    cell.pumpkin_quantity = pumpkin_qty
    
    def _check_strawberry_collection(self, mouse_pos: tuple[int, int]):
        """Check if hovering over strawberries on ground and collect them"""
        cell = self.grid.get_cell_at_position(*mouse_pos)
        if cell and (cell.col, cell.row) in self._get_allowed_grid_coords() and cell.has_strawberry_dropped:
            strawberry_qty = cell.collect_strawberry()
            if strawberry_qty > 0:
                strawberry_item = Item(ItemType.STRAWBERRY, strawberry_qty)
                success = self.inventory.add_item(strawberry_item)
                if not success:
                    cell.has_strawberry_dropped = True
                    cell.strawberry_quantity = strawberry_qty
    
    def _check_golden_wheat_collection(self, mouse_pos: tuple[int, int]):
        """Check if hovering over golden wheat on ground and collect it"""
        cell = self.grid.get_cell_at_position(*mouse_pos)
        if cell and (cell.col, cell.row) in self._get_allowed_grid_coords() and cell.has_golden_wheat_dropped:
            golden_wheat_qty = cell.collect_golden_wheat()
            if golden_wheat_qty > 0:
                golden_wheat_item = Item(ItemType.GOLDEN_WHEAT, golden_wheat_qty)
                success = self.inventory.add_item(golden_wheat_item)
                if not success:
                    cell.has_golden_wheat_dropped = True
                    cell.golden_wheat_quantity = golden_wheat_qty
    
    def _check_carrot_collection(self, mouse_pos: tuple[int, int]):
        """Check if hovering over carrots on ground and collect them"""
        cell = self.grid.get_cell_at_position(*mouse_pos)
        if cell and (cell.col, cell.row) in self._get_allowed_grid_coords() and cell.has_carrot_dropped:
            carrot_qty = cell.collect_carrot()
            if carrot_qty > 0:
                # Add carrots to inventory
                carrot_item = Item(ItemType.CARROT, carrot_qty)
                success = self.inventory.add_item(carrot_item)
                if not success:
                    # Return carrots to ground if inventory full
                    cell.has_carrot_dropped = True
                    cell.carrot_quantity = carrot_qty
    
    def _check_seed_collection(self, mouse_pos: tuple[int, int]):
        """Check if hovering over seeds on ground and collect them"""
        cell = self.grid.get_cell_at_position(*mouse_pos)
        if cell and (cell.col, cell.row) in self._get_allowed_grid_coords() and cell.has_seed_dropped:
            seed_qty = cell.collect_seed()
            if seed_qty > 0:
                # Add seeds to inventory
                seed_item = Item(ItemType.SEED, seed_qty)
                success = self.inventory.add_item(seed_item)
                if not success:
                    # Return seeds to ground if inventory full
                    cell.has_seed_dropped = True
                    cell.seed_quantity = seed_qty
    
    def _check_carrot_seed_collection(self, mouse_pos: tuple[int, int]):
        """Check if hovering over carrot seeds on ground and collect them"""
        cell = self.grid.get_cell_at_position(*mouse_pos)
        if cell and (cell.col, cell.row) in self._get_allowed_grid_coords() and cell.has_carrot_seed_dropped:
            seed_qty = cell.collect_carrot_seed()
            if seed_qty > 0:
                # Add carrot seeds to inventory
                seed_item = Item(ItemType.CARROT_SEED, seed_qty)
                success = self.inventory.add_item(seed_item)
                if not success:
                    # Return carrot seeds to ground if inventory full
                    cell.has_carrot_seed_dropped = True
                    cell.carrot_seed_quantity = seed_qty
    
    def handle_events(self) -> str:
        """Handle game events, returns 'quit', 'menu', or 'continue'"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            # Handle tasks UI events first if open
            if self.tasks_ui.is_open:
                tasks_action = self.tasks_ui.handle_event(event)
                if tasks_action == "close":
                    pass  # Tasks UI was closed
                continue  # Skip other event handling when tasks UI is open
            
            # Handle extended inventory UI events first if open
            if self.extended_inventory_ui.is_open:
                ext_inv_action = self.extended_inventory_ui.handle_event(event)
                if ext_inv_action == "close":
                    pass  # Extended inventory was closed
                continue  # Skip other event handling when extended inventory is open
            
            # Handle shop UI events first if shop is open
            if self.shop_ui.is_open:
                shop_action = self.shop_ui.handle_event(event)
                if shop_action == "close":
                    pass  # Shop was closed
                continue  # Skip other event handling when shop is open
            
            ui_action = self.ui.handle_event(event)
            if ui_action == "tasks":
                self.tasks_ui.toggle()
            elif ui_action == "save":
                self.save_game()
            elif ui_action == "menu":
                return "menu"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
                # E key to toggle extended inventory
                if event.key == pygame.K_e:
                    self.extended_inventory_ui.toggle()
                # Number keys for quick slot selection (0-9)
                if pygame.K_0 <= event.key <= pygame.K_9:
                    if event.key == pygame.K_0:
                        slot = 0
                    else:
                        slot = event.key - pygame.K_0
                    self.inventory.select_slot(slot)
                    self.farmer.held_tool = self.inventory.get_selected_tool()
            elif event.type == pygame.MOUSEMOTION:
                self.grid.handle_hover(event.pos, self._get_allowed_grid_coords())
                # Check for wood collection on hover
                self._check_wood_collection(event.pos)
                # Check for stone collection on hover
                self._check_stone_collection(event.pos)
                # Check for wheat collection on hover
                self._check_wheat_collection(event.pos)
                # Check for carrot collection on hover
                self._check_carrot_collection(event.pos)
                # Check for tomato collection on hover
                self._check_tomato_collection(event.pos)
                # Check for pumpkin collection on hover
                self._check_pumpkin_collection(event.pos)
                # Check for strawberry collection on hover
                self._check_strawberry_collection(event.pos)
                # Check for golden wheat collection on hover
                self._check_golden_wheat_collection(event.pos)
                # Check for seed collection on hover
                self._check_seed_collection(event.pos)
                # Check for carrot seed collection on hover
                self._check_carrot_seed_collection(event.pos)
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
                        self.grid.handle_click(event.pos, self._get_allowed_grid_coords())
                
                elif event.button == 3:  # Right click
                    # Check if clicking on shop building (right-click to open)
                    if self.shop and self.shop.collision_rect.collidepoint(event.pos):
                        self.shop_ui.open(self.player, self.inventory)
                        continue
                    
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
    
    def update(self, dt: float):
        """Update game state"""
        # Update UI with selected cell info
        self.ui.update(self.grid.selected_cell)
        
        # Update XP display in UI
        self.ui.update_xp_display(
            self.player.level,
            self.player.xp,
            self.player.xp_to_next_level,
            self.player.get_xp_progress_percentage()
        )
        
        # Update money display in UI
        self.ui.update_money_display(self.player.money)
        
        # Update inventory animations
        self.inventory.update()
        
        # Update shop UI
        self.shop_ui.update(dt)
        
        # Update trees (for shake animation)
        for tree in self.trees:
            tree.update()
        
        # Update stones (for shake animation)
        for stone in self.stones:
            stone.update()
        
        # Update grid (plant growth)
        self.grid.update(time.time())
        
        # Handle tree regeneration
        current_tree_count = self._count_alive_trees()
        if current_tree_count < self.last_tree_count:
            # A tree was cut, start regeneration timer
            if self.tree_regeneration_timer <= 0:
                self.tree_regeneration_timer = REGENERATION_DELAY
        
        if self.tree_regeneration_timer > 0:
            self.tree_regeneration_timer -= dt
            if self.tree_regeneration_timer <= 0:
                # Time to regenerate trees
                trees_needed = TARGET_TREE_COUNT - current_tree_count
                if trees_needed > 0:
                    self._spawn_trees(trees_needed, self._get_occupied_cells())
        
        self.last_tree_count = current_tree_count
        
        # Handle stone regeneration
        current_stone_count = self._count_alive_stones()
        if current_stone_count < self.last_stone_count:
            # A stone was smashed, start regeneration timer
            if self.stone_regeneration_timer <= 0:
                self.stone_regeneration_timer = REGENERATION_DELAY
        
        if self.stone_regeneration_timer > 0:
            self.stone_regeneration_timer -= dt
            if self.stone_regeneration_timer <= 0:
                # Time to regenerate stones
                stones_needed = TARGET_STONE_COUNT - current_stone_count
                if stones_needed > 0:
                    self._spawn_stones(stones_needed, self._get_occupied_cells())
        
        self.last_stone_count = current_stone_count
    
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
        
        # Add stones
        for stone in self.stones:
            render_list.append(('stone', stone.sort_y, stone))
        
        # Add house (draws its own stone path)
        if self.house:
            render_list.append(('house', self.house.sort_y, self.house))
        
        # Add chest
        if self.chest:
            render_list.append(('chest', self.chest.sort_y, self.chest))
        
        # Add shop
        if self.shop:
            render_list.append(('shop', self.shop.sort_y, self.shop))
        
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
        mouse_pos = pygame.mouse.get_pos()
        self.inventory_rect = self.inventory.draw(self.screen, inventory_x, inventory_y, mouse_pos)
        
        # Draw shop UI if open
        self.shop_ui.draw(self.screen)
        
        # Draw extended inventory UI if open
        self.extended_inventory_ui.draw(self.screen)
        
        # Draw tasks UI if open
        self.tasks_ui.draw(self.screen)
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            
            if not self.handle_events():
                break
            
            self.update(dt)
            self.draw()
        
        return "continue"
