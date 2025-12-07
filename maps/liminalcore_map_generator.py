#!/usr/bin/env python3
"""
Advanced Map Generator for Liminalcore Backrooms Game
Generates complex maps with extensive customization options
"""

import json
import random
import sys
import os
from typing import List, Tuple, Dict, Any
from enum import Enum


class RoomType(Enum):
    HALLWAY = "hallway"
    CORNER = "corner"
    JUNCTION = "junction"
    ROOM = "room"
    TRANSITION = "transition"
    LIMINAL = "liminal"
    CHAOTIC = "chaotic"
    DISTORTED = "distorted"


class MapStyle(Enum):
    MAZE = "maze"
    OPEN_SPACE = "open_space"
    ROOM_BASED = "room_based"
    LIMINAL = "liminal"
    CHAOTIC = "chaotic"


class LiminalMapGenerator:
    """Advanced map generator with extensive customization options"""
    
    def __init__(self, width: int = 100, height: int = 100, seed: int = None):
        self.width = width
        self.height = height
        self.seed = seed or random.randint(0, 999999)
        random.seed(self.seed)
        
        # Map grid: 0=path, 1=wall, 2=door, 3=special, 4=liminal
        self.grid = [[1 for _ in range(width)] for _ in range(height)]
        self.entities = []  # List of entities to place
        self.start_pos = (1, 1)
        self.end_pos = (width-2, height-2)
        
        # Configuration options
        self.config = {
            'room_types': {
                RoomType.HALLWAY: 0.2,
                RoomType.CORNER: 0.15,
                RoomType.JUNCTION: 0.25,
                RoomType.ROOM: 0.2,
                RoomType.TRANSITION: 0.1,
                RoomType.LIMINAL: 0.05,
                RoomType.CHAOTIC: 0.03,
                RoomType.DISTORTED: 0.02
            },
            'entity_density': 0.05,  # Entities per tile
            'door_frequency': 0.1,   # Chance of door per connection
            'special_room_frequency': 0.05,
            'decoration_frequency': 0.3,
            'corridor_width': 1,
            'room_size_range': (3, 8),
            'connection_style': 'standard',  # standard, maze, organic
            'theme': 'yellow',  # yellow, gray, industrial, liminal
            'complexity': 0.5,  # 0.0 to 1.0
            'symmetry': 0.0,    # 0.0 to 1.0
            'loop_probability': 0.3  # Chance of adding loops to maze
        }
    
    def set_config(self, config: Dict[str, Any]):
        """Update generator configuration"""
        self.config.update(config)
    
    def generate_map(self, style: MapStyle = MapStyle.MAZE):
        """Generate a map based on the selected style"""
        # Initialize with walls
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = 1  # Wall
        
        if style == MapStyle.MAZE:
            self._generate_maze()
        elif style == MapStyle.OPEN_SPACE:
            self._generate_open_space()
        elif style == MapStyle.ROOM_BASED:
            self._generate_room_based()
        elif style == MapStyle.LIMINAL:
            self._generate_liminal()
        elif style == MapStyle.CHAOTIC:
            self._generate_chaotic()
        
        # Add finishing touches
        self._add_start_end()
        self._add_doors()
        self._add_special_rooms()
        self._add_decorations()
        self._add_entities()
    
    def _generate_maze(self):
        """Generate a maze using recursive backtracking"""
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
        
        # Add loops based on complexity setting
        if self.config['loop_probability'] > 0:
            self._add_maze_loops()
    
    def _add_maze_loops(self):
        """Add loops to the maze to make it less perfect"""
        complexity = self.config['complexity']
        loop_count = int((self.width * self.height * 0.02) * complexity)
        
        for _ in range(loop_count):
            x = random.randint(2, self.width - 3)
            y = random.randint(2, self.height - 3)
            if self.grid[y][x] == 1:  # Wall
                self.grid[y][x] = 0  # Make it a path
    
    def _generate_open_space(self):
        """Generate an open space map with some random walls"""
        density = 0.15 * (1.0 - self.config['complexity'])  # Lower density for higher complexity
        
        for y in range(1, self.height-1):
            for x in range(1, self.width-1):
                if random.random() < density:
                    self.grid[y][x] = 1  # Wall
                else:
                    self.grid[y][x] = 0  # Path
    
    def _generate_room_based(self):
        """Generate a map with rooms connected by corridors"""
        # Create rooms
        room_size_range = self.config['room_size_range']
        rooms = []
        
        # Try to place rooms randomly
        attempts = 0
        max_attempts = 200
        min_rooms = max(8, int((self.width * self.height) * 0.01 * (1.0 + self.config['complexity'])))
        
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
                if (x < rx + rw + 2 and x + room_width + 2 > rx and
                    y < ry + rh + 2 and y + room_height + 2 > ry):
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
                if 0 <= x < self.width and 0 <= y1 < self.height:
                    self.grid[y1][x] = 0
            
            # Vertical
            start_y, end_y = min(y1, y2), max(y1, y2)
            for y in range(start_y, end_y + 1):
                if 0 <= x2 < self.width and 0 <= y < self.height:
                    self.grid[y][x2] = 0
    
    def _generate_liminal(self):
        """Generate a liminal-themed map with unusual structures"""
        # Start with mostly open space
        for y in range(1, self.height-1):
            for x in range(1, self.width-1):
                if random.random() < 0.1:  # 10% chance of wall
                    self.grid[y][x] = 1  # Wall
                else:
                    self.grid[y][x] = 0  # Path
        
        # Add some large empty spaces
        for _ in range(int(self.width * self.height * 0.005)):
            # Create a large empty area
            cx = random.randint(5, self.width - 6)
            cy = random.randint(5, self.height - 6)
            size = random.randint(3, 6)
            
            for dy in range(-size//2, size//2 + 1):
                for dx in range(-size//2, size//2 + 1):
                    nx, ny = cx + dx, cy + dy
                    if 0 < nx < self.width-1 and 0 < ny < self.height-1:
                        self.grid[ny][nx] = 0  # Path
    
    def _generate_chaotic(self):
        """Generate a chaotic, unstable map"""
        # Very random pattern
        for y in range(1, self.height-1):
            for x in range(1, self.width-1):
                if random.random() < 0.45:  # Almost 50/50
                    self.grid[y][x] = 1  # Wall
                else:
                    self.grid[y][x] = 0  # Path
        
        # Add some special areas
        for _ in range(int(self.width * self.height * 0.01)):
            x = random.randint(2, self.width - 3)
            y = random.randint(2, self.height - 3)
            self.grid[y][x] = 4  # Special liminal tile
    
    def _add_start_end(self):
        """Add start and end positions"""
        self.grid[1][1] = 0  # Start
        self.grid[self.height-2][self.width-2] = 0  # End
        self.start_pos = (1, 1)
        self.end_pos = (self.width-2, self.width-2)
    
    def _add_doors(self):
        """Add doors to the map"""
        door_count = int((self.width * self.height) * self.config['door_frequency'])
        
        for _ in range(door_count):
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
    
    def _add_special_rooms(self):
        """Add special rooms with unique properties"""
        special_count = int((self.width * self.height) * self.config['special_room_frequency'])
        
        for _ in range(special_count):
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
                            if 0 <= ry < self.height and 0 <= rx < self.width:
                                self.grid[ry][rx] = 3  # Special tile
                    found_position = True
    
    def _add_decorations(self):
        """Add decorative elements to the map"""
        decoration_count = int((self.width * self.height) * self.config['decoration_frequency'])
        
        for _ in range(decoration_count):
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
    
    def _add_entities(self):
        """Add various entities to the map"""
        entity_count = int((self.width * self.height) * self.config['entity_density'])
        
        for _ in range(entity_count):
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            
            if self.grid[y][x] == 0:  # Only place entities in paths
                entity_type = random.choice([
                    "chair", "table", "plant", "light", "strange_object", 
                    "monitor", "desk", "bookshelf", "painting"
                ])
                
                entity = {
                    "type": entity_type,
                    "x": float(x),
                    "y": 0.0 if entity_type != "light" else 2.0,
                    "z": float(y)
                }
                
                # Add special properties for certain entities
                if entity_type == "strange_object":
                    entity["properties"] = {
                        "glow": random.choice([True, False]),
                        "sound": random.choice([True, False]),
                        "movement": random.choice(["static", "slow", "random"])
                    }
                elif entity_type == "monitor":
                    entity["properties"] = {
                        "flicker": random.choice([True, False]),
                        "content": random.choice(["static", "text", "image", "void"])
                    }
                
                self.entities.append(entity)
    
    def save_to_file(self, filepath: str):
        """Save the generated map to a JSON file"""
        data = {
            "width": self.width,
            "height": self.height,
            "seed": self.seed,
            "start_pos": [self.start_pos[0], self.start_pos[1]],
            "end_pos": [self.end_pos[0], self.end_pos[1]],
            "map": self.grid,
            "entities": self.entities,
            "config": self.config,
            "generation_style": self.config.get('style', 'custom')
        }
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def print_map(self, max_size=20):
        """Print a text representation of the map to console"""
        print(f"Map ({self.width}x{self.height}):")
        print("-" * min(self.width + 1, max_size + 1))
        
        for y in range(min(self.height, max_size)):
            row = ""
            for x in range(min(self.width, max_size)):
                if (x, y) == self.start_pos:
                    row += "S"  # Start
                elif (x, y) == self.end_pos:
                    row += "E"  # End
                elif self.grid[y][x] == 0:
                    row += " "  # Path
                elif self.grid[y][x] == 1:
                    row += "█"  # Wall
                elif self.grid[y][x] == 2:
                    row += "D"  # Door
                elif self.grid[y][x] == 3:
                    row += "O"  # Special room
                elif self.grid[y][x] == 4:
                    row += "L"  # Liminal space
                else:
                    row += "?"  # Unknown
            print(row)
        print("-" * min(self.width + 1, max_size + 1))


def main():
    """Main function to run the advanced map generator"""
    print("Liminalcore Advanced Map Generator")
    print("==================================")
    
    # Get user input
    width = int(input(f"Enter map width (default 100): ") or "100")
    height = int(input(f"Enter map height (default 100): ") or "100")
    seed_input = input(f"Enter seed (or press Enter for random): ")
    seed = int(seed_input) if seed_input.strip() else None
    
    print("\nSelect map style:")
    print("1. Maze (default)")
    print("2. Open Space")
    print("3. Room-based")
    print("4. Liminal")
    print("5. Chaotic")
    
    style_choice = input("Enter choice (1-5, default 1): ") or "1"
    
    styles = {
        "1": MapStyle.MAZE,
        "2": MapStyle.OPEN_SPACE, 
        "3": MapStyle.ROOM_BASED,
        "4": MapStyle.LIMINAL,
        "5": MapStyle.CHAOTIC
    }
    style = styles.get(style_choice, MapStyle.MAZE)
    
    # Create generator
    generator = LiminalMapGenerator(width, height, seed)
    
    # Get advanced options
    print("\nAdvanced Options:")
    complexity = float(input(f"Enter complexity (0.0-1.0, default 0.5): ") or "0.5")
    door_freq = float(input(f"Enter door frequency (0.0-1.0, default 0.1): ") or "0.1")
    decoration_freq = float(input(f"Enter decoration frequency (0.0-1.0, default 0.3): ") or "0.3")
    
    # Update configuration
    generator.set_config({
        'complexity': max(0.0, min(1.0, complexity)),
        'door_frequency': max(0.0, min(1.0, door_freq)),
        'decoration_frequency': max(0.0, min(1.0, decoration_freq)),
        'style': style.value
    })
    
    print(f"\nGenerating {style.value} map...")
    generator.generate_map(style)
    
    # Show a preview of the map
    print(f"\nGenerated Map Preview (first 20x20):")
    generator.print_map(20)
    
    # Ask for filename
    filename = input(f"\nEnter filename to save (default: liminal_map.json): ") or "liminal_map.json"
    filepath = f"maps/{filename}" if not filename.startswith("maps/") else filename
    
    generator.save_to_file(filepath)
    print(f"Map saved to {filepath}")
    
    # Show some stats
    path_count = sum(row.count(0) for row in generator.grid)
    wall_count = sum(row.count(1) for row in generator.grid)
    door_count = sum(row.count(2) for row in generator.grid)
    special_count = sum(row.count(3) for row in generator.grid)
    liminal_count = sum(row.count(4) for row in generator.grid)
    
    print(f"\nMap Stats:")
    print(f"Dimensions: {width} x {height}")
    print(f"Total cells: {width * height}")
    print(f"Paths: {path_count}")
    print(f"Walls: {wall_count}")
    print(f"Doors: {door_count}")
    print(f"Special rooms: {special_count}")
    print(f"Liminal spaces: {liminal_count}")
    print(f"Entities: {len(generator.entities)}")
    print(f"Seed: {generator.seed}")
    print(f"Complexity: {generator.config['complexity']}")


if __name__ == "__main__":
    main()