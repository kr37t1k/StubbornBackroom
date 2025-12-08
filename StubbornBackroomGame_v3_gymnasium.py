#!/usr/bin/env python3
"""
StubbornBackroom: Psycho Dream - Gymnasium Version
Version with gymnasium integration for AI training
"""

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import math
import json
import os
from enum import Enum
import gymnasium as gym
from gymnasium import spaces
import numpy as np


class RealityState(Enum):
    STABLE = 0
    DISTORTED = 1
    LIMINAL = 2
    CHAOTIC = 3


# 🌌 LIMINALCORE COLOR PALETTE
LIMINAL_YELLOW = color.hsv(45, 0.18, 0.90)  # More saturated yellow
LIMINAL_BEIGE = color.hsv(35, 0.12, 0.92)   # More defined beige
LIMINAL_GRAY = color.hsv(0, 0.02, 0.85)     # Subtle gray
LIMINAL_AMBER = color.hsv(30, 0.25, 0.88)   # Warm amber for liminal spaces

# Enhanced atmosphere
# app = Ursina(borderless=False)
scene.fog_color = LIMINAL_BEIGE.tint(-0.4)
scene.fog_density = 0.015


class BackroomsEnv(gym.Env):
    """Gymnasium environment for the Backrooms game"""
    def __init__(self):
        super(BackroomsEnv, self).__init__()
        
        # Define action and observation space
        # Actions: [forward, backward, left, right, jump]
        self.action_space = spaces.Discrete(5)  # 0: forward, 1: backward, 2: left, 3: right, 4: jump
        
        # Observation space: player position (x, y, z), reality state, distortion level
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(6,), dtype=np.float32
        )
        
        # Initialize game components
        self.reality = RealityDistortion()
        self.world = BackroomsGenerator()
        self.player = LiminalPlayer(
            model='cube',
            y=1.0,
            origin_y=-0.5,
            color=LIMINAL_AMBER.tint(0.3),
            gravity=1.0
        )
        
        # Create enhanced environment
        self.liminal_sky = LiminalSky()
        self.liminal_particles = LiminalParticles()
        self.liminal_message = LiminalMessage()
        
        # Episode tracking
        self.episode_step = 0
        self.max_steps = 1000
        self.reset()
    
    def reset(self, seed=None, options=None):
        """Reset the environment to initial state"""
        super().reset(seed=seed)
        
        # Reset player position
        self.player.position = Vec3(0, 1.0, 0)
        self.player.speed = 6
        self.player.jump_height = 2.0
        
        # Reset reality distortion
        self.reality.distortion_level = 0.0
        self.reality.reality_stability = 1.0
        self.reality.state = RealityState.STABLE
        self.reality.state_change_cooldown = 0
        
        # Reset episode tracking
        self.episode_step = 0
        
        # Return initial observation
        obs = np.array([
            self.player.position.x,
            self.player.position.y,
            self.player.position.z,
            self.reality.distortion_level,
            self.reality.reality_stability,
            self.reality.state.value
        ], dtype=np.float32)
        
        return obs, {}
    
    def step(self, action):
        """Execute one step in the environment"""
        self.episode_step += 1
        
        # Execute action
        self._execute_action(action)
        
        # Update reality distortion
        self.reality.update(time.dt)
        
        # Calculate reward based on movement and stability
        reward = self._calculate_reward()
        
        # Check if episode is done
        terminated = self._check_termination()
        truncated = self.episode_step >= self.max_steps
        
        # Get new observation
        obs = np.array([
            self.player.position.x,
            self.player.position.y,
            self.player.position.z,
            self.reality.distortion_level,
            self.reality.reality_stability,
            self.reality.state.value
        ], dtype=np.float32)
        
        return obs, reward, terminated, truncated, {}
    
    def _execute_action(self, action):
        """Execute the given action"""
        # Simple movement based on action
        move_distance = 0.1 * self.player.speed
        
        if action == 0:  # forward
            self.player.position += self.player.forward * move_distance
        elif action == 1:  # backward
            self.player.position -= self.player.forward * move_distance
        elif action == 2:  # left
            self.player.position -= self.player.right * move_distance
        elif action == 3:  # right
            self.player.position += self.player.right * move_distance
        elif action == 4:  # jump
            # Simple jump simulation
            self.player.y += 0.5
        
        # Update player movement tracking
        self.player.moved_recently = True
        self.player.move_timer = 0
    
    def _calculate_reward(self):
        """Calculate reward based on current state"""
        reward = 0
        
        # Positive reward for exploring (moving to new positions)
        if self.player.moved_recently:
            reward += 0.1
        
        # Negative reward for high reality distortion
        reward -= self.reality.distortion_level * 0.5
        
        # Positive reward for maintaining stability
        reward += self.reality.reality_stability * 0.2
        
        # Small time penalty to encourage efficient exploration
        reward -= 0.01
        
        return reward
    
    def _check_termination(self):
        """Check if the episode should terminate"""
        # For now, terminate if reality distortion is too high
        return self.reality.distortion_level > 0.9
    
    def render(self, mode='human'):
        """Render the environment"""
        # In this 3D environment, rendering is handled by Ursina
        pass
    
    def close(self):
        """Close the environment"""
        # Clean up resources if needed
        pass


class RealityDistortion:
    """Reality distortion system for the gym environment"""
    def __init__(self):
        self.distortion_level = 0.0
        self.reality_stability = 1.0
        self.state = RealityState.STABLE
        self.state_change_cooldown = 0
    
    def update(self, dt):
        # Reality becomes less stable the longer you stay in one place
        if not hasattr(self, 'moved_recently'):
            self.moved_recently = True
        if not self.moved_recently:
            self.reality_stability = max(0.2, self.reality_stability - dt * 0.05)
        else:
            self.reality_stability = min(1.0, self.reality_stability + dt * 0.1)
        
        self.distortion_level = (1.0 - self.reality_stability) * 0.5
        
        # Update reality state based on distortion
        if self.state_change_cooldown <= 0:
            if self.distortion_level > 0.7:
                self.state = RealityState.CHAOTIC
            elif self.distortion_level > 0.4:
                self.state = RealityState.LIMINAL
            elif self.distortion_level > 0.1:
                self.state = RealityState.DISTORTED
            else:
                self.state = RealityState.STABLE
            
            self.state_change_cooldown = 5  # Cooldown between state changes
        else:
            self.state_change_cooldown -= dt


class BackroomsGenerator:
    """Optimized backrooms generator using only pre-made maps for gym environment"""
    def __init__(self):
        self.room_size = 8  # Larger rooms for better exploration
        self.wall_height = 6
        self.ceiling_height = 4.5
        self.loaded_map = None
        self.loaded_map_name = ""
        self.map_directory = "maps"
        self.map_files = self.get_map_files()
        self.current_map_index = 0
        self.entities = []  # Store all created entities for cleanup
        self.load_map_from_file()  # Load default map
    
    def get_map_files(self):
        """Get list of available map files"""
        if not os.path.exists(self.map_directory):
            os.makedirs(self.map_directory)
        
        files = []
        for file in os.listdir(self.map_directory):
            if file.endswith('.json'):
                files.append(file)
        return files if files else ["first_map_from_AdvancedMapEditor.json"]  # fallback
    
    def load_map_from_file(self, filename=None):
        """Load a map from JSON file"""
        if filename is None:
            filename = self.map_files[self.current_map_index % len(self.map_files)]
        
        filepath = os.path.join(self.map_directory, filename)
        
        try:
            with open(filepath, 'r') as f:
                self.loaded_map = json.load(f)
            
            # Clear any existing entities
            self.clear_all_entities()
            # Create rooms from the loaded map data
            self.create_rooms_from_loaded_map()
            self.loaded_map_name = filename
            print(f"Loaded map: {filename}")
        except Exception as e:
            print(f"Failed to load map {filename}: {e}")
            # Create a simple default map if loading fails
            self.create_default_map()
    
    def create_default_map(self):
        """Create a simple default map if file loading fails"""
        # Create a simple 5x5 room
        self.loaded_map = {
            "width": 5,
            "height": 5,
            "map": [
                [1, 1, 1, 1, 1],
                [1, 0, 0, 0, 1],
                [1, 0, 0, 0, 1],
                [1, 0, 0, 0, 1],
                [1, 1, 1, 1, 1]
            ],
            "entities": []
        }
        self.loaded_map_name = "default"
        self.clear_all_entities()
        self.create_rooms_from_loaded_map()
    
    def create_rooms_from_loaded_map(self):
        """Create 3D rooms from the loaded map data"""
        if self.loaded_map is None or self.loaded_map == {}:
            return
        
        # Get map dimensions and data
        width = self.loaded_map.get('width', 10)
        height = self.loaded_map.get('height', 10)
        map_grid = self.loaded_map.get('map', [])
        entities_data = self.loaded_map.get('entities', [])
        
        # Scale factor to convert map grid coordinates to 3D world coordinates
        room_scale = self.room_size
        
        # Create rooms based on the map grid
        for y in range(len(map_grid)):
            if y >= height:
                break
            for x in range(len(map_grid[y])):
                if x >= width:
                    break
                cell_type = map_grid[y][x]
                
                # Only create rooms for path tiles (0) and special tiles (2, 3, 4)
                if cell_type in [0, 2, 3, 4]:  # Path, door, special, liminal
                    # Convert grid coordinates to 3D world coordinates
                    # Center the map around the origin
                    world_x = (x - width // 2) * room_scale
                    world_z = (y - height // 2) * room_scale
                    
                    # Determine room type based on cell type
                    if cell_type == 0:  # Path
                        room_type = 'hallway'
                    elif cell_type == 2:  # Door
                        room_type = 'junction'
                    elif cell_type == 3:  # Special
                        room_type = 'special'
                    elif cell_type == 4:  # Liminal
                        room_type = 'liminal'
                    else:
                        room_type = 'hallway'
                    
                    # Create the room
                    self._create_room_at_position(world_x, world_z, room_type)
        
        # Create entities from the map data
        for entity_data in entities_data:
            self._create_entity_from_data(entity_data)
    
    def _create_room_at_position(self, x, z, room_type='hallway'):
        """Create a single room at a specific position with optimized structure"""
        room_center = Vec3(x, 0, z)
        
        # Create floor
        floor = Entity(
            model='plane',
            scale=(self.room_size, 1, self.room_size),
            position=room_center + Vec3(0, -0.1, 0),
            color=self._get_room_color(room_type),
            collider='box'
        )
        self.entities.append(floor)
        
        # Create ceiling
        ceiling = Entity(
            model='plane',
            scale=(self.room_size, 1, self.room_size),
            position=room_center + Vec3(0, self.ceiling_height, 0),
            rotation=(180, 0, 0),
            color=self._get_ceiling_color(room_type),
            collider='box'
        )
        self.entities.append(ceiling)
        
        # Create ceiling glow effect
        ceiling_glow = Entity(
            model='plane',
            parent=ceiling,
            scale=(self.room_size + 0.1, 1, self.room_size + 0.1),
            color=color.rgba(255, 245, 200, 40),
            unlit=True
        )
        self.entities.append(ceiling_glow)
        
        # Create walls with doorways based on adjacent cells
        self._create_walls_for_room(x, z, room_type)
        
        # Add room-specific decorations based on reality state
        self._add_room_decorations(room_center, room_type)
    
    def _create_walls_for_room(self, x, z, room_type):
        """Create walls for a room based on adjacent cells in the map"""
        # This function will check adjacent cells to determine where to place walls
        if self.loaded_map is None:
            return
            
        map_grid = self.loaded_map.get('map', [])
        width = self.loaded_map.get('width', 10)
        height = self.loaded_map.get('height', 10)
        
        # Convert world coordinates back to grid coordinates
        grid_x = int((x / self.room_size) + width // 2)
        grid_z = int((z / self.room_size) + height // 2)
        
        # Check adjacent cells to determine wall placement
        wall_connections = []
        
        # Check north
        if grid_z + 1 < height and map_grid[grid_z + 1][grid_x] in [0, 2, 3, 4]:
            wall_connections.append('north')
        # Check south
        if grid_z - 1 >= 0 and map_grid[grid_z - 1][grid_x] in [0, 2, 3, 4]:
            wall_connections.append('south')
        # Check east
        if grid_x + 1 < width and map_grid[grid_z][grid_x + 1] in [0, 2, 3, 4]:
            wall_connections.append('east')
        # Check west
        if grid_x - 1 >= 0 and map_grid[grid_z][grid_x - 1] in [0, 2, 3, 4]:
            wall_connections.append('west')
        
        room_center = Vec3(x, 0, z)
        self._create_walls_with_doorways(room_center, room_type, wall_connections)
    
    def _get_room_color(self, room_type):
        """Get appropriate color based on room type and reality state"""
        base_color = LIMINAL_YELLOW
        
        if room_type == 'liminal':
            return LIMINAL_AMBER
        elif room_type == 'chaotic':
            return LIMINAL_GRAY.tint(random.uniform(-0.1, 0.1))
        elif room_type == 'distorted':
            return base_color.tint(random.uniform(-0.2, 0.2))
        else:
            return base_color.tint(random.uniform(-0.1, 0.1))
    
    def _get_ceiling_color(self, room_type):
        """Get appropriate ceiling color"""
        base_color = LIMINAL_YELLOW.tint(0.15)
        
        if room_type == 'liminal':
            return LIMINAL_AMBER.tint(0.1)
        elif room_type == 'chaotic':
            return LIMINAL_GRAY.tint(0.1)
        else:
            return base_color
    
    def _create_walls_with_doorways(self, room_center, room_type, connections):
        """Create walls with doorways in connected directions"""
        wall_thickness = 0.5
        wall_color = self._get_room_color(room_type)
        
        # Create walls based on connections
        for direction in ['north', 'south', 'east', 'west']:
            if direction not in connections:
                wall = self._create_wall(room_center, direction, wall_thickness, wall_color)
                self.entities.append(wall)
            else:
                walls = self._create_wall_with_doorway(room_center, direction, wall_thickness, wall_color)
                self.entities.extend(walls)
    
    def _create_wall(self, center, direction, thickness, color):
        """Create a full wall"""
        if direction in ['north', 'south']:
            scale = (self.room_size, self.wall_height, thickness)
            offset = (0, self.wall_height / 2, self.room_size / 2 if direction == 'north' else -self.room_size / 2)
        else:  # east, west
            scale = (thickness, self.wall_height, self.room_size)
            offset = (self.room_size / 2 if direction == 'east' else -self.room_size / 2, self.wall_height / 2, 0)
        
        wall = Entity(
            model='cube',
            scale=scale,
            position=center + Vec3(offset),
            color=color,
            collider='box'
        )
        
        # Add subtle variations
        wall.scale += Vec3(random.uniform(-0.05, 0.05), random.uniform(-0.05, 0.05), random.uniform(-0.05, 0.05))
        wall.color = wall.color.tint(random.uniform(-0.03, 0.03))
        
        return wall
    
    def _create_wall_with_doorway(self, center, direction, thickness, color):
        """Create a wall with a doorway in the middle - optimized version"""
        walls = []
        
        # Fixed door size
        door_size = 3
        
        if direction in ['north', 'south']:
            # Create two wall segments
            # Left segment
            left_scale = ((self.room_size - door_size) / 2, self.wall_height, thickness)
            left_offset = (-self.room_size/4 - door_size/4, self.wall_height / 2, 
                          self.room_size / 2 if direction == 'north' else -self.room_size / 2)
            
            left_wall = Entity(
                model='cube',
                scale=left_scale,
                position=center + Vec3(left_offset),
                color=color,
                collider='box'
            )
            
            # Right segment
            right_scale = ((self.room_size - door_size) / 2, self.wall_height, thickness)
            right_offset = (self.room_size/4 + door_size/4, self.wall_height / 2, 
                           self.room_size / 2 if direction == 'north' else -self.room_size / 2)
            
            right_wall = Entity(
                model='cube',
                scale=right_scale,
                position=center + Vec3(right_offset),
                color=color,
                collider='box'
            )
            
            # Add variations
            for wall_ent in [left_wall, right_wall]:
                wall_ent.scale += Vec3(random.uniform(-0.05, 0.05), random.uniform(-0.05, 0.05), random.uniform(-0.05, 0.05))
                wall_ent.color = wall_ent.color.tint(random.uniform(-0.03, 0.03))
                walls.append(wall_ent)
        
        else:  # east, west
            # Create two wall segments
            # Top segment
            top_scale = (thickness, self.wall_height, (self.room_size - door_size) / 2)
            top_offset = (self.room_size / 2 if direction == 'east' else -self.room_size / 2, 
                         self.wall_height / 2, -self.room_size/4 - door_size/4)
            
            top_wall = Entity(
                model='cube',
                scale=top_scale,
                position=center + Vec3(top_offset),
                color=color,
                collider='box'
            )
            
            # Bottom segment
            bottom_scale = (thickness, self.wall_height, (self.room_size - door_size) / 2)
            bottom_offset = (self.room_size / 2 if direction == 'east' else -self.room_size / 2, 
                            self.wall_height / 2, self.room_size/4 + door_size/4)
            
            bottom_wall = Entity(
                model='cube',
                scale=bottom_scale,
                position=center + Vec3(bottom_offset),
                color=color,
                collider='box'
            )
            
            # Add variations
            for wall_ent in [top_wall, bottom_wall]:
                wall_ent.scale += Vec3(random.uniform(-0.05, 0.05), random.uniform(-0.05, 0.05), random.uniform(-0.05, 0.05))
                wall_ent.color = wall_ent.color.tint(random.uniform(-0.03, 0.03))
                walls.append(wall_ent)
        
        return walls
    
    def _add_room_decorations(self, center, room_type):
        """Add room-specific decorations with reduced frequency for performance"""
        # Reduce decoration frequency for better performance
        if room_type in ['liminal', 'chaotic', 'distorted']:
            # Add more decorations for liminal/chaotic rooms
            for _ in range(random.randint(0, 1)):
                if random.random() < 0.3:  # 30% chance of decoration
                    self._add_random_decoration(center, room_type)
        else:
            # Normal rooms have fewer decorations
            if random.random() < 0.1:  # 10% chance of decoration
                self._add_random_decoration(center, room_type)
    
    def _add_random_decoration(self, center, room_type):
        """Add a random decoration to the room"""
        # Random position within the room
        x_offset = random.uniform(-self.room_size/2 + 1, self.room_size/2 - 1)
        z_offset = random.uniform(-self.room_size/2 + 1, self.room_size/2 - 1)
        
        # Don't place decorations too close to walls
        if abs(x_offset) > self.room_size/2 - 1.5 or abs(z_offset) > self.room_size/2 - 1.5:
            return
        
        position = center + Vec3(x_offset, 0.5, z_offset)
        
        # Choose decoration type based on room type
        if room_type in ['liminal', 'chaotic']:
            decoration_types = ['chair', 'light', 'strange_object']
        else:
            decoration_types = ['chair', 'light']
        
        decoration_type = random.choice(decoration_types)
        
        if decoration_type == 'chair':
            decoration = Entity(
                model='cube',
                scale=(0.8, 0.8, 0.8),
                position=position,
                color=LIMINAL_BEIGE.tint(-0.2),
                collider='box'
            )
        elif decoration_type == 'light':
            decoration = Entity(
                model='cube',
                scale=(0.3, 0.1, 0.3),
                position=position + Vec3(0, 2.0, 0),
                color=color.white,
                unlit=True,
                collider='box'
            )
        elif decoration_type == 'strange_object':
            # Something out of place in the backrooms
            decoration = Entity(
                model='sphere',
                scale=(0.6, 0.6, 0.6),
                position=position,
                color=color.blue.tint(random.uniform(-0.2, 0.2)),
                unlit=True,
                collider='box'
            )
        
        self.entities.append(decoration)

    def clear_all_entities(self):
        """Clear all generated entities from the scene"""
        for entity in self.entities:
            destroy(entity)
        self.entities.clear()


class LiminalPlayer:
    """Simplified player for gym environment"""
    def __init__(self, **kwargs):
        # Create a simple entity to represent the player
        self.entity = Entity(
            model='cube',
            y=1.0,
            origin_y=-0.5,
            color=LIMINAL_AMBER.tint(0.3),
            collider='box'
        )
        
        self.moved_recently = False
        self.move_timer = 0
        self.base_height = 1.0
        self.speed = 6
        self.jump_height = 2.0
        
        # Movement stats
        self.distance_traveled = 0
        self.last_position = Vec3(0, 1.0, 0)
        
        # Set initial position
        self.entity.position = self.last_position
    
    @property
    def position(self):
        return self.entity.position
    
    @position.setter
    def position(self, value):
        self.entity.position = value
    
    @property
    def forward(self):
        # Simple forward direction (positive Z)
        return Vec3(0, 0, 1)
    
    @property
    def right(self):
        # Simple right direction (positive X)
        return Vec3(1, 0, 0)


class LiminalSky(Entity):
    """Simplified sky for gym environment"""
    def __init__(self):
        super().__init__(
            parent=scene,
            model='sphere',
            scale=2000,  # Larger for more immersive feel
            double_sided=True,
            unlit=True
        )
        self.color = LIMINAL_BEIGE.tint(-0.3)


class LiminalParticles(Entity):
    """Simplified particle system for gym environment"""
    def __init__(self):
        super().__init__(parent=scene)
        # No particles for gym environment to improve performance


class LiminalMessage:
    """Simplified message system for gym environment"""
    def __init__(self):
        self.text = ""
        self.current_message = ""
        self.timer = 0
        self.fade_timer = 0
        self.message_interval = 15


def input(key):
    """Handle input events - only for manual testing"""
    if key == 'escape':
        application.quit()


def update():
    """Main update loop - only for manual testing"""
    # This function is mainly for manual testing
    # The gym environment handles updates in its step function


# Create the gym environment
env = BackroomsEnv()

# Configure window for visualization (when running manually)
scene.background_color = LIMINAL_BEIGE.tint(-0.5)
window.title = 'Liminalcore Backrooms • Gymnasium Environment'
window.fps_counter.enabled = True
window.exit_button.visible = False

# Set window size
window.size = (1400, 900)
window.position = (50, 50)

print("StubbornBackrooms • Psycho Dream - Gymnasium Version")
print("This version is designed for AI training with gymnasium interface")
print("Use env.step(action) to interact with the environment")

# For manual testing, you can uncomment the following:
if __name__ == "__main__":
    # Example of how to use the environment
    observation, info = env.reset()
    print("Initial observation:", observation)
    
    for i in range(100):
        action = env.action_space.sample()  # Random action
        observation, reward, terminated, truncated, info = env.step(action)
        print(f"Step {i}: Action={action}, Obs={observation}, Reward={reward}")
        
        if terminated or truncated:
            print("Episode finished, resetting...")
            observation, info = env.reset()
    
    app.run()