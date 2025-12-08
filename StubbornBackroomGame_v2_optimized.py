#!/usr/bin/env python3
"""
StubbornBackroom: Psycho Dream - Optimized Version 2
High performance version with efficient map loading
"""

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import math
import json
import os
from enum import Enum


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
    """Lightweight debugging system"""
    def __init__(self):
        self.debug_mode = False
        self.show_fps = True
        self.debug_panel = None
        self.create_debug_panel()
    
    def create_debug_panel(self):
        """Create the debug information panel"""
        self.debug_panel = Entity(parent=camera.ui, position=window.top_left + Vec2(0.05, -0.05))
        
        # FPS display
        self.fps_text = Text(parent=self.debug_panel, text="", position=(0, 0), scale=1.2, color=color.white)
        
        # Map info
        self.map_text = Text(parent=self.debug_panel, text="", position=(0, -0.05), scale=1.0, color=color.green)
    
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
        
        # Update map info
        self.map_text.text = f"Map: {world.loaded_map_name}"


class RealityDistortion:
    """Optimized reality distortion system"""
    def __init__(self):
        self.distortion_level = 0.0
        self.reality_stability = 1.0
        self.state = RealityState.STABLE
        self.state_change_cooldown = 0
    
    def update(self, dt):
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


class BackroomsGenerator:
    """Highly optimized backrooms generator using only pre-made maps"""
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
        self.room_entities = {}  # Dictionary to track room entities by position
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
            for _ in range(random.randint(0, 2)):
                if random.random() < 0.5:  # 50% chance of decoration
                    self._add_random_decoration(center, room_type)
        else:
            # Normal rooms have fewer decorations
            if random.random() < 0.2:  # 20% chance of decoration
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
            decoration_types = ['chair', 'table', 'light', 'strange_object']
        else:
            decoration_types = ['chair', 'table', 'light']
        
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


class LiminalPlayer(FirstPersonController):
    """Optimized player controller with reality interaction"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cursor = Entity(parent=camera.ui, model='circle', color=LIMINAL_AMBER, scale=0.02)
        self.moved_recently = False
        self.move_timer = 0
        self.base_height = 1.0
        self.reality_state = RealityState.STABLE
        self.speed_multiplier = 1.0
        
        # Movement stats
        self.distance_traveled = 0
        self.time_in_reality = 0
        self.last_position = self.position
    
    def update(self):
        # Store previous position for movement detection
        prev_position = self.position
        
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
    """Simplified sky with liminal effects"""
    def __init__(self):
        super().__init__(
            parent=scene,
            model='sphere',
            scale=2000,  # Larger for more immersive feel
            double_sided=True,
            unlit=True
        )
        
        # Simplified shader for better performance
        simple_shader = '''
        #version 140
        uniform mat4 p3d_ModelViewProjectionMatrix;
        in vec4 p3d_Vertex;
        in vec2 p3d_MultiTexCoord0;
        out vec2 texcoord;
        
        uniform float time;
        uniform float distortion;

        void main() {
            gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
            texcoord = p3d_MultiTexCoord0;
            
            // Simplified color calculation
            vec2 uv = texcoord;
            float gradient = uv.y * 0.5 + 0.5;
            vec3 color = mix(vec3(0.95, 0.92, 0.85), vec3(0.88, 0.85, 0.75), gradient);
            
            // Add simple distortion effect
            color += vec3(distortion * 0.05);
            
            gl_FragColor = vec4(color, 1.0);
        }
        '''
        
        try:
            self.shader = Shader(vertex=Shader.Amplify, fragment=simple_shader)
        except:
            # If shader fails, use default color
            self.color = LIMINAL_BEIGE.tint(-0.3)

    def update(self):
        try:
            self.set_shader_input('time', time.time())
            self.set_shader_input('distortion', reality.distortion_level)
        except:
            pass  # Ignore shader errors


class LiminalParticles(Entity):
    """Optimized particle system with reality effects"""
    def __init__(self):
        super().__init__(parent=scene)
        self.particles = []
        self.max_particles = 15  # Reduced for better performance
        
        # Create floating liminal particles
        for i in range(self.max_particles):
            particle = Entity(
                parent=self,
                model='quad',
                color=color.rgba(255, 245, 220, 60),
                scale=random.uniform(0.05, 0.15),
                position=(
                    random.uniform(-20, 20),
                    random.uniform(1, 6),
                    random.uniform(-20, 20)
                ),
                unlit=True
            )
            self.particles.append({
                'entity': particle,
                'speed': random.uniform(0.1, 0.5),
                'base_pos': particle.position,
                'offset': random.uniform(0, 10)
            })

    def update(self):
        for i, p in enumerate(self.particles):
            # Gentle floating movement with reality influence
            time_factor = 1.0 + reality.distortion_level * 0.3
            p['entity'].y = p['base_pos'].y + math.sin(time.time() * p['speed'] * time_factor + p['offset']) * 0.2
            p['entity'].x = p['base_pos'].x + math.sin(time.time() * 0.2 * time_factor + i + p['offset']) * 0.1
            p['entity'].z = p['base_pos'].z + math.cos(time.time() * 0.3 * time_factor + i + p['offset']) * 0.1
            
            # Simple transparency pulse
            base_alpha = 50 + reality.distortion_level * 30
            pulse = math.sin(time.time() * 1.0 + i + p['offset']) * 15
            alpha = max(15, min(80, base_alpha + pulse))
            p['entity'].color = color.rgba(255, 245, 220, alpha)


class LiminalMessage(Text):
    """Optimized liminal messages"""
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
            "you are not alone here...",
            "find the pattern in chaos...",
            "the liminal spaces call to you...",
            "infinite rooms, infinite halls...",
            "welcome to the in-between..."
        ]
        self.current_message = ""
        self.timer = 0
        self.fade_timer = 0
        self.message_interval = 15  # Messages appear every 15 seconds

    def update(self):
        self.timer += time.dt

        # Change message periodically
        if self.timer > self.message_interval and self.fade_timer <= 0:
            # Filter messages based on reality state
            if reality.state == RealityState.CHAOTIC:
                filtered_messages = [msg for msg in self.messages if "chaos" in msg or "unstable" in msg or "something" in msg]
                if not filtered_messages:
                    filtered_messages = [msg for msg in self.messages if "reality" in msg]
            elif reality.state == RealityState.LIMINAL:
                filtered_messages = [msg for msg in self.messages if "liminal" in msg or "between" in msg or "spaces" in msg]
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
                self.alpha = min(1.0, self.alpha + time.dt * 1.0)
            else:
                # Fade out
                self.alpha = max(0.0, self.alpha - time.dt * 1.0)
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
        print("3D Map Editor would open here with:")
        print("- Visual 3D map creation tools")
        print("- Room and corridor design")
        print("- Entity placement system")
        print("- Reality distortion preview")
        print("- Export to JSON functionality")
        self.is_open = True


# Initialize systems
debug_manager = DebugManager()
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
    
    # Debug toggles
    if key == 'f5':
        debug_manager.debug_mode = not debug_manager.debug_mode
    
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
        print(f"Switched to map: {world.map_files[world.current_map_index]}")
    
    # Open 3D map editor
    if key == 'e':
        map_editor.open_editor()


def update():
    """Main update loop"""
    reality.update(time.dt)
    
    # Update systems
    debug_manager.update()
    
    # Reality distortion affects the whole scene
    if reality.distortion_level > 0:
        # Subtle screen distortion
        camera.x = math.sin(time.time() * 5) * reality.distortion_level * 0.01
        camera.z = math.cos(time.time() * 3) * reality.distortion_level * 0.01
        
        # Update fog based on reality state
        if reality.state == RealityState.CHAOTIC:
            scene.fog_color = LIMINAL_GRAY.tint(-0.3)
        elif reality.state == RealityState.LIMINAL:
            scene.fog_color = LIMINAL_AMBER.tint(-0.4)
        else:
            scene.fog_color = LIMINAL_BEIGE.tint(-0.4 + reality.distortion_level * 0.2)
        
        # Adjust fog density based on reality state
        scene.fog_density = 0.015 + reality.distortion_level * 0.01
    
    # Update liminal sky distortion
    try:
        liminal_sky.set_shader_input('distortion', reality.distortion_level)
    except:
        pass  # Ignore shader errors


# Configure window and start game
scene.background_color = LIMINAL_BEIGE.tint(-0.5)
window.title = 'Liminalcore Backrooms • Enhanced Experience (Optimized v2)'
window.fps_counter.enabled = True
window.exit_button.visible = False

# Set window size
window.size = (1400, 900)
window.position = (50, 50)

# Start player in a hallway for better initial experience
player.position = Vec3(0, 1.0, 0)

print("StubbornBackrooms • Psycho Dream - Optimized Version 2")
print("Controls:")
print("- WASD: Move")
print("- Mouse: Look around")
print("- Space: Jump")
print("- F5: Toggle debug info")
print("- Tab: Reality distortion view")
print("- M: Switch maps")
print("- E: Open 3D Map Editor")
print("- Esc: Quit")

app.run()