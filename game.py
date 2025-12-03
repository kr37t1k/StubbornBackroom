#!/usr/bin/env python3
# main game script - StubbornBackroom: Psycho Dream
# 3D Backrooms Python 3.11 Prototype

import math
import random
from dataclasses import dataclass
from typing import Tuple, List, Dict, Optional

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import *

import numpy as np
import json
import os
import sys


@dataclass
class Config:
    window_size: tuple = (1280, 720)
    window_type = 'windowed'  # ['windowed', 'fullscreen', 'borderless']
    fps: int = 60
    title: str = "StubbornBackroom: Psycho Dream"
    icon_path: str = "textures/wall_texture.png"
    player_speed: float = 5.0
    mouse_sensitivity: float = 0.1
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


class BackroomsGame(ShowBase):
    def __init__(self):
        # Initialize the ShowBase class
        ShowBase.__init__(self)
        
        # Disable default mouse control
        self.disableMouse()
        
        # Configuration
        self.config = Config()
        
        # Set window properties
        self.win.set_title(self.config.title)
        
        # Player properties
        self.player_speed = self.config.player_speed
        self.mouse_sensitivity = self.config.mouse_sensitivity
        self.gravity = self.config.gravity
        self.player_pos = LPoint3f(1.5, 0, 1.5)  # Start position
        self.player_hpr = LPoint3f(0, 0, 0)  # Heading, pitch, roll
        self.player_velocity = LVector3f(0, 0, 0)
        self.is_jumping = False
        self.on_ground = True
        
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
        self.setup_tasks()
        
        # Set initial camera position
        self.set_camera_position()
    
    def setup_scene(self):
        """Set up the 3D scene with walls and floors based on the map"""
        # Set background color to backrooms yellow
        self.setBackgroundColor(0.8, 0.75, 0.3)  # Distinctive backrooms yellow
        
        # Create the floor
        self.create_floor()
        
        # Create walls based on map
        self.create_walls_from_map()
        
        # Create ceiling
        self.create_ceiling()
    
    def create_floor(self):
        """Create the floor of the backrooms"""
        # Create a large square for the floor
        floor_size = max(self.map.width, self.map.height) * 2
        floor_center_x = (self.map.width - 1) 
        floor_center_z = (self.map.height - 1)
        
        # Load floor texture
        floor_tex = self.loader.loadTexture("textures/floor_texture.png")
        floor_tex.setWrapU(Texture.WM_repeat)
        floor_tex.setWrapV(Texture.WM_repeat)
        floor_tex.setMinfilter(Texture.FT_linear_mipmap_linear)
        
        # Create a square for the floor
        cm = CardMaker("floor")
        cm.setFrame(-floor_size/2, floor_size/2, -floor_size/2, floor_size/2)
        floor = self.render.attachNewNode(cm.generate())
        floor.setPos(floor_center_x, 0, floor_center_z)
        floor.setP(-90)  # Rotate to be horizontal
        floor.setTexture(floor_tex)
        floor.setTexScale(floor_tex, 10)  # Repeat texture
        
        # Make it solid for collision
        floor.setCollideMask(BitMask32.bit(1))
    
    def create_ceiling(self):
        """Create the ceiling of the backrooms"""
        # Create a large square for the ceiling
        ceiling_size = max(self.map.width, self.map.height) * 2
        ceiling_center_x = (self.map.width - 1) 
        ceiling_center_z = (self.map.height - 1)
        
        # Load ceiling texture (same as floor for now)
        ceiling_tex = self.loader.loadTexture("textures/floor_texture.png")
        ceiling_tex.setWrapU(Texture.WM_repeat)
        ceiling_tex.setWrapV(Texture.WM_repeat)
        ceiling_tex.setMinfilter(Texture.FT_linear_mipmap_linear)
        
        # Create a square for the ceiling
        cm = CardMaker("ceiling")
        cm.setFrame(-ceiling_size/2, ceiling_size/2, -ceiling_size/2, ceiling_size/2)
        ceiling = self.render.attachNewNode(cm.generate())
        ceiling.setPos(ceiling_center_x, 3, ceiling_center_z)  # 3 units above floor
        ceiling.setP(90)  # Rotate to be horizontal (facing down)
        ceiling.setTexture(ceiling_tex)
        ceiling.setTexScale(ceiling_tex, 10)  # Repeat texture
        
        # Make it solid for collision
        ceiling.setCollideMask(BitMask32.bit(1))
    
    def create_walls_from_map(self):
        """Create 3D walls based on the 2D map"""
        wall_tex = self.loader.loadTexture("textures/wall_texture.png")
        wall_tex.setWrapU(Texture.WM_repeat)
        wall_tex.setWrapV(Texture.WM_repeat)
        wall_tex.setMinfilter(Texture.FT_linear_mipmap_linear)
        
        for y in range(self.map.height):
            for x in range(self.map.width):
                if self.map.grid[y][x] == 1:  # Wall
                    # Create a wall at this position
                    wall = self.render.attachNewNode("wall")
                    wall.setPos(x, 0, y)
                    wall.setScale(1, 1, 3)  # Width, depth, height
                    
                    # Create a cube for the wall
                    cm = CardMaker("wall_side")
                    
                    # Front face
                    cm.setFrame(-0.5, 0.5, -0.5, 0.5)
                    front = wall.attachNewNode(cm.generate())
                    front.setPos(0, 0.5, 1.5)
                    front.setR(0)
                    front.setTexture(wall_tex)
                    
                    # Back face
                    back = wall.attachNewNode(cm.generate())
                    back.setPos(0, -0.5, 1.5)
                    back.setR(0)
                    back.setSx(-1)  # Flip texture
                    back.setTexture(wall_tex)
                    
                    # Left face
                    left = wall.attachNewNode(cm.generate())
                    left.setPos(-0.5, 0, 1.5)
                    left.setR(90)
                    left.setTexture(wall_tex)
                    
                    # Right face
                    right = wall.attachNewNode(cm.generate())
                    right.setPos(0.5, 0, 1.5)
                    right.setR(-90)
                    right.setTexture(wall_tex)
                    
                    # Top face
                    top = wall.attachNewNode(cm.generate())
                    top.setPos(0, 0, 3)
                    top.setR(-90)
                    top.setP(90)
                    top.setTexture(wall_tex)
                    
                    # Make wall solid for collision
                    wall.setCollideMask(BitMask32.bit(1))
    
    def setup_controls(self):
        """Set up keyboard and mouse controls"""
        # Keyboard controls
        self.accept("w", self.set_key, ["forward", True])
        self.accept("w-up", self.set_key, ["forward", False])
        self.accept("s", self.set_key, ["backward", True])
        self.accept("s-up", self.set_key, ["backward", False])
        self.accept("a", self.set_key, ["left", True])
        self.accept("a-up", self.set_key, ["left", False])
        self.accept("d", self.set_key, ["right", True])
        self.accept("d-up", self.set_key, ["right", False])
        self.accept("space", self.set_key, ["jump", True])
        self.accept("space-up", self.set_key, ["jump", False])
        self.accept("escape", sys.exit)
        
        # Mouse controls for looking around
        self.accept("mouse3", self.toggle_mouse_control)
        self.mouse_control_enabled = True
        
        # Initially hide the cursor
        props = WindowProperties()
        props.setCursorHidden(True)
        self.win.requestProperties(props)
    
    def toggle_mouse_control(self):
        """Toggle mouse control on/off"""
        self.mouse_control_enabled = not self.mouse_control_enabled
        props = WindowProperties()
        props.setCursorHidden(self.mouse_control_enabled)
        self.win.requestProperties(props)
    
    def set_key(self, key, value):
        """Set the state of a key"""
        self.keys[key] = value
    
    def setup_lighting(self):
        """Set up basic lighting for the scene"""
        # Ambient light
        ambient_light = AmbientLight("ambient_light")
        ambient_light.set_color((0.3, 0.3, 0.2, 1))  # Slightly yellowish ambient
        self.render.set_light(self.render.attach_new_node(ambient_light))
        
        # Directional light (sun-like)
        directional_light = DirectionalLight("directional_light")
        directional_light.set_color((0.8, 0.7, 0.5, 1))  # Warm yellow light
        directional_light.set_direction((-1, -1, -1))
        self.render.set_light(self.render.attach_new_node(directional_light))
        
        # Player flashlight
        self.flashlight = Spotlight("flashlight")
        self.flashlight.set_color((1.0, 0.95, 0.8, 1.0))
        self.flashlight.set_exponent(80)
        self.flashlight.set_fov(60)
        lens = PerspectiveLens()
        self.flashlight.set_lens(lens)
        
        self.flashlight_np = self.render.attach_new_node(self.flashlight)
        self.render.set_light(self.flashlight_np)
    
    def setup_audio(self):
        """Set up audio system"""
        # Load background music
        if os.path.exists("audio/atomiste.mp3"):
            self.background_music = self.loader.loadSfx("audio/atomiste.mp3")
            self.background_music.set_loop(True)
            self.background_music.set_volume(0.3)
            self.background_music.play()
    
    def setup_tasks(self):
        """Set up game tasks"""
        self.taskMgr.add(self.update_player, "update_player")
        self.taskMgr.add(self.update_camera, "update_camera")
        self.taskMgr.add(self.update_reality, "update_reality")
        self.taskMgr.add(self.update_flashlight, "update_flashlight")
    
    def update_player(self, task):
        """Update player movement and physics"""
        dt = globalClock.getDt()
        
        # Handle movement
        move_x = 0
        move_y = 0
        
        if self.keys["forward"]:
            move_y += 1
        if self.keys["backward"]:
            move_y -= 1
        if self.keys["left"]:
            move_x -= 1
        if self.keys["right"]:
            move_x += 1
        
        # Normalize diagonal movement
        if move_x != 0 and move_y != 0:
            move_x *= 0.7071
            move_y *= 0.7071
        
        # Apply movement relative to player's heading
        heading = self.player_hpr[0]
        rad_heading = math.radians(heading)
        
        move_x_real = move_x * math.cos(rad_heading) - move_y * math.sin(rad_heading)
        move_y_real = move_x * math.sin(rad_heading) + move_y * math.cos(rad_heading)
        
        # Update position
        new_x = self.player_pos[0] + move_x_real * self.player_speed * dt
        new_y = self.player_pos[1]
        new_z = self.player_pos[2] + move_y_real * self.player_speed * dt
        
        # Simple collision detection - check if new position is in a wall
        grid_x = int(new_x)
        grid_z = int(new_z)
        
        if (0 <= grid_x < self.map.width and 
            0 <= grid_z < self.map.height and 
            self.map.grid[grid_z][grid_x] == 0):  # 0 is path, 1 is wall
            self.player_pos[0] = new_x
            self.player_pos[2] = new_z
        
        # Handle jumping
        if self.keys["jump"] and self.on_ground:
            self.player_velocity[2] = 6.0  # Jump velocity
            self.on_ground = False
            self.is_jumping = True
        
        # Apply gravity
        self.player_velocity[2] += self.gravity * dt
        
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

