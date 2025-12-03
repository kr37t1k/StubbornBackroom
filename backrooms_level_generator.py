import numpy as np
from PIL import Image
import random
import os
from typing import List, Tuple, Dict, Any
import json

class BackroomsLevelGenerator:
    """
    Standalone backrooms level generator that creates procedurally generated levels
    with rooms, corridors, and backrooms-specific features.
    """
    
    def __init__(self, width: int = 100, height: int = 100, seed: int = None):
        self.width = width
        self.height = height
        self.seed = seed or random.randint(0, 1000000)
        random.seed(self.seed)
        np.random.seed(self.seed)
        
        # Tile types
        self.EMPTY = 0
        self.WALL = 1
        self.FLOOR = 2
        self.DOOR = 3
        self.CORRIDOR = 4
        self.ROOM = 5
        self.HAZARD = 6
        
        # Level data
        self.level_map = np.zeros((self.height, self.width), dtype=int)
        self.rooms = []
        self.doors = []
        self.corridors = []
        self.hazards = []
        
    def generate_level(self) -> Dict[str, Any]:
        """Generate a complete backrooms level with rooms, corridors, and hazards."""
        self._generate_base_structure()
        self._add_rooms()
        self._add_corridors()
        self._add_doors()
        self._add_hazards()
        self._add_decorations()
        
        return self._export_level_data()
    
    def _generate_base_structure(self):
        """Generate the base structure of the level."""
        # Start with empty space
        self.level_map.fill(self.EMPTY)
        
        # Add some noise to create a more organic feel
        noise = np.random.random((self.height, self.width))
        self.level_map[noise > 0.7] = self.WALL
    
    def _add_rooms(self, min_rooms: int = 5, max_rooms: int = 15):
        """Add rooms to the level."""
        num_rooms = random.randint(min_rooms, max_rooms)
        
        for _ in range(num_rooms):
            # Generate room dimensions
            room_width = random.randint(5, 15)
            room_height = random.randint(5, 15)
            
            # Find a valid position for the room
            valid_position = False
            attempts = 0
            while not valid_position and attempts < 50:
                x = random.randint(1, self.width - room_width - 1)
                y = random.randint(1, self.height - room_height - 1)
                
                # Check if the room overlaps with existing rooms
                overlap = False
                for existing_room in self.rooms:
                    ex, ey, ew, eh = existing_room
                    if (x < ex + ew and x + room_width > ex and 
                        y < ey + eh and y + room_height > ey):
                        overlap = True
                        break
                
                if not overlap:
                    valid_position = True
                    # Add the room
                    self.rooms.append((x, y, room_width, room_height))
                    
                    # Fill the room with floor
                    self.level_map[y:y+room_height, x:x+room_width] = self.ROOM
                    
                    # Add walls around the room
                    for i in range(y-1, y+room_height+1):
                        for j in range(x-1, x+room_width+1):
                            if i < 0 or i >= self.height or j < 0 or j >= self.width:
                                continue
                            if (i == y-1 or i == y+room_height or 
                                j == x-1 or j == x+room_width):
                                if self.level_map[i, j] == self.EMPTY:
                                    self.level_map[i, j] = self.WALL
                attempts += 1
    
    def _add_corridors(self):
        """Connect rooms with corridors."""
        if len(self.rooms) < 2:
            return
        
        # Connect each room to the next one
        for i in range(len(self.rooms) - 1):
            room1 = self.rooms[i]
            room2 = self.rooms[i + 1]
            
            # Center points of rooms
            center1_x = room1[0] + room1[2] // 2
            center1_y = room1[1] + room1[3] // 2
            center2_x = room2[0] + room2[2] // 2
            center2_y = room2[1] + room2[3] // 2
            
            # Create L-shaped corridor
            if random.choice([True, False]):
                # Horizontal then vertical
                self._create_corridor(center1_x, center1_y, center2_x, center1_y)
                self._create_corridor(center2_x, center1_y, center2_x, center2_y)
            else:
                # Vertical then horizontal
                self._create_corridor(center1_x, center1_y, center1_x, center2_y)
                self._create_corridor(center1_x, center2_y, center2_x, center2_y)
    
    def _create_corridor(self, x1: int, y1: int, x2: int, y2: int):
        """Create a corridor between two points."""
        # Horizontal segment
        if x1 != x2:
            start_x, end_x = min(x1, x2), max(x1, x2)
            for x in range(start_x, end_x + 1):
                if 0 <= x < self.width and 0 <= y1 < self.height:
                    if self.level_map[y1, x] in [self.EMPTY, self.WALL]:
                        self.level_map[y1, x] = self.CORRIDOR
        
        # Vertical segment
        if y1 != y2:
            start_y, end_y = min(y1, y2), max(y1, y2)
            for y in range(start_y, end_y + 1):
                if 0 <= x2 < self.width and 0 <= y < self.height:
                    if self.level_map[y, x2] in [self.EMPTY, self.WALL]:
                        self.level_map[y, x2] = self.CORRIDOR
    
    def _add_doors(self):
        """Add doors connecting rooms and corridors."""
        for room in self.rooms:
            x, y, w, h = room
            # Add doors on each wall of the room
            door_positions = [
                (x + w // 2, y - 1),  # Top
                (x + w // 2, y + h),  # Bottom
                (x - 1, y + h // 2),  # Left
                (x + w, y + h // 2)   # Right
            ]
            
            for door_x, door_y in door_positions:
                if (0 <= door_x < self.width and 0 <= door_y < self.height and 
                    self.level_map[door_y, door_x] == self.WALL):
                    # Check if adjacent to corridor or another room
                    adjacent_to_corridor = False
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = door_x + dx, door_y + dy
                        if (0 <= nx < self.width and 0 <= ny < self.height and 
                            self.level_map[ny, nx] in [self.CORRIDOR, self.ROOM]):
                            adjacent_to_corridor = True
                            break
                    
                    if adjacent_to_corridor:
                        self.level_map[door_y, door_x] = self.DOOR
                        self.doors.append((door_x, door_y))
    
    def _add_hazards(self):
        """Add hazardous areas to the level."""
        num_hazards = random.randint(2, 6)
        
        for _ in range(num_hazards):
            hazard_x = random.randint(5, self.width - 5)
            hazard_y = random.randint(5, self.height - 5)
            hazard_size = random.randint(2, 4)
            
            # Place hazard in a floor area
            for i in range(hazard_y - hazard_size//2, hazard_y + hazard_size//2 + 1):
                for j in range(hazard_x - hazard_size//2, hazard_x + hazard_size//2 + 1):
                    if (0 <= i < self.height and 0 <= j < self.width and 
                        self.level_map[i, j] in [self.FLOOR, self.ROOM, self.CORRIDOR]):
                        self.level_map[i, j] = self.HAZARD
                        self.hazards.append((j, i))
    
    def _add_decorations(self):
        """Add decorative elements to the level."""
        # Convert remaining empty spaces to floors
        self.level_map[self.level_map == self.EMPTY] = self.FLOOR
    
    def _export_level_data(self) -> Dict[str, Any]:
        """Export the level data to a dictionary format."""
        return {
            'width': self.width,
            'height': self.height,
            'seed': self.seed,
            'map': self.level_map.tolist(),
            'rooms': self.rooms,
            'doors': self.doors,
            'corridors': self.corridors,
            'hazards': self.hazards,
            'metadata': {
                'generated_by': 'BackroomsLevelGenerator',
                'tile_types': {
                    'empty': self.EMPTY,
                    'wall': self.WALL,
                    'floor': self.FLOOR,
                    'door': self.DOOR,
                    'corridor': self.CORRIDOR,
                    'room': self.ROOM,
                    'hazard': self.HAZARD
                }
            }
        }
    
    def save_level_to_file(self, filename: str):
        """Save the generated level to a JSON file."""
        level_data = self.generate_level()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(level_data, f, indent=2)
        
        print(f"Level saved to {filename}")
    
    def visualize_level(self, filename: str = None) -> Image.Image:
        """Visualize the level as an image."""
        # Create a color map for different tile types
        color_map = {
            self.EMPTY: (0, 0, 0),      # Black
            self.WALL: (100, 100, 100), # Gray
            self.FLOOR: (200, 200, 200), # Light gray
            self.DOOR: (255, 165, 0),   # Orange
            self.CORRIDOR: (180, 180, 180), # Lighter gray
            self.ROOM: (220, 220, 220), # Lighter gray
            self.HAZARD: (255, 0, 0)    # Red
        }
        
        # Create image
        img = Image.new('RGB', (self.width, self.height))
        pixels = img.load()
        
        for y in range(self.height):
            for x in range(self.width):
                tile_type = self.level_map[y, x]
                pixels[x, y] = color_map.get(tile_type, (0, 0, 0))
        
        if filename:
            img.save(filename)
        
        return img

if __name__ == "__main__":
    # Example usage
    generator = BackroomsLevelGenerator(width=100, height=100, seed=42)
    level_data = generator.generate_level()
    generator.visualize_level("backrooms_level.png")
    generator.save_level_to_file("levels/generated_level.json")
    print("Level generation complete!")