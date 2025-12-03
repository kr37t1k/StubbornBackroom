#!/usr/bin/env python3
"""
Advanced Map Generator for Backrooms Game
Generates complex maps with multiple entity types for the 3D backrooms game
"""

import json
import random
import sys
import os
from typing import List, Tuple


class AdvancedMapGenerator:
    """Generates complex maps with multiple entity types for the backrooms game"""
    
    def __init__(self, width: int = 100, height: int = 100, seed: int = None):
        self.width = width
        self.height = height
        self.seed = seed or random.randint(0, 999999)
        self.grid = [[1 for _ in range(width)] for _ in range(height)]  # 1 = wall, 0 = path, 2 = door, 3 = special
        self.entities = []  # List of entities to place in the map
        self.start_pos = (1, 1)
        self.end_pos = (width-2, height-2)
        random.seed(self.seed)
    
    def generate_maze(self):
        """Generate a maze using recursive backtracking algorithm"""
        # Initialize with walls
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = 1  # Wall
        
        # Create maze using recursive backtracking
        stack = []
        visited = [[False for _ in range(self.width)] for _ in range(self.height)]
        
        # Start at (1,1)
        start_x, start_y = 1, 1
        stack.append((start_x, start_y))
        visited[start_y][start_x] = True
        self.grid[start_y][start_x] = 0  # Path
        
        directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]  # Up, Right, Down, Left (skip 1 for walls)
        
        while stack:
            current_x, current_y = stack[-1]
            
            # Find unvisited neighbors
            neighbors = []
            for dx, dy in directions:
                nx, ny = current_x + dx, current_y + dy
                if 0 < nx < self.width-1 and 0 < ny < self.height-1 and not visited[ny][nx]:
                    neighbors.append((nx, ny, current_x + dx//2, current_y + dy//2))  # Also include wall to remove
            
            if neighbors:
                # Choose random neighbor
                nx, ny, wall_x, wall_y = random.choice(neighbors)
                
                # Carve path
                self.grid[ny][nx] = 0
                self.grid[wall_y][wall_x] = 0  # Remove wall between
                visited[ny][nx] = True
                stack.append((nx, ny))
            else:
                # Backtrack
                stack.pop()
        
        # Add some random connections to make it less perfect
        for _ in range(int(self.width * self.height * 0.02)):
            x = random.randint(2, self.width - 3)
            y = random.randint(2, self.height - 3)
            if self.grid[y][x] == 1:  # Wall
                self.grid[y][x] = 0  # Make it a path
        
        # Set start and end
        self.grid[1][1] = 0  # Start
        self.grid[self.height-2][self.width-2] = 0  # End
        self.start_pos = (1, 1)
        self.end_pos = (self.width-2, self.height-2)
    
    def add_doors(self, count: int = 10):
        """Add doors to the map"""
        for _ in range(count):
            # Find a wall to replace with a door
            valid_positions = []
            for y in range(1, self.height-1):
                for x in range(1, self.width-1):
                    if self.grid[y][x] == 1:  # Wall
                        # Check if it's a vertical wall (has paths on both sides horizontally)
                        if (x > 0 and x < self.width-1 and 
                            self.grid[y][x-1] == 0 and self.grid[y][x+1] == 0):
                            valid_positions.append((x, y))
                        # Check if it's a horizontal wall (has paths on both sides vertically)
                        elif (y > 0 and y < self.height-1 and 
                              self.grid[y-1][x] == 0 and self.grid[y+1][x] == 0):
                            valid_positions.append((x, y))
            
            if valid_positions:
                x, y = random.choice(valid_positions)
                self.grid[y][x] = 2  # Door identifier
                # Add door to entities list
                self.entities.append({
                    "type": "door",
                    "x": float(x),
                    "y": 2.0,  # Fixed height for doors
                    "z": float(y),
                    "is_open": False,
                    "locked": random.choice([True, False, False, False])  # 25% chance of being locked
                })
    
    def add_special_rooms(self, count: int = 3):
        """Add special rooms with unique properties"""
        for _ in range(count):
            # Try to find a suitable area for a special room
            room_width = random.randint(4, 8)
            room_height = random.randint(4, 8)
            
            attempts = 0
            max_attempts = 100
            found_position = False
            
            while attempts < max_attempts and not found_position:
                attempts += 1
                x = random.randint(2, self.width - room_width - 2)
                y = random.randint(2, self.height - room_height - 2)
                
                # Check if the area is mostly empty
                is_empty = True
                for ry in range(y, y + room_height):
                    for rx in range(x, x + room_width):
                        if self.grid[ry][rx] != 0:  # Not a path
                            is_empty = False
                            break
                    if not is_empty:
                        break
                
                if is_empty:
                    # Create special room by converting to special tiles
                    for ry in range(y, y + room_height):
                        for rx in range(x, x + room_width):
                            self.grid[ry][rx] = 3  # Special tile
                    found_position = True
    
    def add_decorations(self, count: int = 20):
        """Add decorative elements to the map"""
        for _ in range(count):
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            
            if self.grid[y][x] == 0:  # Only place decorations in paths
                decoration_type = random.choice(["chair", "table", "plant", "light"])
                self.entities.append({
                    "type": decoration_type,
                    "x": float(x),
                    "y": 0.0,
                    "z": float(y)
                })
    
    def generate_open_space(self):
        """Generate an open space map with some random walls"""
        # Start with mostly open space
        for y in range(self.height):
            for x in range(self.width):
                if random.random() < 0.15:  # 15% chance of wall
                    self.grid[y][x] = 1  # Wall
                else:
                    self.grid[y][x] = 0  # Path
        
        # Ensure start and end are clear
        self.grid[1][1] = 0
        self.grid[self.height-2][self.width-2] = 0
        self.start_pos = (1, 1)
        self.end_pos = (self.width-2, self.height-2)
    
    def generate_room_based(self):
        """Generate a map with rooms connected by corridors"""
        # Initialize with walls
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = 1  # Wall
        
        # Create rooms
        room_size_range = (4, 8)
        rooms = []
        
        # Try to place rooms randomly
        attempts = 0
        max_attempts = 200
        min_rooms = max(8, (self.width * self.height) // 150)  # At least 8 or 1 per 150 cells
        
        while len(rooms) < min_rooms and attempts < max_attempts:
            attempts += 1
            
            # Random room size
            room_width = random.randint(*room_size_range)
            room_height = random.randint(*room_size_range)
            
            # Random position
            x = random.randint(1, self.width - room_width - 1)
            y = random.randint(1, self.height - room_height - 1)
            
            # Check if this room overlaps with existing rooms
            overlaps = False
            for rx, ry, rw, rh in rooms:
                # Check for overlap with some padding
                if (x < rx + rw + 1 and x + room_width + 1 > rx and
                    y < ry + rh + 1 and y + room_height + 1 > ry):
                    overlaps = True
                    break
            
            if not overlaps:
                # Add room
                rooms.append((x, y, room_width, room_height))
                
                # Carve out the room
                for ry in range(y, y + room_height):
                    for rx in range(x, x + room_width):
                        self.grid[ry][rx] = 0  # Path
    
        # Connect rooms with corridors
        for i in range(len(rooms) - 1):
            room1 = rooms[i]
            room2 = rooms[i + 1]
            
            # Center of rooms
            x1, y1 = room1[0] + room1[2] // 2, room1[1] + room1[3] // 2
            x2, y2 = room2[0] + room2[2] // 2, room2[1] + room2[3] // 2
            
            # Create L-shaped corridor
            # Horizontal first
            start_x, end_x = min(x1, x2), max(x1, x2)
            for x in range(start_x, end_x + 1):
                self.grid[y1][x] = 0
            
            # Vertical
            start_y, end_y = min(y1, y2), max(y1, y2)
            for y in range(start_y, end_y + 1):
                self.grid[y][x2] = 0
        
        # Ensure start and end are clear
        self.grid[1][1] = 0
        self.grid[self.height-2][self.width-2] = 0
        self.start_pos = (1, 1)
        self.end_pos = (self.width-2, self.height-2)
    
    def save_to_file(self, filepath: str):
        """Save the generated map to a JSON file with entities"""
        data = {
            "width": self.width,
            "height": self.height,
            "seed": self.seed,
            "start_pos": self.start_pos,
            "end_pos": self.end_pos,
            "map": self.grid,
            "entities": self.entities
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def print_map(self):
        """Print a text representation of the map to console"""
        for row in self.grid:
            for cell in row:
                if cell == 0:
                    print(' ', end='')  # Path
                elif cell == 1:
                    print('█', end='')  # Wall
                elif cell == 2:
                    print('D', end='')  # Door
                elif cell == 3:
                    print('S', end='')  # Special room
            print()


def main():
    """Main function to run the advanced map generator"""
    print("Advanced Backrooms Map Generator")
    print("===============================")
    
    # Get user input
    width = int(input(f"Enter map width (default 100): ") or "100")
    height = int(input(f"Enter map height (default 100): ") or "100")
    seed_input = input(f"Enter seed (or press Enter for random): ")
    seed = int(seed_input) if seed_input.strip() else None
    
    print("\nSelect map type:")
    print("1. Maze (default)")
    print("2. Open Space")
    print("3. Room-based")
    
    map_type = input("Enter choice (1-3, default 1): ") or "1"
    
    generator = AdvancedMapGenerator(width, height, seed)
    
    if map_type == "2":
        print("Generating open space map...")
        generator.generate_open_space()
    elif map_type == "3":
        print("Generating room-based map...")
        generator.generate_room_based()
    else:
        print("Generating maze...")
        generator.generate_maze()
    
    # Add advanced features
    print("Adding doors...")
    generator.add_doors(15)
    
    print("Adding special rooms...")
    generator.add_special_rooms(5)
    
    print("Adding decorations...")
    generator.add_decorations(30)
    
    # Show a preview of the map
    print(f"\nGenerated Map Preview (first 20x20):")
    print("-" * 21)
    for y in range(min(20, height)):
        row = ""
        for x in range(min(20, width)):
            if (x, y) == generator.start_pos:
                row += "S"  # Start
            elif (x, y) == generator.end_pos:
                row += "E"  # End
            elif generator.grid[y][x] == 0:
                row += " "  # Path
            elif generator.grid[y][x] == 1:
                row += "█"  # Wall
            elif generator.grid[y][x] == 2:
                row += "D"  # Door
            elif generator.grid[y][x] == 3:
                row += "O"  # Special room
        print(row)
    print("-" * 21)
    
    # Ask for filename
    filename = input(f"\nEnter filename to save (default: advanced_map.json): ") or "advanced_map.json"
    
    generator.save_to_file(filename)
    print(f"Map saved to {filename}")
    
    # Show some stats
    path_count = sum(row.count(0) for row in generator.grid)
    wall_count = sum(row.count(1) for row in generator.grid)
    door_count = sum(row.count(2) for row in generator.grid)
    special_count = sum(row.count(3) for row in generator.grid)
    
    print(f"\nMap Stats:")
    print(f"Dimensions: {width} x {height}")
    print(f"Total cells: {width * height}")
    print(f"Paths: {path_count}")
    print(f"Walls: {wall_count}")
    print(f"Doors: {door_count}")
    print(f"Special rooms: {special_count}")
    print(f"Entities: {len(generator.entities)}")
    print(f"Seed: {generator.seed}")


if __name__ == "__main__":
    main()