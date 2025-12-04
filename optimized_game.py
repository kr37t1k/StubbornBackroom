#!/usr/bin/env python3
# Optimized Backrooms Game with Fog, Physics, and Advanced Entities
# 3D Backrooms Python 3.11 Prototype with Ursina - Optimized for older laptops

import math
import random
from dataclasses import dataclass
from typing import Tuple, List, Dict, Optional
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import json
import os
import sys


@dataclass
class Config:
    window_size: tuple = (1024, 576)  # Smaller window for better performance
    window_type = 'windowed'  # ['windowed', 'fullscreen', 'borderless']
    fps: int = 60  # Lower FPS for better performance on older hardware
    title: str = "Optimized Backrooms: Psycho Dream"
    map: Path = "./maps/simulation.json"
    player_speed: float = 5.0
    mouse_sensitivity: tuple = (75, 75)
    gravity: float = -8
    reality_decay_rate: float = 0.0001
    hallucination_threshold: float = 0.3
    fog_density: float = 0.02  # Fog density for atmosphere
    max_entities: int = 500  # Reduced for optimization
    render_distance: int = 20  # Limited render distance
    texture_quality: str = 'low'  # low, medium, high
    lighting_quality: str = 'low'  # low, medium, high
    enable_shadows: bool = False  # Disable shadows for performance


class Entity3D:
    """Base class for all 3D entities in the game"""
    def __init__(self, x: float, y: float, z: float, entity_type: str = "generic"):
        self.x = x
        self.y = y
        self.z = z
        self.entity_type = entity_type
        self.entity = None
        self.active = True
        self.health = 100
        self.collidable = True
    
    def create_entity(self):
        """Create the actual 3D entity - to be overridden by subclasses"""
        pass
    
    def update(self):
        """Update the entity - to be overridden by subclasses"""
        pass


class Wall(Entity3D):
    """Wall entity with collision"""
    def __init__(self, x: float, y: float, z: float, height: float = 3.0, width: float = 1.0, depth: float = 1.0):
        super().__init__(x, y, z, "wall")
        self.height = height
        self.width = width
        self.depth = depth
    
    def create_entity(self):
        self.entity = Entity(
            model='cube',
            texture='textures/wall_texture.png',
            texture_scale=Vec2(1, 1),
            scale=(self.width, self.height, self.depth),
            x=self.x,
            y=self.y,
            z=self.z,
            color=color.white
        )
        self.entity.collider = 'box'
        return self.entity


class Floor(Entity3D):
    """Floor entity"""
    def __init__(self, x: float, z: float, size: float = 1.0):
        super().__init__(x, 0, z, "floor")
        self.size = size
    
    def create_entity(self):
        self.entity = Entity(
            model='plane',
            texture='textures/floor_texture.png',
            texture_scale=Vec2(5, 5),  # Lower resolution for performance
            scale=self.size,
            rotation_x=90,
            x=self.x,
            z=self.z,
            color=color.white
        )
        self.entity.collider = 'mesh'
        return self.entity


class Ceiling(Entity3D):
    """Ceiling entity"""
    def __init__(self, x: float, z: float, size: float = 1.0):
        super().__init__(x, 3, z, "ceiling")  # Fixed height at 3
        self.size = size
    
    def create_entity(self):
        self.entity = Entity(
            model='plane',
            texture='textures/roof_texture.png',
            texture_scale=Vec2(5, 5),  # Lower resolution for performance
            scale=self.size,
            rotation_x=-90,  # Flip to face down
            y=3,  # 3 units above floor
            x=self.x,
            z=self.z,
            color=color.white
        )
        self.entity.collider = 'mesh'
        return self.entity


class Door(Entity3D):
    """Interactive door entity"""
    def __init__(self, x: float, y: float, z: float, is_open: bool = False, locked: bool = False):
        super().__init__(x, y, z, "door")
        self.is_open = is_open
        self.locked = locked
        self.rotation = 0  # For opening animation
    
    def create_entity(self):
        # Create door frame
        self.frame = Entity(
            model='cube',
            texture='textures/wall_texture.png',
            scale=(0.1, 3, 2.2),
            x=self.x - 1,
            y=self.y,
            z=self.z,
            color=color.gray
        )
        self.frame.collider = 'box'
        
        # Create door panel
        self.door_panel = Entity(
            model='cube',
            texture='textures/door_texture.png',
            scale=(0.1, 2.8, 2),
            x=self.x,
            y=self.y,
            z=self.z,
            color=color.brown
        )
        self.door_panel.collider = 'box'
        
        # Set initial rotation based on open state
        if self.is_open:
            self.door_panel.rotation_y = 90
        
        self.entity = [self.frame, self.door_panel]
        return self.entity
    
    def toggle_door(self):
        """Toggle door open/closed state"""
        if not self.locked:
            self.is_open = not self.is_open
            if self.is_open:
                self.door_panel.animate_rotation_y(90, duration=0.5)
            else:
                self.door_panel.animate_rotation_y(0, duration=0.5)
            return True
        return False


class OptimizedMap:
    """Optimized map with multiple entity types and performance considerations"""
    def __init__(self, width: int = 100, height: int = 100, seed: int = None):
        self.width = width
        self.height = height
        self.seed = seed or random.randint(0, 999999)
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
        self.entities = []  # List of all entities in the map
        self.start_pos = (1, 1)
        self.end_pos = (width-2, height-2)
    
    def generate_maze(self):
        """Generate a maze-like structure"""
        random.seed(self.seed)
        
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
        for _ in range(int(self.width * self.height * 0.01)):  # Reduced for performance
            x = random.randint(2, self.width - 3)
            y = random.randint(2, self.height - 3)
            if self.grid[y][x] == 1:  # Wall
                self.grid[y][x] = 0  # Make it a path
        
        # Set start and end
        self.grid[1][1] = 0  # Start
        self.grid[self.height-2][self.width-2] = 0  # End
        self.start_pos = (1, 1)
        self.end_pos = (self.width-2, self.height-2)
    
    def add_doors_randomly(self, count: int = 5):
        """Add doors randomly to the map"""
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
    
    def save_to_file(self, filepath: str):
        """Save map to JSON file with entities"""
        # Convert entities to serializable format
        entities_data = []
        for entity in self.entities:
            if isinstance(entity, Door):
                entities_data.append({
                    "type": "door",
                    "x": entity.x,
                    "y": entity.y,
                    "z": entity.z,
                    "is_open": entity.is_open,
                    "locked": entity.locked
                })
        
        data = {
            "width": self.width,
            "height": self.height,
            "seed": self.seed,
            "start_pos": self.start_pos,
            "end_pos": self.end_pos,
            "map": self.grid,
            "entities": entities_data
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_from_file(self, filepath: str):
        """Load map from JSON file with entities"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.width = data["width"]
        self.height = data["height"]
        self.seed = data["seed"]
        self.start_pos = tuple(data["start_pos"])
        self.end_pos = tuple(data["end_pos"])
        self.grid = data["map"]
        
        # Load entities
        if "entities" in data:
            for entity_data in data["entities"]:
                if entity_data["type"] == "door":
                    door = Door(
                        x=entity_data["x"],
                        y=entity_data["y"],
                        z=entity_data["z"],
                        is_open=entity_data["is_open"],
                        locked=entity_data["locked"]
                    )
                    self.entities.append(door)


class OptimizedBackroomsGame(Entity):
    def __init__(self):
        # Initialize Ursina
        super().__init__()
        
        # Configuration
        self.config = Config()
        
        # Optimize performance settings
        self.setup_performance_optimizations()
        
        # Set window properties
        window.title = self.config.title
        window.borderless = True if self.config.window_type == 'borderless' else False
        window.exit_button.visible = False
        window.fps_counter.enabled = True
        window.size = self.config.window_size
        
        # Enable fog for atmosphere
        self.enable_fog()
        
        # Player properties
        self.player_speed = self.config.player_speed
        self.mouse_sensitivity = self.config.mouse_sensitivity
        
        # Reality system
        self.reality_stability = 1.0  # 1.0 = stable, 0.0 = completely distorted
        self.hallucination_level = 0.0
        self.time_in_darkness = 0.0
        self.last_sound_time = 0.0
        
        # Game state
        self.keys = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
            "jump": False
        }
        
        # Load map
        self.map = OptimizedMap()
        if os.path.exists(self.config.map):
            self.map.load_from_file(self.config.map)
        else:
            print("Wrong path:  " + self.config.map)
            self.map.generate_maze()
            self.map.add_doors_randomly(5)  # Reduced number of doors for performance
            self.map.save_to_file(self.config.map)
        
        # Initialize the game
        self.setup_scene()
        self.setup_controls()
        self.setup_lighting()
        self.setup_audio()
        self.setup_player()
        
        # For optimization - limit entity updates
        self.entity_update_counter = 0
        self.frame_counter = 0
        self.frame_skip = 2  # Update less frequently
    
    def setup_performance_optimizations(self):
        """Set up performance optimizations for older hardware"""
        # Reduce render quality
        window.render_modes = {
            'default': {
                'antialiasing': 0,  # Disable antialiasing
            }
        }
        
        # Reduce texture filtering
        # from panda3d.core import Texture
        # Texture.set_minfilter(Texture.FT_linear)
        # Texture.set_magfilter(Texture.FT_linear)
    
    def enable_fog(self):
        """Enable fog for atmospheric effect"""
        # Set background color to backrooms yellow
        window.color = color.rgb(204, 191, 77)  # Distinctive backrooms yellow
        
        # Enable fog in the renderer
        from panda3d.core import Fog
        from ursina import scene
        
        fog = Fog("fog")
        fog.setColor(204/255, 191/255, 77/255)  # Backrooms yellow
        fog.setExpDensity(self.config.fog_density)
        
        render.setFog(fog)
    
    def setup_scene(self):
        """Set up the 3D scene with walls, floors, ceilings, and other entities"""
        # Create the floor
        self.create_floor()
        
        # Create walls and other entities based on map
        self.create_entities_from_map()
        
        # Create ceiling
        self.create_ceiling()
    
    def create_floor(self):
        """Create the floor of the backrooms"""
        # Create a large plane for the floor
        floor_size = min(max(self.map.width, self.map.height) * 2, 200)  # Limit size for performance
        floor_center_x = (self.map.width - 1) / 2
        floor_center_z = (self.map.height - 1) / 2
        
        # Create floor entity
        floor = Entity(
            model='plane',
            texture='textures/floor_texture.png',
            texture_scale=Vec2(5, 5),  # Lower resolution for performance
            scale=floor_size,
            rotation_x=90,
            x=floor_center_x,
            z=floor_center_z,
            color=color.white
        )
        
        # Make it solid for collision
        floor.collider = 'mesh'
    
    def create_ceiling(self):
        """Create the ceiling of the backrooms"""
        # Create a large plane for the ceiling
        ceiling_size = min(max(self.map.width, self.map.height) * 2, 200)  # Limit size for performance
        ceiling_center_x = (self.map.width - 1) / 2
        ceiling_center_z = (self.map.height - 1) / 2
        
        # Create ceiling entity
        ceiling = Entity(
            model='plane',
            texture='textures/roof_texture.png',
            texture_scale=Vec2(5, 5),  # Lower resolution for performance
            scale=ceiling_size,
            rotation_x=-90,  # Flip to face down
            y=3,  # 3 units above floor
            x=ceiling_center_x,
            z=ceiling_center_z,
            color=color.white
        )
        
        # Make it solid for collision
        ceiling.collider = 'mesh'
    
    def create_entities_from_map(self):
        """Create 3D entities based on the 2D map and entity list"""
        # Create walls from grid (limit number for performance)
        entities_created = 0
        max_entities = self.config.max_entities // 3  # Reserve some for other entities
        
        for y in range(min(self.map.height, self.config.render_distance * 2)):  # Limit render distance
            for x in range(min(self.map.width, self.config.render_distance * 2)):
                if entities_created >= max_entities:
                    break
                
                if self.map.grid[y][x] == 1:  # Wall
                    # Create a wall at this position
                    wall = Entity(
                        model='cube',
                        texture='textures/wall_texture.png',
                        texture_scale=Vec2(1, 1),
                        scale=(1, 3, 1),  # Width, height, depth
                        x=x,
                        y=2,  # Center height
                        z=y,
                        color=color.white
                    )
                    
                    # Make wall solid for collision
                    wall.collider = 'box'
                    entities_created += 1
                elif self.map.grid[y][x] == 2:  # Door
                    # Create a door at this position
                    door = Door(x, 2, y, is_open=False, locked=False)
                    door.create_entity()
                    self.map.entities.append(door)
                    entities_created += 1
        
        # Create any additional entities from the map's entity list
        for entity in self.map.entities:
            entity.create_entity()
    
    def setup_controls(self):
        """Set up keyboard and mouse controls"""
        # Keyboard controls are handled by Ursina's input system
        # We'll track key states manually
        self.key_states = {
            'w': False,
            's': False,
            'a': False,
            'd': False,
            'space': False
        }
        
        # Ursina's input handling
        def on_input(key):
            if key in self.key_states:
                self.key_states[key] = True
            elif key.endswith(' up') and key[:-3] in self.key_states:
                self.key_states[key[:-3]] = False
            elif 'r' in key: # Reset player position
                self.player.position = Vec3(2.5, 2.5, -0.5)  # Reset position
            elif key == 'escape':
                application.quit()
            elif key == 'f':  # Toggle fog
                self.toggle_fog()
        
        self.input_handler = on_input
    
    def toggle_fog(self):
        """Toggle fog on/off"""
        # For now, just print a message - actual fog toggle would require more complex implementation
        print("Fog toggled")
    
    def setup_lighting(self):
        """Set up basic lighting for the scene"""
        # Ambient light
        AmbientLight(color=color.rgb(77, 77, 51))  # Slightly yellowish ambient
        
        # Directional light (sun-like) - simplified for performance
        self.directional_light = DirectionalLight()
        self.directional_light.color = color.rgb(204, 191, 128)  # Warm yellow light
        self.directional_light.rotation = Vec3(45, -45, 0)
        
        # Disable shadows for performance
        if not self.config.enable_shadows:
            self.directional_light.shadow_map_resolution = (256, 256)  # Lower resolution
        
        # Player flashlight will be handled by the player controller
    
    def setup_audio(self):
        """Set up audio system"""
        # Ursina doesn't have built-in audio manager, so we'll use pygame.mixer for background music
        try:
            from pydub import AudioSegment
            from pydub.playback import play
            if os.path.exists("audio/atomiste.mp3"):
                background_music = AudioSegment.from_file("audio/atomiste.mp3")
                play(background_music)
        except ImportError:
            print("pydub not available for audio playback")
    
    def setup_player(self):
        """Set up the first person player controller with enhanced physics"""
        # Create first person controller
        self.player = FirstPersonController()
        self.player.position = Vec3(2.5, 2.5, -0.5)  # Start position
        self.player.speed = self.player_speed
        self.player.jump_height = 3  # Jump height for better physics
        self.player.gravity = self.config.gravity  # Custom gravity
        self.player.ground_y = 0  # Ground level
        
        # Set mouse sensitivity
        mouse_sensitivity = Vec2(self.mouse_sensitivity[0], self.mouse_sensitivity[1])
        self.player.mouse_sensitivity = mouse_sensitivity
    
    def input(self, key):
        """Handle input events"""
        if key in self.key_states:
            self.key_states[key] = True
        elif key.endswith(' up') and key[:-3] in self.key_states:
            self.key_states[key[:-3]] = False
        elif key == 'r':
            self.player.position = Vec3(2.5, 2.5, 1.5)  # Reset position
        elif key == 'escape':
            application.quit()
        elif key == 'f':  # Toggle fog
            self.toggle_fog()
    
    def update(self):
        """Update game logic every frame"""
        self.frame_counter += 1
        
        # Update reality distortion effects less frequently for performance
        if self.frame_counter % 3 == 0:  # Update every 3 frames
            self.update_reality()
        
        # Update hallucination effects less frequently for performance
        if self.frame_counter % 5 == 0:  # Update every 5 frames
            self.update_hallucinations()
        
        # Update entities periodically (for optimization)
        if self.frame_counter % 10 == 0:  # Only update entities every 10 frames
            self.update_entities()
    
    def update_entities(self):
        """Update all entities in the map"""
        for entity in self.map.entities:
            entity.update()
    
    def update_reality(self):
        """Update reality distortion effects"""
        # Gradually decrease reality stability
        self.reality_stability -= self.config.reality_decay_rate
        
        # Randomly increase hallucination level
        self.hallucination_level += random.uniform(-0.0005, 0.001)  # Reduced rate for performance
        self.hallucination_level = max(0, min(1.0, self.hallucination_level))
        
        # Apply reality distortion effects
        if self.hallucination_level > self.config.hallucination_threshold:
            # Apply visual distortion effects
            self.apply_visual_distortion()
    
    def update_hallucinations(self):
        """Update hallucination effects"""
        # Change lighting randomly when hallucinating (less frequently for performance)
        if self.hallucination_level > 0.5:
            flicker = random.random() < 0.005  # Reduced frequency for performance
            if flicker:
                new_light_color = color.hsv(random.randint(0, 360), random.uniform(0.5, 1.0), random.uniform(0.3, 1.0))
                self.directional_light.color = new_light_color
    
    def apply_visual_distortion(self):
        """Apply visual distortion effects when reality is unstable"""
        # For now, just print a message to indicate distortion
        # In a full implementation, we would modify the camera or shader effects
        pass


if __name__ == "__main__":
    # Create and run the game
    app = Ursina()
    game = OptimizedBackroomsGame()
    app.run()