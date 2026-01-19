#!/usr/bin/env python3
"""
StubbornBackroom: Psycho Dream - OOP Version
An advanced Backrooms game built with the custom OOP game engine framework
"""

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import math
import json
import os
from enum import Enum

# Import our custom engine components
from core.engine import GameObject, Component, EntityManager, GameEngine, GameState
from core.fps_controller import FPSController
from core.ai_system import EnemyAI, AIBehavior, AITeamManager, TacticalAI


# 🌌 LIMINALCORE COLOR PALETTE
LIMINAL_YELLOW = color.hsv(45, 0.18, 0.90)  # More saturated yellow
LIMINAL_BEIGE = color.hsv(35, 0.12, 0.92)   # More defined beige
LIMINAL_GRAY = color.hsv(0, 0.02, 0.85)     # Subtle gray
LIMINAL_AMBER = color.hsv(30, 0.25, 0.88)   # Warm amber for liminal spaces


class RealityState(Enum):
    STABLE = 0
    DISTORTED = 1
    LIMINAL = 2
    CHAOTIC = 3


class RealityDistortion:
    """Enhanced reality distortion system"""
    def __init__(self):
        self.distortion_level = 0.0
        self.wave_offset = 0
        self.reality_stability = 1.0
        self.liminal_state_timer = 0
        self.state = RealityState.STABLE
        self.state_change_cooldown = 0
    
    def update(self, dt, player_moved_recently):
        self.wave_offset += dt * 0.5
        
        # Reality becomes less stable the longer you stay in one place
        if not player_moved_recently:
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
        
        # Update liminal state timer
        if self.state in [RealityState.LIMINAL, RealityState.CHAOTIC]:
            self.liminal_state_timer += dt
        else:
            self.liminal_state_timer = 0


class BackroomsGenerator:
    """Enhanced procedural backrooms generator with map loading support"""
    def __init__(self):
        self.room_size = 8  # Larger rooms for better exploration
        self.wall_height = 6
        self.ceiling_height = 4.5
        self.generated_positions = set()
        self.room_connections = {}
        self.last_generation_position = (0, 0)
        self.current_room_pos = (0, 0)
        self.current_connections = []
        self.loaded_map = "first_map_from_AdvancedMapEditor.json"
        self.map_directory = "maps"
        self.map_files = self.get_map_files()
        self.current_map_index = 3
        self.load_map_from_file()  # Load default map
    
    def get_map_files(self):
        """Get list of available map files"""
        if not os.path.exists(self.map_directory):
            os.makedirs(self.map_directory)
        
        files = []
        for file in os.listdir(self.map_directory):
            if file.endswith('.json'):
                files.append(file)
        return files
    
    def load_map_from_file(self, filename=None):
        """Load a map from JSON file"""
        if not self.map_files:
            # If no map files exist, generate default
            self.generate_default_map()
            return
        
        if filename is None:
            filename = self.map_files[self.current_map_index % len(self.map_files)]
        
        filepath = os.path.join(self.map_directory, filename)
        
        try:
            with open(filepath, 'r') as f:
                self.loaded_map = json.load(f)
            
            # Clear previously generated positions when loading a new map
            self.clear_generated_rooms()
            # Create rooms from the loaded map data
            self.create_rooms_from_loaded_map()
            print(f"Loaded map: {filename}")
        except Exception as e:
            print(f"Failed to load map {filename}: {e}")
            self.generate_default_map()
    
    def generate_default_map(self):
        """Generate a default procedural map"""
        # For now, we'll use the procedural generation
        self.loaded_map = None
    
    def create_rooms_from_loaded_map(self):
        """Create 3D rooms from the loaded map data"""
        if self.loaded_map is None or self.loaded_map == {}:
            return
        
        # Clear any existing generated rooms
        self.clear_generated_rooms()
        
        # Get map dimensions and data
        width = self.loaded_map.get('width', 100)
        height = self.loaded_map.get('height', 100)
        map_grid = self.loaded_map.get('map', [])
        entities = self.loaded_map.get('entities', [])
        
        # Scale factor to convert map grid coordinates to 3D world coordinates
        # Each grid cell will be one room
        room_scale = self.room_size  # Use the same room size as the procedural generator
        
        # Create rooms based on the map grid
        for y in range(len(map_grid)):
            for x in range(len(map_grid[y])):
                if x < width and y < height:
                    cell_type = map_grid[y][x]
                    
                    # Only create rooms for path tiles (0) and special tiles (3, 4)
                    # Walls (1) will have walls, doors (2) will have doorways
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
                        self._create_room_from_map_data(world_x, world_z, room_type, cell_type)
        
        # Create entities from the map data
        for entity_data in entities:
            self._create_entity_from_data(entity_data)
    
    def _create_room_from_map_data(self, x, z, room_type, cell_type):
        """Create a single room based on map data"""
        # Generate the room using the same method as the procedural generator
        # but with the specific coordinates from the map
        chunk_x = int(x / self.room_size)
        chunk_z = int(z / self.room_size)
        chunk_pos = (chunk_x, chunk_z)
        
        # Only generate if not already generated
        if chunk_pos not in self.generated_positions:
            self.generate_room(chunk_x, chunk_z)
            self.generated_positions.add(chunk_pos)
    
    def _create_entity_from_data(self, entity_data):
        """Create an entity from the loaded entity data"""
        # This is where we would create specific entities based on the map data
        # For now, we'll just log that we're processing an entity
        pass
    
    def clear_generated_rooms(self):
        """Clear all generated rooms from the scene"""
        # Remove all entities that were generated by the backrooms generator
        entities_to_destroy = []
        for entity in scene.entities:
            # Check if this entity was created by the room generator
            if hasattr(entity, 'is_generated_room'):
                entities_to_destroy.append(entity)
        
        for entity in entities_to_destroy:
            destroy(entity)
        
        # Clear the generated positions set
        self.generated_positions.clear()
        self.room_connections.clear()
    
    def generate_around_player(self, player_position):
        """Generate rooms around player or load from map if available"""
        # Check if we have a loaded map
        if self.loaded_map is not None and self.loaded_map != {}:
            # If a map is loaded, we don't generate procedurally
            # The loaded map should already be in place
            return
        
        player_chunk = (
            math.floor(player_position.x / self.room_size),
            math.floor(player_position.z / self.room_size)
        )
        
        # Only regenerate if player moved to a new chunk
        if player_chunk == self.last_generation_position:
            return
        
        self.last_generation_position = player_chunk
        self.current_room_pos = player_chunk
        
        # Generate 5x5 grid of rooms around player for better continuity
        for x in range(-2, 3):
            for z in range(-2, 3):
                chunk_x = player_chunk[0] + x
                chunk_z = player_chunk[1] + z
                chunk_pos = (chunk_x, chunk_z)
                
                if chunk_pos not in self.generated_positions:
                    self.generate_room(chunk_x, chunk_z)
                    self.generated_positions.add(chunk_pos)
    
    def generate_room(self, x, z):
        """Generate a single room"""
        room_center = Vec3(x * self.room_size, 0, z * self.room_size)
        room_key = (x, z)
        
        # Determine room type based on position and map data
        room_type = self._determine_room_type(x, z)
        connection_directions = self._get_room_connections(x, z, room_type)
        self.current_connections = connection_directions
        
        # Create floor
        floor = Entity(
            model='plane',
            scale=(self.room_size, 1, self.room_size),
            position=room_center + Vec3(0, -0.1, 0),
            color=self._get_room_color(room_type),
            collider='box'
        )
        floor.is_generated_room = True  # Tag as generated room entity
        
        # Create ceiling
        ceiling = Entity(
            model='plane',
            scale=(self.room_size, 1, self.room_size),
            position=room_center + Vec3(0, self.ceiling_height, 0),
            rotation=(180, 0, 0),
            color=self._get_ceiling_color(room_type),
            collider='box'
        )
        ceiling.is_generated_room = True  # Tag as generated room entity
        
        # Create ceiling glow effect
        ceiling_glow = Entity(
            model='plane',
            parent=ceiling,
            scale=(self.room_size + 0.1, 1, self.room_size + 0.1),
            color=color.rgba(255, 245, 200, 40),
            unlit=True
        )
        ceiling_glow.is_generated_room = True  # Tag as generated room entity
        
        # Create walls with doorways
        self._create_walls_with_doorways(room_center, room_type, connection_directions)
        
        # Add room-specific decorations based on reality state
        self._add_room_decorations(room_center, room_type)
    
    def _determine_room_type(self, x, z):
        """Determine room type based on position and reality state"""
        distance = math.sqrt(x * x + z * z)
        
        # Adjust room types based on reality state
        if reality.state == RealityState.CHAOTIC:
            # More chaotic room types
            return random.choice(['chaotic', 'distorted', 'junction'])
        elif reality.state == RealityState.LIMINAL:
            # More liminal room types
            return random.choice(['liminal', 'transition', 'junction'])
        else:
            # Normal room types
            if distance < 3:
                return 'junction'
            elif distance < 6:
                return random.choice(['hallway', 'corner', 'junction'])
            else:
                return random.choice(['hallway', 'room', 'corner'])
    
    def _get_room_connections(self, x, z, room_type):
        """Determine which directions have doorways"""
        connections = []
        
        # Base connections based on room type
        if room_type in ['junction', 'liminal', 'chaotic']:
            connections = ['north', 'south', 'east', 'west']
        elif room_type == 'hallway':
            if random.random() < 0.5:
                connections = ['north', 'south']
            else:
                connections = ['east', 'west']
        elif room_type == 'corner':
            choices = [
                ['north', 'east'],
                ['east', 'south'],
                ['south', 'west'],
                ['west', 'north']
            ]
            connections = random.choice(choices)
        elif room_type == 'room':
            directions = ['north', 'south', 'east', 'west']
            random.shuffle(directions)
            connections = directions[:random.randint(1, 2)]
        elif room_type == 'transition':
            # Special transitional rooms
            connections = ['north', 'south']
        elif room_type == 'distorted':
            # Distorted rooms have random connections
            directions = ['north', 'south', 'east', 'west']
            connections = random.sample(directions, random.randint(1, 3))
        
        # Ensure at least one connection for edge rooms
        if not connections:
            connections = random.choice([['north'], ['south'], ['east'], ['west']])
        
        return connections
    
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
        door_positions = {
            'north': (0, self.room_size / 2 - 2),
            'south': (0, -self.room_size / 2 + 2),
            'east': (self.room_size / 2 - 2, 0),
            'west': (-self.room_size / 2 + 2, 0)
        }
        
        door_size = 3
        wall_thickness = 0.5
        wall_color = self._get_room_color(room_type)
        
        # Create walls based on connections
        for direction in ['north', 'south', 'east', 'west']:
            if direction not in connections:
                self._create_wall(room_center, direction, wall_thickness, wall_color)
            else:
                self._create_wall_with_doorway(room_center, direction, wall_thickness, wall_color, door_size)
    
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
        
        wall.is_generated_room = True  # Tag as generated room entity
        
        # Add subtle variations
        wall.scale += Vec3(random.uniform(-0.05, 0.05), random.uniform(-0.05, 0.05), random.uniform(-0.05, 0.05))
        wall.color = wall.color.tint(random.uniform(-0.03, 0.03))
        
        # Create soft glow effect
        glow = Entity(
            model='cube',
            parent=wall,
            scale=wall.scale * 1.03,
            color=(255, 240, 220, 30),
            unlit=True
        )
        
        glow.is_generated_room = True  # Tag as generated room entity
        
        return wall
    
    def _create_wall_with_doorway(self, center, direction, thickness, color, door_size):
        """Create a wall with a doorway in the middle"""
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
            
            left_wall.is_generated_room = True  # Tag as generated room entity
            
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
            
            right_wall.is_generated_room = True  # Tag as generated room entity
            
            # Add variations and glow
            for wall_ent in [left_wall, right_wall]:
                wall_ent.scale += Vec3(random.uniform(-0.05, 0.05), random.uniform(-0.05, 0.05), random.uniform(-0.05, 0.05))
                wall_ent.color = wall_ent.color.tint(random.uniform(-0.03, 0.03))
                
                glow = Entity(
                    model='cube',
                    parent=wall_ent,
                    scale=wall_ent.scale * 1.03,
                    color=(255, 240, 220, 30),
                    unlit=True
                )
                
                glow.is_generated_room = True  # Tag as generated room entity
        
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
            
            top_wall.is_generated_room = True  # Tag as generated room entity
            
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
            
            bottom_wall.is_generated_room = True  # Tag as generated room entity
            
            # Add variations and glow
            for wall_ent in [top_wall, bottom_wall]:
                wall_ent.scale += Vec3(random.uniform(-0.05, 0.05), random.uniform(-0.05, 0.05), random.uniform(-0.05, 0.05))
                wall_ent.color = wall_ent.color.tint(random.uniform(-0.03, 0.03))
                
                glow = Entity(
                    model='cube',
                    parent=wall_ent,
                    scale=wall_ent.scale * 1.03,
                    color=(255, 240, 220, 30),
                    unlit=True
                )
                
                glow.is_generated_room = True  # Tag as generated room entity
    
    def _add_room_decorations(self, center, room_type):
        """Add room-specific decorations"""
        if room_type in ['liminal', 'chaotic', 'distorted']:
            # Add more decorations for liminal/chaotic rooms
            for _ in range(random.randint(1, 3)):
                if random.random() < 0.7:  # 70% chance of decoration
                    self._add_random_decoration(center, room_type)
        else:
            # Normal rooms have fewer decorations
            if random.random() < 0.4:  # 40% chance of decoration
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
            decoration_types = ['chair', 'table', 'plant', 'light', 'strange_object']
        else:
            decoration_types = ['chair', 'table', 'plant', 'light']
        
        decoration_type = random.choice(decoration_types)
        
        if decoration_type == 'chair':
            decoration = Entity(
                model='cube',
                scale=(0.8, 0.8, 0.8),
                position=position,
                color=LIMINAL_BEIGE.tint(-0.2),
                collider='box'
            )
        elif decoration_type == 'table':
            decoration = Entity(
                model='cube',
                scale=(1.5, 0.2, 1.0),
                position=position + Vec3(0, 0.4, 0),
                color=LIMINAL_BEIGE.tint(-0.3),
                collider='box'
            )
        elif decoration_type == 'plant':
            decoration = Entity(
                model='cube',
                scale=(0.5, 1.2, 0.5),
                position=position,
                color=color.green.tint(-0.3),
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
        
        # Tag the decoration as a generated room entity
        decoration.is_generated_room = True  # Tag as generated room entity


class LiminalPlayer(GameObject):
    """Enhanced player using the OOP framework"""
    def __init__(self, **kwargs):
        super().__init__(name="Player")
        
        # Create the underlying ursina entity
        self.entity = Entity(
            model='cube',
            y=1.0,
            origin_y=-0.5,
            color=LIMINAL_AMBER.tint(0.3),
            gravity=1.0
        )
        
        # Add FPS controller component
        self.fps_controller = FPSController(speed=6, jump_height=2.0, gravity=1.0)
        self.add_component(self.fps_controller)
        
        # Player properties
        self.moved_recently = False
        self.move_timer = 0
        self.base_height = 1.0
        self.floating = False
        self.float_speed = 1.5
        self.float_amount = 0.05
        self.reality_state = RealityState.STABLE
        self.speed_multiplier = 1.0
        
        # Movement stats
        self.distance_traveled = 0
        self.time_in_reality = 0
        self.last_position = self.entity.position
        
        # UI Elements
        self.cursor = Entity(parent=camera.ui, model='circle', color=LIMINAL_AMBER, scale=0.02)
        self.ammo_text = Text(
            text=f'Ammo: {self.fps_controller.ammo}',
            position=(-0.85, 0.45),
            origin=(-0.5, 0),
            scale=1.5,
            color=color.white
        )
        self.health_text = Text(
            text=f'Health: {self.fps_controller.health}',
            position=(-0.85, 0.4),
            origin=(-0.5, 0),
            scale=1.5,
            color=color.white
        )
    
    def update(self, dt):
        super().update(dt)
        
        # Store previous position for movement detection
        prev_position = self.entity.position
        
        # Update physics first via FPS controller
        # The FPS controller handles movement internally
        
        # Calculate distance traveled
        distance_moved = (self.entity.position - prev_position).length()
        self.distance_traveled += distance_moved
        
        # Track movement for reality stability
        if distance_moved > 0.1:
            self.moved_recently = True
            self.move_timer = 0
        else:
            self.move_timer += dt
            if self.move_timer > 3.0:  # Increased timeout
                self.moved_recently = False
        
        # Apply floating effect
        float_offset = math.sin(time.time() * self.float_speed) * self.float_amount
        self.entity.y = self.base_height + float_offset
        
        # Update reality state
        self.reality_state = reality.state
        
        # Keep player at ground level
        self.entity.y = max(0.9, self.entity.y)
        
        # Update time in reality
        self.time_in_reality += dt
        
        # Update UI
        self.ammo_text.text = f'Ammo: {self.fps_controller.ammo}'
        self.health_text.text = f'Health: {self.fps_controller.health}'
        
        # Update transform
        self.transform.position = self.entity.position


class EnemyManager:
    """Manages enemy AI instances"""
    def __init__(self):
        self.enemies = []
        self.ai_team_manager = AITeamManager()
    
    def create_enemy(self, enemy_type, position, ai_behavior=AIBehavior.AGGRESSIVE):
        """Create a new enemy with AI"""
        # Create the ursina entity for the enemy
        enemy_entity = Entity(
            model='cube',
            scale=(1, 2, 1),
            position=position,
            color=color.light_gray,
            collider='box'
        )
        
        # Create the enemy game object
        enemy_obj = GameObject(name=f"Enemy_{len(self.enemies)}")
        enemy_obj.entity = enemy_entity
        
        # Add AI component
        enemy_ai = EnemyAI(ai_behavior=ai_behavior, detection_range=15.0, attack_range=3.0)
        enemy_obj.add_component(enemy_ai)
        
        # Add to manager
        self.enemies.append(enemy_obj)
        self.ai_team_manager.add_enemy_to_team(enemy_ai, "enemies")
        
        return enemy_obj
    
    def update_all(self, dt):
        """Update all enemies"""
        self.ai_team_manager.update_all(dt)
        
        # Update visual representations
        for enemy in self.enemies:
            if hasattr(enemy, 'entity') and hasattr(enemy, 'transform'):
                # Sync entity position with transform
                enemy.entity.position = enemy.transform.position


class GameUI:
    """Game UI Manager"""
    def __init__(self):
        self.health_bar = None
        self.ammo_display = None
        self.minimap = None
        self.message_display = None
        
        # Create basic UI elements
        self.create_ui_elements()
    
    def create_ui_elements(self):
        """Create the basic UI elements"""
        # Health bar
        self.health_bar = Entity(
            parent=camera.ui,
            model='quad',
            scale=(0.4, 0.04),
            position=(-0.6, 0.45),
            color=color.red
        )
        
        # Ammo display
        self.ammo_display = Text(
            text='Ammo: 30',
            position=(-0.85, 0.45),
            origin=(-0.5, 0),
            scale=1.5,
            color=color.white
        )
    
    def update(self):
        """Update UI elements"""
        pass


# Initialize systems using our OOP framework
app = Ursina(borderless=False)

# Scene setup
scene.fog_color = LIMINAL_BEIGE.tint(-0.4)
scene.fog_density = 0.015

# Initialize game systems
reality = RealityDistortion()
world = BackroomsGenerator()

# Create player using our OOP framework
player = LiminalPlayer()

# Create enemy manager
enemy_manager = EnemyManager()

# Create enemies
for i in range(10):
    x = random.uniform(-20, 20)
    z = random.uniform(-20, 20)
    enemy_manager.create_enemy(
        "basic", 
        position=Vec3(x, 1, z), 
        ai_behavior=random.choice(list(AIBehavior))
    )

# Add starting room
world.generate_room(0, 0)
world.generated_positions.add((0, 0))

# Create game UI
game_ui = GameUI()


def input(key):
    """Handle input events"""
    if key == 'escape':
        application.quit()

    # Reality manipulation
    if key == 'tab':
        # Toggle reality distortion view
        if application.time_scale == 1.0:
            application.time_scale = 0.5
            scene.fog_density = 0.03
        else:
            application.time_scale = 1.0
            scene.fog_density = 0.015

    # Map switching
    if key == 'm':
        world.current_map_index = (world.current_map_index + 1) % len(world.map_files)
        world.load_map_from_file()
        print(f"Switched to map: {world.map_files[world.current_map_index] if world.map_files else 'Default'}")


def update():
    """Main update loop"""
    dt = time.dt
    
    # Update reality system
    reality.update(dt, player.moved_recently)
    
    # Generate world around player
    world.generate_around_player(player.entity.position)
    
    # Update player
    player.update(dt)
    
    # Update enemies
    enemy_manager.update_all(dt)
    
    # Update UI
    game_ui.update()
    
    # Reality distortion affects the whole scene
    if reality.distortion_level > 0:
        # Subtle screen distortion
        camera.x = math.sin(time.time() * 5) * reality.distortion_level * 0.02
        camera.z = math.cos(time.time() * 3) * reality.distortion_level * 0.02

        # Update fog based on reality state
        if reality.state == RealityState.CHAOTIC:
            scene.fog_color = LIMINAL_GRAY.tint(-0.3)
        elif reality.state == RealityState.LIMINAL:
            scene.fog_color = LIMINAL_AMBER.tint(-0.4)
        else:
            scene.fog_color = LIMINAL_BEIGE.tint(-0.4 + reality.distortion_level * 0.2)

        # Adjust fog density based on reality state
        scene.fog_density = 0.015 + reality.distortion_level * 0.01


# Configure window and start game
scene.background_color = LIMINAL_BEIGE.tint(-0.5)
window.title = 'Liminalcore Backrooms • Enhanced Experience (OOP)'
window.fps_counter.enabled = True
window.exit_button.visible = False

# Set window size
window.size = (1400, 900)
window.position = (50, 50)

# Start player in a hallway for better initial experience
player.entity.position = Vec3(0, 1.0, 0)

print("StubbornBackrooms • Psycho Dream (OOP Version)")
print("Controls:")
print("- WASD: Move")
print("- Mouse: Look around")
print("- Left Click: Shoot")
print("- Space: Jump")
print("- Tab: Reality distortion view")
print("- M: Switch maps")
print("- Esc: Quit")

app.run()