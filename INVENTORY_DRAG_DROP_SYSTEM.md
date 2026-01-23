# Inventory Drag-and-Drop System

## Overview
The inventory now supports a full drag-and-drop system for moving items between inventory slots and dropping them into the world.

## Features

### 1. **Click to Drag**
- **First Click**: Click on any item in the inventory (when TAB opens it) to start dragging it
- The dragged item appears highlighted at the mouse cursor with a yellow/gold background
- The original slot darkens to show where you're dragging from

### 2. **Drop in Empty Slot**
- **Second Click in Inventory**: Click on an empty slot to move the dragged item there
- The item transfers from the source slot to the destination slot
- Empty slots display with a `.` placeholder character

### 3. **Swap Items**
- **Drop on Occupied Slot**: Click on a slot that already has an item
- The two items swap positions instantly
- This allows you to reorganize your inventory freely

### 4. **Drop in World**
- **Click Outside Inventory**: While dragging an item, click anywhere in the dungeon view
- The item is dropped in the world in the direction you clicked
- The system tries to place items up to 3 tiles away in the clicked direction
- Dropped items become pickable ground items with their weapon glyph displayed
- Successfully dropped items are removed from inventory

### 5. **Abort Drag**
- **Close Inventory (TAB)**: If you're dragging an item and press TAB, the item is automatically dropped in front of the player
- This prevents losing items if you accidentally close the inventory mid-drag

## Visual Feedback

### Inventory Display
- **Hotbar (Row 0)**: 8 weapon/item slots with 1-8 numbers, selected items highlighted in gold
- **Inventory (Rows 1-3)**: 24 additional slots for storage
- **Dragged From Slot**: Shows with a darker background (60, 60, 40) while dragging
- **Dragged Item**: Follows your mouse cursor with bright yellow highlight (255, 255, 100) on dark background
- **Empty Slots**: Display with a `.` character to show walkable/usable space

### Tooltip Display
- When hovering over an item (not dragging), the item name appears at the top center of the screen
- Tooltip disappears when you move away or start dragging

## Implementation Details

### State Variables
```python
self.dragged_item       # Dictionary copy of the item being dragged
self.dragged_from_slot  # (row, col) tuple of where the drag started
```

### Key Methods
- **`drop_item_in_direction(item, direction_row, direction_col)`**
  - Finds a valid floor tile up to 3 tiles away in the given direction
  - Checks for walkability, monster occupation, and existing ground items
  - Returns `True` if successfully dropped, `False` otherwise

### Event Handling
The system handles three main mouse interactions:

1. **MOUSEMOTION**: Updates hovered item tooltip (only in inventory area when open)
2. **MOUSEBUTTONDOWN (Left Click)**:
   - **In inventory**: Either start drag or complete drag/swap
   - **Outside inventory while dragging**: Drop item in that world direction
   - **Outside inventory normally**: Normal world interaction (swing weapon)

## Usage Instructions

### To Move Items
1. Press **TAB** to open inventory
2. **Left Click** an item to pick it up
3. **Left Click** an empty slot to place it there
4. **Left Click** another item to swap them

### To Drop Items in World
1. With inventory open, **Left Click** an item to start dragging
2. **Left Click** somewhere in the dungeon view (outside inventory area)
3. Item appears on the ground in that direction

### To Reorganize While Dropping
1. Open inventory (**TAB**)
2. Click an item to drag it
3. Click in the dungeon to drop it
4. Items are placed intelligently up to 3 tiles away in the clicked direction

## Edge Cases Handled

- **Inventory Full**: Dropped items still appear in world if inventory is full
- **Occupied Tiles**: Won't drop on monsters, exits, or existing ground items
- **Wall Collision**: Won't drop in walls; finds nearest valid walkable tile
- **Out of Range**: If no valid tile exists within 3 tiles, drop fails silently
- **Mid-Drag Close**: Closing inventory during drag automatically drops item in front

## Balance Notes

- Items can be freely reorganized without item loss
- Dragging between inventory and world is quick and intuitive
- The direction-based dropping mechanic encourages spatial awareness
- Multiple items can exist on the same tile (via ground_items dict)

## Future Enhancements

Potential features for later:
- Right-click to drop items without opening inventory
- Drag multiple items at once
- Item sorting/organization buttons
- Quick-drop hotkey while inventory is open
- Drag-to-drop-on-self for using items
