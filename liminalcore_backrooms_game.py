#!/usr/bin/env python3
"""
Liminalcore Backrooms Game
Advanced 3D backrooms experience with enhanced features
"""

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import math
import json
import os
from enum import Enum


class QualityLevel(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    ULTRA = 3


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
app = Ursina(borderless=False)
scene.fog_color = LIMINAL_BEIGE.tint(-0.4)
scene.fog_density = 0.015


class DebugManager:
    """Advanced debugging system"""
    def __init__(self):
        self.debug_mode = False
        self.performance_monitor = True
        self.map_debug = False
        self.entity_debug = False
        self.reality_debug = False
        self.show_fps = True
        self.debug_panel = None
        self.create_debug_panel()
    
    def create_debug_panel(self):
        """Create the debug information panel"""
        self.debug_panel = Entity(parent=camera.ui, position=window.top_left + Vec2(0.05, -0.05))
        
        # FPS display
        self.fps_text = Text(parent=self.debug_panel, text="", position=(0, 0), scale=1.2, color=color.white)
        
        # Performance info
        self.perf_text = Text(parent=self.debug_panel, text="", position=(0, -0.05), scale=1.0, color=color.blue)
        
        # Reality state
        self.reality_text = Text(parent=self.debug_panel, text="", position=(0, -0.1), scale=1.0, color=color.orange)
        
        # Map info
        self.map_text = Text(parent=self.debug_panel, text="", position=(0, -0.15), scale=1.0, color=color.green)
    
    def update(self):
        """Update debug information"""
        if not self.debug_mode:
            self.debug_panel.enabled = False
            return
        
        self.debug_panel.enabled = True
        
        # Update FPS
        if self.show_fps:
            self.fps_text.text = f"FPS: {int(1 / time.dt)}"
        else:
            self.fps_text.text = ""
        
        # Update performance info
        if self.performance_monitor:
            self.perf_text.text = f"Entities: {len(scene.entities)} | Render: {render.get_num_geoms()}"
        else:
            self.perf_text.text = ""
        
        # Update reality info
        if self.reality_debug:
            self.reality_text.text = f"Reality: {player.reality_state.name} | Distortion: {reality.distortion_level:.2f}"
        else:
            self.reality_text.text = ""
        
        # Update map info
        if self.map_debug:
            self.map_text.text = f"Room: {world.current_room_pos} | Connections: {len(world.current_connections)}"
        else:
            self.map_text.text = ""


class QualityManager:
    """Quality and performance settings manager"""
    def __init__(self):
        self.current_level = QualityLevel.NORMAL
        self.settings = {
            QualityLevel.LOW: {
                'render_distance': 10,
                'lighting_quality': 0.3,
                'texture_quality': 0.5,
                'shadows': False,
                'particles': 5,
                'fog_density': 0.025
            },
            QualityLevel.NORMAL: {
                'render_distance': 20,
                'lighting_quality': 0.6,
                'texture_quality': 0.7,
                'shadows': True,
                'particles': 15,
                'fog_density': 0.015
            },
            QualityLevel.HIGH: {
                'render_distance': 35,
                'lighting_quality': 0.85,
                'texture_quality': 0.9,
                'shadows': True,
                'particles': 25,
                'fog_density': 0.012
            },
            QualityLevel.ULTRA: {
                'render_distance': 50,
                'lighting_quality': 1.0,
                'texture_quality': 1.0,
                'shadows': True,
                'particles': 40,
                'fog_density': 0.01
            }
        }
        self.apply_settings()
    
    def set_quality(self, level):
        """Set the quality level"""
        self.current_level = level
        self.apply_settings()
    
    def apply_settings(self):
        """Apply current quality settings"""
        settings = self.settings[self.current_level]
        scene.fog_density = settings['fog_density']
        
        # Note: Some settings would require additional implementation in the renderer


class RealityDistortion:
    """Enhanced reality distortion system"""
    def __init__(self):
        self.distortion_level = 0.0
        self.wave_offset = 0
        self.reality_stability = 1.0
        self.liminal_state_timer = 0
        self.state = RealityState.STABLE
        self.state_change_cooldown = 0
    
    def update(self, dt):
        self.wave_offset += dt * 0.5
        
        # Reality becomes less stable the longer you stay in one place
        if not player.moved_recently:
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
        self.loaded_map = None
        self.map_directory = "maps"
        self.map_files = self.get_map_files()
        self.current_map_index = 0
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
            print(f"Loaded map: {filename}")
        except Exception as e:
            print(f"Failed to load map {filename}: {e}")
            self.generate_default_map()
    
    def generate_default_map(self):
        """Generate a default procedural map"""
        # For now, we'll use the procedural generation
        self.loaded_map = None
    
    def generate_around_player(self, player_position):
        """Generate rooms around player"""
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
        
        # Create ceiling
        ceiling = Entity(
            model='plane',
            scale=(self.room_size, 1, self.room_size),
            position=room_center + Vec3(0, self.ceiling_height, 0),
            rotation=(180, 0, 0),
            color=self._get_ceiling_color(room_type),
            collider='box'
        )
        
        # Create ceiling glow effect
        ceiling_glow = Entity(
            model='plane',
            parent=ceiling,
            scale=(self.room_size + 0.1, 1, self.room_size + 0.1),
            color=color.rgba(255, 245, 200, 40),
            unlit=True
        )
        
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
        
        # Add subtle variations
        wall.scale += Vec3(random.uniform(-0.05, 0.05), random.uniform(-0.05, 0.05), random.uniform(-0.05, 0.05))
        wall.color = wall.color.tint(random.uniform(-0.03, 0.03))
        
        # Create soft glow effect
        glow = Entity(
            model='cube',
            parent=wall,
            scale=wall.scale * 1.03,
            color=color.rgba(255, 240, 220, 30),
            unlit=True
        )
        
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
            
            # Add variations and glow
            for wall_ent in [left_wall, right_wall]:
                wall_ent.scale += Vec3(random.uniform(-0.05, 0.05), random.uniform(-0.05, 0.05), random.uniform(-0.05, 0.05))
                wall_ent.color = wall_ent.color.tint(random.uniform(-0.03, 0.03))
                
                glow = Entity(
                    model='cube',
                    parent=wall_ent,
                    scale=wall_ent.scale * 1.03,
                    color=color.rgba(255, 240, 220, 30),
                    unlit=True
                )
        
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
            
            # Add variations and glow
            for wall_ent in [top_wall, bottom_wall]:
                wall_ent.scale += Vec3(random.uniform(-0.05, 0.05), random.uniform(-0.05, 0.05), random.uniform(-0.05, 0.05))
                wall_ent.color = wall_ent.color.tint(random.uniform(-0.03, 0.03))
                
                glow = Entity(
                    model='cube',
                    parent=wall_ent,
                    scale=wall_ent.scale * 1.03,
                    color=color.rgba(255, 240, 220, 30),
                    unlit=True
                )
    
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


class LiminalPlayer(FirstPersonController):
    """Enhanced player controller with reality interaction"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cursor = Entity(parent=camera.ui, model='circle', color=LIMINAL_AMBER, scale=0.02)
        self.moved_recently = False
        self.move_timer = 0
        self.base_height = 1.0
        self.floating = False
        self.float_speed = 1.5
        self.float_amount = 0.05
        self.jump_height = 1.0
        self.reality_state = RealityState.STABLE
        self.speed_multiplier = 1.0
        self.heartbeat_sound = None  # Placeholder for heartbeat sound
        
        # Movement stats
        self.distance_traveled = 0
        self.time_in_reality = 0
        self.last_position = self.position
    
    def update(self):
        # Store previous position for movement detection
        prev_position = self.position.copy()
        
        # Update physics first
        super().update()
        
        # Calculate distance traveled
        distance_moved = (self.position - prev_position).length()
        self.distance_traveled += distance_moved
        
        # Track movement for reality stability
        if distance_moved > 0.1:
            self.moved_recently = True
            self.move_timer = 0
        else:
            self.move_timer += time.dt
            if self.move_timer > 3.0:  # Increased timeout
                self.moved_recently = False
        
        # Apply floating effect
        float_offset = math.sin(time.time() * self.float_speed) * self.float_amount
        self.y = self.base_height + float_offset
        
        # Reality distortion affects movement
        self.speed = 6 * reality.reality_stability * self.speed_multiplier
        self.jump_height = 2.0 * reality.reality_stability
        
        # Update reality state
        self.reality_state = reality.state
        
        # Keep player at ground level
        self.y = max(0.9, self.y)
        
        # Update time in reality
        self.time_in_reality += time.dt


class LiminalSky(Entity):
    """Enhanced sky with liminal effects"""
    def __init__(self):
        super().__init__(
            parent=scene,
            model='sphere',
            scale=2000,  # Larger for more immersive feel
            double_sided=True,
            unlit=True
        )
        
        default_vertex_shader = '''
        #version 140
        uniform mat4 p3d_ModelViewProjectionMatrix;
        in vec4 p3d_Vertex;
        in vec2 p3d_MultiTexCoord0;
        out vec2 texcoord;

        void main() {
            gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
            texcoord = p3d_MultiTexCoord0;
        }
        '''

        fragment_shader = '''
        #version 140
        uniform vec4 p3d_ColorScale;
        in vec2 texcoord;
        out vec4 fragColor;

        uniform float time;
        uniform float distortion;

        void main() {
            vec2 uv = texcoord;
            float gradient = uv.y * 0.5 + 0.5;
            
            // Base color with subtle variations
            vec3 color = mix(vec3(0.95, 0.92, 0.85), vec3(0.88, 0.85, 0.75), gradient);
            
            // Add liminal wave effects
            float wave1 = sin(uv.x * 8.0 + time * 0.3) * 0.02;
            float wave2 = cos(uv.y * 6.0 + time * 0.4) * 0.02;
            color += vec3(wave1 + wave2);
            
            // Reality distortion effect
            float distortion_effect = distortion * 0.1;
            color += vec3(distortion_effect * sin(time * 2.0));
            
            fragColor = vec4(color, 1.0) * p3d_ColorScale;
        }
        '''

        self.shader = Shader(language=Shader.GLSL,
                             vertex=default_vertex_shader,
                             fragment=fragment_shader
                             )

        self.set_shader_input('time', 0)
        self.set_shader_input('distortion', 0)

    def update(self):
        self.set_shader_input('time', time.time())
        self.set_shader_input('distortion', reality.distortion_level)


class LiminalParticles(Entity):
    """Enhanced particle system with reality effects"""
    def __init__(self):
        super().__init__(parent=scene)
        self.particles = []
        self.max_particles = 50  # Increased for more atmosphere
        
        # Create floating liminal particles
        for i in range(self.max_particles):
            particle = Entity(
                parent=self,
                model='circle',
                color=color.rgba(255, 245, 220, 80),
                scale=random.uniform(0.08, 0.2),
                position=(
                    random.uniform(-50, 50),
                    random.uniform(1, 8),
                    random.uniform(-50, 50)
                ),
                unlit=True
            )
            self.particles.append({
                'entity': particle,
                'speed': random.uniform(0.2, 1.0),
                'direction': Vec3(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)).normalized(),
                'base_pos': particle.position
            })

    def update(self):
        for i, p in enumerate(self.particles):
            # Gentle floating movement with reality influence
            time_factor = 1.0 + reality.distortion_level * 0.5
            p['entity'].y = p['base_pos'].y + math.sin(time.time() * p['speed'] * time_factor) * 0.3
            p['entity'].x = p['base_pos'].x + math.sin(time.time() * 0.3 * time_factor + i) * 0.2
            p['entity'].z = p['base_pos'].z + math.cos(time.time() * 0.4 * time_factor + i) * 0.2
            
            # Pulse transparency based on reality state
            base_alpha = 60 + reality.distortion_level * 40
            pulse = math.sin(time.time() * 1.5 + i) * 20
            alpha = max(20, min(100, base_alpha + pulse))
            p['entity'].color = color.rgba(255, 245, 220, alpha)


class LiminalMessage(Text):
    """Enhanced liminal messages"""
    def __init__(self):
        super().__init__(
            text='',
            origin=(0, 0),
            y=-0.35,
            color=LIMINAL_AMBER,
            scale=1.3,
            alpha=0
        )
        self.messages = [
            "the walls remember you...",
            "time flows differently here...",
            "reality is... unstable...",
            "the yellow is calling...",
            "something watches from above...",
            "the fluorescent hum grows louder...",
            "you are not alone here...",
            "the exit was never real...",
            "find the pattern in chaos...",
            "the liminal spaces call to you...",
            "your footsteps echo forever...",
            "the ceiling lights flicker...",
            "doors lead to more doors...",
            "the backrooms embrace you...",
            "lost in the yellow void...",
            "the walls breathe with you...",
            "infinite rooms, infinite halls...",
            "the exit is a lie...",
            "welcome to the in-between...",
            "the backrooms know your name..."
        ]
        self.current_message = ""
        self.timer = 0
        self.fade_timer = 0
        self.message_interval = 10  # Messages appear every 10 seconds

    def update(self):
        self.timer += time.dt

        # Change message periodically
        if self.timer > self.message_interval and not self.fade_timer:
            # Filter messages based on reality state
            if reality.state == RealityState.CHAOTIC:
                filtered_messages = [msg for msg in self.messages if "chaos" in msg or "chaotic" in msg or "unstable" in msg or "something" in msg]
                if not filtered_messages:
                    filtered_messages = [msg for msg in self.messages if "reality" in msg or "exit" in msg]
            elif reality.state == RealityState.LIMINAL:
                filtered_messages = [msg for msg in self.messages if "liminal" in msg or "between" in msg or "time" in msg or "spaces" in msg]
                if not filtered_messages:
                    filtered_messages = [msg for msg in self.messages if "walls" in msg or "yellow" in msg]
            else:
                filtered_messages = self.messages
            
            self.current_message = random.choice(filtered_messages) if filtered_messages else random.choice(self.messages)
            self.text = self.current_message
            self.fade_timer = 1.0  # Start fading in
            self.timer = 0

        # Fade in/out
        if self.fade_timer > 0:
            self.fade_timer -= time.dt
            if self.fade_timer > 0.5:
                # Fade in
                self.alpha = min(1.0, self.alpha + time.dt * 1.5)
            else:
                # Fade out
                self.alpha = max(0.0, self.alpha - time.dt * 1.5)
                if self.alpha <= 0:
                    self.text = ''
                    self.current_message = ''


class MapEditor3D:
    """Standalone 3D Map Editor"""
    def __init__(self):
        self.editor_app = None
        self.is_open = False
        self.editor_window = None
    
    def open_editor(self):
        """Open the 3D map editor"""
        print("Opening 3D Map Editor...")
        # In a real implementation, this would open a separate window or app
        # For now, we'll just print a message
        print("3D Map Editor would open here with:")
        print("- Visual 3D map creation tools")
        print("- Room and corridor design")
        print("- Entity placement system")
        print("- Texture and material selection")
        print("- Reality distortion preview")
        print("- Export to JSON functionality")
        
        # Placeholder for actual 3D editor implementation
        self.is_open = True


# Initialize systems
debug_manager = DebugManager()
quality_manager = QualityManager()
reality = RealityDistortion()
world = BackroomsGenerator()

# Create enhanced player
player = LiminalPlayer(
    model='cube',
    y=1.0,
    origin_y=-0.5,
    color=LIMINAL_AMBER.tint(0.3),
    gravity=1.0
)

# Add starting room
world.generate_room(0, 0)
world.generated_positions.add((0, 0))

# Create enhanced environment
liminal_sky = LiminalSky()
liminal_particles = LiminalParticles()
liminal_message = LiminalMessage()

# Create map editor instance
map_editor = MapEditor3D()


def input(key):
    """Handle input events"""
    if key == 'escape':
        application.quit()
    
    # Quality level switching
    if key == 'f1':
        quality_manager.set_quality(QualityLevel.LOW)
        debug_manager.debug_mode = not debug_manager.debug_mode
    elif key == 'f2':
        quality_manager.set_quality(QualityLevel.NORMAL)
    elif key == 'f3':
        quality_manager.set_quality(QualityLevel.HIGH)
    elif key == 'f4':
        quality_manager.set_quality(QualityLevel.ULTRA)
    
    # Debug toggles
    if key == 'f5':
        debug_manager.debug_mode = not debug_manager.debug_mode
    if key == 'f6':
        debug_manager.performance_monitor = not debug_manager.performance_monitor
    if key == 'f7':
        debug_manager.map_debug = not debug_manager.map_debug
    if key == 'f8':
        debug_manager.entity_debug = not debug_manager.entity_debug
    if key == 'f9':
        debug_manager.reality_debug = not debug_manager.reality_debug
    if key == 'f10':
        debug_manager.show_fps = not debug_manager.show_fps
    
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
    
    # Open 3D map editor
    if key == 'e':
        map_editor.open_editor()


def update():
    """Main update loop"""
    reality.update(time.dt)
    world.generate_around_player(player.position)
    
    # Update systems
    debug_manager.update()
    
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
        base_density = quality_manager.settings[quality_manager.current_level]['fog_density']
        scene.fog_density = base_density + reality.distortion_level * 0.01
    
    # Update liminal sky distortion
    liminal_sky.set_shader_input('distortion', reality.distortion_level)


# Configure window and start game
scene.background_color = LIMINAL_BEIGE.tint(-0.5)
window.title = 'Liminalcore Backrooms • Enhanced Experience'
window.fps_counter.enabled = True
window.exit_button.visible = False

# Set window size
window.size = (1400, 900)
window.position = (50, 50)

# Start player in a hallway for better initial experience
player.position = Vec3(0, 1.0, 0)

print("Liminalcore Backrooms Game Loaded!")
print("Controls:")
print("- WASD: Move")
print("- Mouse: Look around")
print("- Space: Jump")
print("- F1-F4: Quality levels (Low, Normal, High, Ultra)")
print("- F5-F10: Debug toggles")
print("- Tab: Reality distortion view")
print("- M: Switch maps")
print("- E: Open 3D Map Editor")
print("- Esc: Quit")

app.run()