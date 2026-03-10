"""
Shop UI - Buy and Sell interface for the shop building
"""
import pygame
from typing import Optional, Callable, Dict, List, Tuple
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, YELLOW, GREEN, DARK_GREEN, RED
from game.inventory import ItemType, Item, Tool, ToolType, SWORD_DAMAGE


# Seed unlock levels - which level each seed becomes available
SEED_UNLOCK_LEVELS = {
    ItemType.SEED: 1,           # Wheat seeds - unlocked at level 1
    ItemType.CARROT_SEED: 1,    # Carrot seeds - unlocked at level 1
    ItemType.TOMATO_SEED: 3,    # Tomato seeds - unlocked at level 3
    ItemType.PUMPKIN_SEED: 4,   # Pumpkin seeds - unlocked at level 4
    ItemType.STRAWBERRY_SEED: 5, # Strawberry seeds - unlocked at level 5
    ItemType.GOLDEN_SEED: 7,   # Golden seeds - unlocked at level 7
}

# Tool unlock levels
TOOL_UNLOCK_LEVELS = {
    ToolType.IRON_SWORD: 2,
    ToolType.GOLDEN_SWORD: 5,
    ToolType.DIAMOND_SWORD: 8,
}


class ShopTool:
    """Represents a tool that can be bought in the shop"""
    
    def __init__(self, name: str, tool_type: ToolType, price: int, description: str = "", unlock_level: int = 1):
        self.name = name
        self.tool_type = tool_type
        self.price = price
        self.description = description
        self.unlock_level = unlock_level


class ShopItem:
    """Represents an item that can be bought in the shop"""
    
    def __init__(self, name: str, item_type: ItemType, price: int, description: str = "", unlock_level: int = 1):
        self.name = name
        self.item_type = item_type
        self.price = price
        self.description = description
        self.unlock_level = unlock_level


class ShopUI:
    """Shop interface for buying and selling items"""
    
    def __init__(self):
        self.is_open = False
        self.current_tab = "buy"  # "buy" or "sell"
        self.current_category = "seeds"  # "seeds" or "tools"
        
        # Shop dimensions
        self.width = 600
        self.height = 600
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = (SCREEN_HEIGHT - self.height) // 2
        
        # Fonts
        self.title_font = pygame.font.SysFont('Arial', 28, bold=True)
        self.header_font = pygame.font.SysFont('Arial', 22, bold=True)
        self.item_font = pygame.font.SysFont('Arial', 18, bold=True)
        self.small_font = pygame.font.SysFont('Arial', 14)
        
        # Define items available for purchase (seeds)
        self.seed_items: List[ShopItem] = [
            ShopItem("Wheat Seeds", ItemType.SEED, 10, "Plant to grow wheat", unlock_level=1),
            ShopItem("Carrot Seeds", ItemType.CARROT_SEED, 15, "Plant to grow carrots", unlock_level=1),
            ShopItem("Tomato Seeds", ItemType.TOMATO_SEED, 25, "Plant to grow tomatoes", unlock_level=3),
            ShopItem("Pumpkin Seeds", ItemType.PUMPKIN_SEED, 35, "Plant to grow pumpkins", unlock_level=4),
            ShopItem("Strawberry Seeds", ItemType.STRAWBERRY_SEED, 50, "Plant to grow strawberries", unlock_level=5),
            ShopItem("Golden Seeds", ItemType.GOLDEN_SEED, 100, "Rare! Plant to grow golden wheat", unlock_level=7),
        ]
        
        # Define tools available for purchase
        self.tool_items: List[ShopTool] = [
            ShopTool("Iron Sword", ToolType.IRON_SWORD, 150, "Strong iron blade. 2 damage.", unlock_level=2),
            ShopTool("Golden Sword", ToolType.GOLDEN_SWORD, 300, "Golden blade. 3 damage, faster swing.", unlock_level=5),
            ShopTool("Diamond Sword", ToolType.DIAMOND_SWORD, 500, "Diamond blade. 5 damage - one hit kill brute!", unlock_level=8),
        ]
        
        # Tab buttons
        self.buy_tab_rect = pygame.Rect(self.x + 20, self.y + 50, 100, 35)
        self.sell_tab_rect = pygame.Rect(self.x + 130, self.y + 50, 100, 35)
        
        # Category buttons
        self.seeds_cat_rect = pygame.Rect(self.x + 20, self.y + 95, 100, 30)
        self.tools_cat_rect = pygame.Rect(self.x + 130, self.y + 95, 100, 30)
        
        # Close button
        self.close_button_rect = pygame.Rect(self.x + self.width - 40, self.y + 10, 30, 30)
        
        # Item button rects (will be updated when drawing)
        self.item_buttons: List[Tuple[pygame.Rect, ShopItem]] = []
        self.tool_buttons: List[Tuple[pygame.Rect, ShopTool]] = []
        
        # Player reference (set when opened)
        self.player = None
        self.inventory = None
        
        # Callbacks
        self.on_buy: Optional[Callable[[ShopItem], bool]] = None
        self.on_buy_tool: Optional[Callable[[ShopTool], bool]] = None
        self.on_sell: Optional[Callable[[Item], bool]] = None
        
        # Message to display
        self.message = ""
        self.message_color = WHITE
        self.message_timer = 0
    
    def open(self, player, inventory):
        """Open the shop UI"""
        self.is_open = True
        self.current_tab = "buy"
        self.player = player
        self.inventory = inventory
        self.message = ""
    
    def close(self):
        """Close the shop UI"""
        self.is_open = False
        self.player = None
        self.inventory = None
        self.message = ""
    
    def show_message(self, text: str, color: tuple = WHITE, duration: float = 2.0):
        """Show a message in the shop UI"""
        self.message = text
        self.message_color = color
        self.message_timer = duration
    
    def update(self, dt: float):
        """Update the shop UI"""
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Handle events for the shop UI. Returns 'close' if shop should close."""
        if not self.is_open:
            return None
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            
            # Check close button
            if self.close_button_rect.collidepoint(mouse_pos):
                self.close()
                return "close"
            
            # Check tab buttons
            if self.buy_tab_rect.collidepoint(mouse_pos):
                self.current_tab = "buy"
                return None
            
            if self.sell_tab_rect.collidepoint(mouse_pos):
                self.current_tab = "sell"
                return None
            
            # Check category buttons (only in buy tab)
            if self.current_tab == "buy":
                if self.seeds_cat_rect.collidepoint(mouse_pos):
                    self.current_category = "seeds"
                    return None
                
                if self.tools_cat_rect.collidepoint(mouse_pos):
                    self.current_category = "tools"
                    return None
            
            # Check item buttons
            if self.current_tab == "buy":
                # Check seed items
                for rect, item in self.item_buttons:
                    if rect.collidepoint(mouse_pos):
                        # Try to buy the item
                        if self.on_buy:
                            success = self.on_buy(item)
                            if success:
                                self.show_message(f"Bought {item.name}!", GREEN)
                            else:
                                self.show_message("Not enough money!", RED)
                        return None
                
                # Check tool items
                for rect, tool in self.tool_buttons:
                    if rect.collidepoint(mouse_pos):
                        # Try to buy the tool
                        if self.on_buy_tool:
                            success = self.on_buy_tool(tool)
                            if success:
                                self.show_message(f"Bought {tool.name}!", GREEN)
                            else:
                                self.show_message("Not enough money!", RED)
                        return None
                        
            elif self.current_tab == "sell":
                for rect, sell_info in self.item_buttons:
                    if rect.collidepoint(mouse_pos):
                        # Try to sell the item
                        if self.on_sell:
                            self.on_sell(sell_info)
                        return None
            
            # Click outside the shop closes it
            shop_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            if not shop_rect.collidepoint(mouse_pos):
                self.close()
                return "close"
        
        return None
    
    def draw(self, screen: pygame.Surface):
        """Draw the shop UI"""
        if not self.is_open:
            return
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Draw shop panel
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, (60, 40, 30), panel_rect, border_radius=10)
        pygame.draw.rect(screen, (139, 90, 43), panel_rect, 3, border_radius=10)
        
        # Draw title
        title_surface = self.title_font.render("Shop", True, YELLOW)
        title_rect = title_surface.get_rect(centerx=self.x + self.width // 2, top=self.y + 15)
        screen.blit(title_surface, title_rect)
        
        # Draw close button (X)
        pygame.draw.rect(screen, (150, 50, 50), self.close_button_rect, border_radius=5)
        pygame.draw.rect(screen, (200, 80, 80), self.close_button_rect, 2, border_radius=5)
        x_text = self.header_font.render("X", True, WHITE)
        x_rect = x_text.get_rect(center=self.close_button_rect.center)
        screen.blit(x_text, x_rect)
        
        # Draw money display
        if self.player:
            money_text = f"Money: {self.player.money} coins"
            money_surface = self.item_font.render(money_text, True, YELLOW)
            screen.blit(money_surface, (self.x + self.width - 180, self.y + 55))
        
        # Draw tab buttons
        buy_color = (80, 120, 80) if self.current_tab == "buy" else (60, 60, 60)
        sell_color = (80, 120, 80) if self.current_tab == "sell" else (60, 60, 60)
        
        pygame.draw.rect(screen, buy_color, self.buy_tab_rect, border_radius=5)
        pygame.draw.rect(screen, (100, 150, 100) if self.current_tab == "buy" else (80, 80, 80), 
                        self.buy_tab_rect, 2, border_radius=5)
        buy_text = self.item_font.render("Buy", True, WHITE)
        buy_text_rect = buy_text.get_rect(center=self.buy_tab_rect.center)
        screen.blit(buy_text, buy_text_rect)
        
        pygame.draw.rect(screen, sell_color, self.sell_tab_rect, border_radius=5)
        pygame.draw.rect(screen, (100, 150, 100) if self.current_tab == "sell" else (80, 80, 80), 
                        self.sell_tab_rect, 2, border_radius=5)
        sell_text = self.item_font.render("Sell", True, WHITE)
        sell_text_rect = sell_text.get_rect(center=self.sell_tab_rect.center)
        screen.blit(sell_text, sell_text_rect)
        
        # Draw category buttons (only in buy tab)
        if self.current_tab == "buy":
            seeds_color = (100, 140, 100) if self.current_category == "seeds" else (70, 70, 70)
            tools_color = (100, 140, 100) if self.current_category == "tools" else (70, 70, 70)
            
            pygame.draw.rect(screen, seeds_color, self.seeds_cat_rect, border_radius=5)
            pygame.draw.rect(screen, (120, 160, 120) if self.current_category == "seeds" else (90, 90, 90), 
                            self.seeds_cat_rect, 2, border_radius=5)
            seeds_text = self.small_font.render("Seeds", True, WHITE)
            seeds_text_rect = seeds_text.get_rect(center=self.seeds_cat_rect.center)
            screen.blit(seeds_text, seeds_text_rect)
            
            pygame.draw.rect(screen, tools_color, self.tools_cat_rect, border_radius=5)
            pygame.draw.rect(screen, (120, 160, 120) if self.current_category == "tools" else (90, 90, 90), 
                            self.tools_cat_rect, 2, border_radius=5)
            tools_text = self.small_font.render("Tools", True, WHITE)
            tools_text_rect = tools_text.get_rect(center=self.tools_cat_rect.center)
            screen.blit(tools_text, tools_text_rect)
        
        # Draw content based on current tab
        if self.current_tab == "buy":
            self._draw_buy_tab(screen)
        else:
            self._draw_sell_tab(screen)
        
        # Draw message if any
        if self.message:
            msg_surface = self.item_font.render(self.message, True, self.message_color)
            msg_rect = msg_surface.get_rect(centerx=self.x + self.width // 2, bottom=self.y + self.height - 20)
            # Background for message
            bg_rect = msg_rect.inflate(20, 10)
            pygame.draw.rect(screen, (40, 40, 40), bg_rect, border_radius=5)
            screen.blit(msg_surface, msg_rect)
    
    def _draw_buy_tab(self, screen: pygame.Surface):
        """Draw the buy tab content"""
        self.item_buttons = []
        self.tool_buttons = []
        
        # Draw items header
        header_y = self.y + 135
        pygame.draw.line(screen, (139, 90, 43), (self.x + 20, header_y), 
                        (self.x + self.width - 20, header_y), 2)
        
        # Get player level
        player_level = 1
        if self.player:
            player_level = self.player.level
        
        if self.current_category == "seeds":
            self._draw_seeds_category(screen, header_y, player_level)
        else:
            self._draw_tools_category(screen, header_y, player_level)
    
    def _draw_seeds_category(self, screen: pygame.Surface, header_y: int, player_level: int):
        """Draw seeds category items"""
        # Draw items for sale
        item_y = header_y + 20
        item_height = 60
        item_spacing = 10
        
        for i, item in enumerate(self.seed_items):
            is_locked = player_level < item.unlock_level
            
            # Item background (darker if locked)
            item_rect = pygame.Rect(self.x + 30, item_y + i * (item_height + item_spacing), 
                                   self.width - 60, item_height)
            bg_color = (30, 30, 30) if is_locked else (50, 50, 50)
            pygame.draw.rect(screen, bg_color, item_rect, border_radius=5)
            border_color = (60, 60, 60) if is_locked else (80, 80, 80)
            pygame.draw.rect(screen, border_color, item_rect, 2, border_radius=5)
            
            # Item icon (use Item class to get icon)
            temp_item = Item(item.item_type, 1)
            icon = temp_item.icon
            icon_rect = icon.get_rect(center=(item_rect.left + 30, item_rect.centery))
            
            if is_locked:
                # Draw icon with reduced opacity for locked items
                icon.set_alpha(128)
                screen.blit(icon, icon_rect)
                icon.set_alpha(255)  # Reset alpha
            else:
                screen.blit(icon, icon_rect)
            
            # Item name (gray if locked)
            name_color = (128, 128, 128) if is_locked else WHITE
            name_surface = self.item_font.render(item.name, True, name_color)
            screen.blit(name_surface, (item_rect.left + 60, item_rect.top + 10))
            
            # Item description or lock message
            if is_locked:
                lock_text = f"Unlocks at level {item.unlock_level}"
                desc_surface = self.small_font.render(lock_text, True, (255, 150, 150))
            else:
                desc_surface = self.small_font.render(item.description, True, (180, 180, 180))
            screen.blit(desc_surface, (item_rect.left + 60, item_rect.top + 32))
            
            # Price
            price_text = f"{item.price} coins"
            price_surface = self.item_font.render(price_text, True, YELLOW)
            price_rect = price_surface.get_rect(right=item_rect.right - 90, centery=item_rect.centery)
            screen.blit(price_surface, price_rect)
            
            # Buy button (disabled if locked or not enough money)
            buy_button_rect = pygame.Rect(item_rect.right - 80, item_rect.top + 12, 70, 36)
            can_afford = self.player and self.player.money >= item.price and not is_locked
            
            if is_locked:
                button_color = (60, 60, 60)
                border_color = (80, 80, 80)
            elif can_afford:
                button_color = (80, 150, 80)
                border_color = (120, 180, 120)
            else:
                button_color = (100, 60, 60)
                border_color = (140, 100, 100)
            
            pygame.draw.rect(screen, button_color, buy_button_rect, border_radius=5)
            pygame.draw.rect(screen, border_color, buy_button_rect, 2, border_radius=5)
            
            # Button text
            if is_locked:
                buy_text = self.small_font.render("Locked", True, (150, 150, 150))
            else:
                buy_text = self.small_font.render("Buy", True, WHITE)
            buy_text_rect = buy_text.get_rect(center=buy_button_rect.center)
            screen.blit(buy_text, buy_text_rect)
            
            # Store button rect for click detection (only if not locked)
            if not is_locked:
                self.item_buttons.append((buy_button_rect, item))
    
    def _draw_tools_category(self, screen: pygame.Surface, header_y: int, player_level: int):
        """Draw tools category items (swords with damage info)"""
        # Draw tools for sale
        item_y = header_y + 20
        item_height = 70
        item_spacing = 10
        
        for i, tool in enumerate(self.tool_items):
            is_locked = player_level < tool.unlock_level
            
            # Item background (darker if locked)
            item_rect = pygame.Rect(self.x + 30, item_y + i * (item_height + item_spacing), 
                                   self.width - 60, item_height)
            bg_color = (30, 30, 30) if is_locked else (50, 50, 50)
            pygame.draw.rect(screen, bg_color, item_rect, border_radius=5)
            border_color = (60, 60, 60) if is_locked else (80, 80, 80)
            pygame.draw.rect(screen, border_color, item_rect, 2, border_radius=5)
            
            # Tool icon (use Tool class to get icon)
            temp_tool = Tool(tool.tool_type, tool.name)
            icon = temp_tool.icon
            icon_rect = icon.get_rect(center=(item_rect.left + 30, item_rect.centery))
            
            if is_locked:
                # Draw icon with reduced opacity for locked items
                icon.set_alpha(128)
                screen.blit(icon, icon_rect)
                icon.set_alpha(255)  # Reset alpha
            else:
                screen.blit(icon, icon_rect)
            
            # Tool name (gray if locked)
            name_color = (128, 128, 128) if is_locked else WHITE
            name_surface = self.item_font.render(tool.name, True, name_color)
            screen.blit(name_surface, (item_rect.left + 60, item_rect.top + 8))
            
            # Damage info - always show for swords
            damage = SWORD_DAMAGE.get(tool.tool_type, 1)
            damage_text = f"Damage: {damage}"
            damage_color = (100, 100, 100) if is_locked else (255, 100, 100)
            damage_surface = self.small_font.render(damage_text, True, damage_color)
            screen.blit(damage_surface, (item_rect.left + 60, item_rect.top + 28))
            
            # Tool description or lock message
            if is_locked:
                lock_text = f"Unlocks at level {tool.unlock_level}"
                desc_surface = self.small_font.render(lock_text, True, (255, 150, 150))
            else:
                desc_surface = self.small_font.render(tool.description, True, (180, 180, 180))
            screen.blit(desc_surface, (item_rect.left + 60, item_rect.top + 45))
            
            # Price
            price_text = f"{tool.price} coins"
            price_surface = self.item_font.render(price_text, True, YELLOW)
            price_rect = price_surface.get_rect(right=item_rect.right - 90, centery=item_rect.centery)
            screen.blit(price_surface, price_rect)
            
            # Buy button (disabled if locked or not enough money)
            buy_button_rect = pygame.Rect(item_rect.right - 80, item_rect.top + 17, 70, 36)
            can_afford = self.player and self.player.money >= tool.price and not is_locked
            
            if is_locked:
                button_color = (60, 60, 60)
                border_color = (80, 80, 80)
            elif can_afford:
                button_color = (80, 150, 80)
                border_color = (120, 180, 120)
            else:
                button_color = (100, 60, 60)
                border_color = (140, 100, 100)
            
            pygame.draw.rect(screen, button_color, buy_button_rect, border_radius=5)
            pygame.draw.rect(screen, border_color, buy_button_rect, 2, border_radius=5)
            
            # Button text
            if is_locked:
                buy_text = self.small_font.render("Locked", True, (150, 150, 150))
            else:
                buy_text = self.small_font.render("Buy", True, WHITE)
            buy_text_rect = buy_text.get_rect(center=buy_button_rect.center)
            screen.blit(buy_text, buy_text_rect)
            
            # Store button rect for click detection (only if not locked)
            if not is_locked:
                self.tool_buttons.append((buy_button_rect, tool))
    
    def _draw_sell_tab(self, screen: pygame.Surface):
        """Draw the sell tab content"""
        self.item_buttons = []
        
        # Draw items header
        header_y = self.y + 100
        pygame.draw.line(screen, (139, 90, 43), (self.x + 20, header_y), 
                        (self.x + self.width - 20, header_y), 2)
        
        if not self.inventory:
            no_items_text = self.item_font.render("No inventory available", True, (150, 150, 150))
            text_rect = no_items_text.get_rect(centerx=self.x + self.width // 2, centery=self.y + 200)
            screen.blit(no_items_text, text_rect)
            return
        
        # Get sellable items from inventory
        sellable_items = []
        sell_prices = {
            ItemType.WHEAT: 15,
            ItemType.CARROT: 20,
            ItemType.WOOD: 5,
            ItemType.STONE: 8,
            ItemType.SEED: 5,
            ItemType.CARROT_SEED: 8,
            ItemType.TOMATO: 30,
            ItemType.PUMPKIN: 45,
            ItemType.STRAWBERRY: 60,
            ItemType.GOLDEN_WHEAT: 150,
            ItemType.TOMATO_SEED: 15,
            ItemType.PUMPKIN_SEED: 20,
            ItemType.STRAWBERRY_SEED: 30,
            ItemType.GOLDEN_SEED: 60,
        }
        
        for i, slot in enumerate(self.inventory.slots):
            if isinstance(slot, Item) and slot.item_type in sell_prices:
                sellable_items.append((i, slot, sell_prices[slot.item_type]))
        
        if not sellable_items:
            no_items_text = self.item_font.render("No items to sell", True, (150, 150, 150))
            text_rect = no_items_text.get_rect(centerx=self.x + self.width // 2, centery=self.y + 200)
            screen.blit(no_items_text, text_rect)
            return
        
        # Draw sellable items
        item_y = header_y + 20
        item_height = 50
        item_spacing = 8
        
        for i, (slot_idx, item, price) in enumerate(sellable_items[:6]):  # Show max 6 items
            # Item background
            item_rect = pygame.Rect(self.x + 30, item_y + i * (item_height + item_spacing), 
                                   self.width - 60, item_height)
            pygame.draw.rect(screen, (50, 50, 50), item_rect, border_radius=5)
            pygame.draw.rect(screen, (80, 80, 80), item_rect, 2, border_radius=5)
            
            # Item icon
            icon = item.icon
            icon_rect = icon.get_rect(center=(item_rect.left + 25, item_rect.centery))
            screen.blit(icon, icon_rect)
            
            # Item name and quantity
            name_text = f"{item.item_type.value.replace('_', ' ').title()} x{item.quantity}"
            name_surface = self.item_font.render(name_text, True, WHITE)
            screen.blit(name_surface, (item_rect.left + 55, item_rect.top + 8))
            
            # Price per item
            price_text = f"{price} coins each"
            price_surface = self.small_font.render(price_text, True, YELLOW)
            screen.blit(price_surface, (item_rect.left + 55, item_rect.top + 28))
            
            # Sell button
            sell_button_rect = pygame.Rect(item_rect.right - 80, item_rect.top + 7, 70, 36)
            pygame.draw.rect(screen, (150, 80, 80), sell_button_rect, border_radius=5)
            pygame.draw.rect(screen, (180, 120, 120), sell_button_rect, 2, border_radius=5)
            sell_text = self.small_font.render("Sell", True, WHITE)
            sell_text_rect = sell_text.get_rect(center=sell_button_rect.center)
            screen.blit(sell_text, sell_text_rect)
            
            # Store button rect with sell info
            self.item_buttons.append((sell_button_rect, (slot_idx, item, price)))