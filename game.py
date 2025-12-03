#!/usr/bin/env python3
# main game script - StubbornBackroom: Psycho Dream
# 3D Backrooms Python 3.11 Prototype with Ursina

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
    window_size: tuple = (1280, 720)
    window_type = 'windowed'  # ['windowed', 'fullscreen', 'borderless']
    fps: int = 60
    title: str = "StubbornBackroom: Psycho Dream"
    player_speed: float = 5.0
    mouse_sensitivity: tuple = (40, 40)
    gravity: float = -9.81
    reality_decay_rate: float = 0.0001
    hallucination_threshold: float = 0.7


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


class BackroomsGame(Ursina):
    def __init__(self):
        # Initialize Ursina
        super().__init__()
        
        # Configuration
        self.config = Config()
        
        # Set window properties
        window.title = self.config.title
        window.borderless = False
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
        if os.path.exists("maps/generated_map.json"):
            self.map.load_from_file("maps/generated_map.json")
        else:
            self.map.generate_maze()
            self.map.save_to_file("maps/generated_map.json")
        
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
            texture='textures/floor_texture.png',
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
                        texture_scale=Vec2(1, 1),
                        scale=(1, 3, 1),  # Width, height, depth
                        x=x,
                        y=1.5,  # Center height
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
            elif key == 'escape':
                application.quit()
        
        self.input_handler = on_input
    
    def setup_lighting(self):
        """Set up basic lighting for the scene"""
        # Ambient light
        AmbientLight(color=color.rgb(77, 77, 51))  # Slightly yellowish ambient
        
        # Directional light (sun-like)
        self.directional_light = DirectionalLight()
        self.directional_light.color = color.rgb(204, 191, 128)  # Warm yellow light
        self.directional_light.rotation = Vec3(45, -45, 0)
        
        # Player flashlight will be handled by the player controller
    
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
        self.player.position = Vec3(1.5, 1.5, 1.5)  # Start position
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
            flicker = random.random() < 0.02  # 2% chance each frame
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
    game = BackroomsGame()
    game.run()locity[2] += self.gravity * dt
        
        # Update vertical position
        new_pos = self.player_pos + self.player_velocity * dt
        self.player_pos = new_pos
        
        # Simple ground collision
        if self.player_pos[1] <= 0:
            self.player_pos[1] = 0
            self.player_velocity[1] = 0
            self.on_ground = True
        
        # Check if player is near the "exit"
        exit_x, exit_z = self.map.end_pos
        distance_to_exit = math.sqrt((self.player_pos[0] - exit_x)**2 + (self.player_pos[2] - exit_z)**2)
        if distance_to_exit < 1.0:
            print("You found the exit!")
            # In a real game, you'd transition to the next level or end the game
        
        return Task.cont
    
    def update_camera(self, task):
        """Update camera position and orientation"""
        dt = globalClock.getDt()
        
        # Update camera to follow player
        self.camera.setPos(self.player_pos[0], self.player_pos[1] + 1.8, self.player_pos[2])  # Eye level
        
        # Handle mouse look if enabled
        if self.mouse_control_enabled and self.mouseWatcherNode.hasMouse():
            mouse_x = self.mouseWatcherNode.getMouseX()
            mouse_y = self.mouseWatcherNode.getMouseY()
            
            # Calculate mouse movement since last frame
            if not hasattr(self, 'last_mouse_x'):
                self.last_mouse_x = mouse_x
                self.last_mouse_y = mouse_y
            
            mouse_dx = mouse_x - self.last_mouse_x
            mouse_dy = mouse_y - self.last_mouse_y
            
            # Update player heading and pitch based on mouse movement
            self.player_hpr[0] -= mouse_dx * self.mouse_sensitivity * 50
            self.player_hpr[1] = max(-90, min(90, self.player_hpr[1] - mouse_dy * self.mouse_sensitivity * 50))
            
            # Apply rotation to camera
            self.camera.setHpr(self.player_hpr[0], self.player_hpr[1], 0)
            
            # Reset mouse position to center to prevent cursor from leaving window
            self.win.movePointer(0, 
                                int(self.win.getProperties().getXSize() / 2),
                                int(self.win.getProperties().getYSize() / 2))
            
            # Update last mouse position
            self.last_mouse_x = self.win.getProperties().getXSize() / 2
            self.last_mouse_y = self.win.getProperties().getYSize() / 2
        else:
            # Update camera rotation based on player's heading/pitch
            self.camera.setHpr(self.player_hpr[0], self.player_hpr[1], 0)
        
        return Task.cont
    
    def update_flashlight(self, task):
        """Update flashlight position and direction"""
        # Position the flashlight at the camera
        self.flashlight_np.set_pos(self.camera.getPos())
        self.flashlight_np.set_hpr(self.camera.getHpr())
        return Task.cont
    
    def update_reality(self, task):
        """Update reality stability and hallucination levels"""
        dt = globalClock.getDt()
        
        # Reality decay based on isolation and darkness
        decay_rate = self.config.reality_decay_rate
        
        # Check if player is in a dark area (simplified)
        # In a real implementation, this would be based on light levels at player position
        self.time_in_darkness += dt
        if self.background_music.status() == 2:  # Playing
            self.last_sound_time = 0
        else:
            self.last_sound_time += dt
        
        # Increase decay rate if player is alone in darkness for too long
        if self.time_in_darkness > 10.0:
            decay_rate *= 2.0
        
        # Update reality stability
        self.reality_stability = max(0.0, self.reality_stability - decay_rate)
        
        # Update hallucination level
        self.hallucination_level = 1.0 - self.reality_stability
        
        # Apply visual effects based on hallucination level
        self.apply_reality_effects()
        
        return Task.cont
    
    def apply_reality_effects(self):
        """Apply visual and audio effects based on reality level"""
        # Change background color based on reality stability
        base_color = (0.8, 0.75, 0.3)  # Base backrooms yellow
        distortion_color = (0.9, 0.3, 0.3)  # Red for distortion
        
        r = base_color[0] + (distortion_color[0] - base_color[0]) * self.hallucination_level
        g = base_color[1] + (distortion_color[1] - base_color[1]) * self.hallucination_level
        b = base_color[2] + (distortion_color[2] - base_color[2]) * self.hallucination_level
        
        self.setBackgroundColor(r, g, b)
    
    def set_camera_position(self):
        """Set initial camera position"""
        self.camera.setPos(self.player_pos[0], self.player_pos[1] + 1.8, self.player_pos[2])  # Eye level
        self.camera.setHpr(0, 0, 0)


def main():
    """Main function to run the game"""
    # Create and run the game
    game = BackroomsGame()
    game.run()


if __name__ == "__main__":
    main()

