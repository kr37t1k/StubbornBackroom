#!/usr/bin/env python3
# main game script - StubbornBackroom: Psycho Dream
# 3D Backrooms Python 3.11 Prototype with Ursina

import math
import random
import time
from dataclasses import dataclass
from typing import Tuple, List, Dict, Optional

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import json
import os
import sys


@dataclass
class Config:
    window_size: tuple = (1280, 720)
    window_type = 'windowed'  # ['windowed', 'fullscreen', 'borderless']
    fps: int = 70
    title: str = "StubbornBackroom: Psycho Dream"
    map: Path = "./maps/backrooms_style.json"
    player_speed: float = 5.0
    mouse_sensitivity: tuple = (75, 75)
    gravity: float = -8
    reality_decay_rate: float = 0.0001
    hallucination_threshold: float = 0.3


class Map:
    """Represents a 2D map for the backrooms game"""
    def __init__(self, width: int = 100, height: int = 100, seed: int = None):
        self.width = width
        self.height = height
        self.seed = seed or random.randint(0, 999999)
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
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
    
    def save_to_file(self, filepath: str):
        """Save map to JSON file"""
        data = {
            "width": self.width,
            "height": self.height,
            "seed": self.seed,
            "start_pos": self.start_pos,
            "end_pos": self.end_pos,
            "map": self.grid
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_from_file(self, filepath: str):
        """Load map from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.width = data["width"]
        self.height = data["height"]
        self.seed = data["seed"]
        self.start_pos = tuple(data["start_pos"])
        self.end_pos = tuple(data["end_pos"])
        self.grid = data["map"]

class BackroomsGame(Entity):
    def __init__(self):
        # Initialize Ursina
        super().__init__()
        
        # Configuration
        self.config = Config()
        
        # Set window properties
        window.title = self.config.title
        window.borderless = True if self.config.window_type == 'borderless' else False
        window.exit_button.visible = False
        window.fps_counter.enabled = True
        window.size = self.config.window_size
        
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
        self.map = Map()
        if os.path.exists(self.config.map):
            self.map.load_from_file(self.config.map)
        else:
            print("Wrong path:  " + self.config.map)
            # self.map.generate_maze()
            # self.map.save_to_file(self.config.map)
        
        # Initialize the game
        self.setup_scene()
        self.setup_controls()
        self.setup_lighting()
        self.setup_audio()
        self.setup_player()
        
    def setup_scene(self):
        """Set up the 3D scene with walls and floors based on the map"""
        # Set background color to backrooms yellow
        window.color = color.rgb(204, 191, 77)  # Distinctive backrooms yellow
        
        # Create the floor
        self.create_floor()
        
        # Create walls based on map
        self.create_walls_from_map()
        
        # Create ceiling
        self.create_ceiling()
    
    def create_floor(self):
        """Create the floor of the backrooms"""
        # Create a large plane for the floor
        floor_size = max(self.map.width, self.map.height) * 2
        floor_center_x = (self.map.width - 1) / 2
        floor_center_z = (self.map.height - 1) / 2
        
        # Create floor entity
        floor = Entity(
            model='plane',
            texture='textures/floor_texture.png',
            texture_scale=Vec2(10, 10),
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
        ceiling_size = max(self.map.width, self.map.height) * 2
        ceiling_center_x = (self.map.width - 1) / 2
        ceiling_center_z = (self.map.height - 1) / 2
        
        # Create ceiling entity
        ceiling = Entity(
            model='plane',
            texture='textures/roof_texture.png',
            texture_scale=Vec2(10, 10),
            scale=ceiling_size,
            rotation_x=-90,  # Flip to face down
            y=3,  # 3 units above floor
            x=ceiling_center_x,
            z=ceiling_center_z,
            color=color.white
        )
        
        # Make it solid for collision
        ceiling.collider = 'mesh'
    
    def create_walls_from_map(self):
        """Create 3D walls based on the 2D map"""
        for y in range(self.map.height):
            for x in range(self.map.width):
                if self.map.grid[y][x] == 1:  # Wall
                    # Create a wall at this position
                    wall = Entity(
                        model='cube',
                        texture='textures/wall_texture.png',
                        texture_scale=Vec2(2, 2),
                        scale=(1, 3, 1),  # Width, height, depth
                        x=x,
                        y=1.5,  # Center height (half of 3)
                        z=y,
                        color=color.white
                    )
                    
                    # Make wall solid for collision
                    wall.collider = 'box'
    
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
            elif 'r' in key: #fix plz
                self.player.position = Vec3(self.map.start_pos[0] + 0.5, 1.5, self.map.start_pos[1] + 0.5)  # Reset position
            elif key == 'escape':
                application.quit()
        
        self.input_handler = on_input
    
    def setup_lighting(self):
        """Set up basic lighting for the scene"""
        # Ambient light - more yellowish for backrooms feel
        AmbientLight(color=color.rgb(100, 85, 30))  # More yellow/sepia tone
        
        # Multiple point lights to simulate flickering fluorescent lights
        # Create several lights at different positions above the floor
        for x in range(0, self.map.width, 10):  # Every 10 units
            for z in range(0, self.map.height, 10):  # Every 10 units
                if random.random() > 0.3:  # Not all lights
                    light = PointLight(
                        position=Vec3(x, 2.8, z),  # Just under the ceiling
                        color=color.rgb(220, 220, 150),  # Warm yellow light
                        intensity=random.uniform(0.3, 0.8),  # Varying intensities
                        range=10
                    )
                    # Add some lights that flicker
                    if random.random() > 0.7:
                        light.intensity = random.uniform(0.1, 0.2)  # Dimmer for flickering effect
        
        # A subtle directional light for general illumination
        self.directional_light = DirectionalLight()
        self.directional_light.color = color.rgb(180, 170, 100)  # Warm yellow light
        self.directional_light.rotation = Vec3(45, -45, 0)
    
    def setup_audio(self):
        """Set up audio system"""
        # Ursina doesn't have built-in audio manager, so we'll use pygame.mixer for background music
        try:
            import pygame.mixer
            pygame.mixer.init()
            
            if os.path.exists("audio/atomiste.mp3"):
                pygame.mixer.music.load("audio/atomiste.mp3")
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)  # Loop indefinitely
        except ImportError:
            print("pygame not available for audio playback")
    
    def setup_player(self):
        """Set up the first person player controller"""
        # Create first person controller
        self.player = FirstPersonController()
        # Start position at the beginning of the maze
        self.player.position = Vec3(self.map.start_pos[0] + 0.5, 1.5, self.map.start_pos[1] + 0.5)  # Start position adjusted for wall height
        self.player.speed = self.player_speed
        
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
            self.player.position = Vec3(self.map.start_pos[0] + 0.5, 1.5, self.map.start_pos[1] + 0.5)  # Reset position
        elif key == 'escape':
            application.quit()
    
    def update(self):
        """Update game logic every frame"""
        # Update reality distortion effects
        self.update_reality()
        
        # Update hallucination effects
        self.update_hallucinations()
    
    def update_reality(self):
        """Update reality distortion effects"""
        # Gradually decrease reality stability
        self.reality_stability -= self.config.reality_decay_rate
        
        # Randomly increase hallucination level
        self.hallucination_level += random.uniform(-0.001, 0.002)
        self.hallucination_level = max(0, min(1.0, self.hallucination_level))
        
        # Apply reality distortion effects
        if self.hallucination_level > self.config.hallucination_threshold:
            # Apply visual distortion effects
            self.apply_visual_distortion()
    
    def update_hallucinations(self):
        """Update hallucination effects"""
        # Change lighting randomly when hallucinating
        if self.hallucination_level > 0.5:
            flicker = random.random() < 0.05  # 5% chance each frame for more frequent flickering
            if flicker:
                # Create more unsettling color shifts
                hue_shift = random.uniform(0, 360)
                saturation = random.uniform(0.3, 1.0)
                value = random.uniform(0.2, 0.8)
                new_light_color = color.hsv(hue_shift, saturation, value)
                self.directional_light.color = new_light_color
        
        # Add occasional sound effects for immersion
        current_time = time.time()
        if current_time - self.last_sound_time > random.uniform(10, 30) and random.random() < 0.3:
            # In a real implementation, we would play ambient sounds here
            self.last_sound_time = current_time
    
    def apply_visual_distortion(self):
        """Apply visual distortion effects when reality is unstable"""
        # For now, just print a message to indicate distortion
        # In a full implementation, we would modify the camera or shader effects
        pass


if __name__ == "__main__":
    # Create and run the game
    app = Ursina()
    game = BackroomsGame()
    app.run()
