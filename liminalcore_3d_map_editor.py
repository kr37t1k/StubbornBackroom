#!/usr/bin/env python3
"""
Standalone 3D Map Editor for StubbornBackroom Game
"""
# its not working - remove
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader, basic_lighting_shader
import json
import os
from enum import Enum


# 🔧 Enhanced Editor Configuration
class EditorMode(Enum):
    BUILD = 0  # Place/remove walls, floors
    EDIT = 1  # Modify existing structures
    ENTITY = 2  # Place game entities
    PAINT = 3  # Paint textures/colors

# 🎮 SIMPLE NOCLIP CAMERA (tested and working)
class NoClipCamera(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Basic settings
        self.speed = 6
        self.sensitivity = 20
        self.position = Vec3(0, 2, 0)
        self.rotation = Vec3(0, 0, 0)

        # Input state
        self.keys = {'forward': False, 'backward': False,
                     'left': False, 'right': False,
                     'up': False, 'down': False}

        # Mouse state
        self.mouse_enabled = True
        mouse.locked = True

    def update(self):
        # Mouse look (only if enabled)
        if self.mouse_enabled:
            self.rotation_y += mouse.velocity[0] * self.sensitivity
            self.rotation_x -= mouse.velocity[1] * self.sensitivity
            self.rotation_x = clamp(self.rotation_x, -90, 90)

        # Calculate movement direction
        direction = Vec3(
            self.forward * (self.keys['forward'] - self.keys['backward']) +
            self.right * (self.keys['right'] - self.keys['left'])
        ).normalized()

        # Apply movement
        self.position += direction * self.speed * time.dt

        # Vertical movement
        if self.keys['up']:
            self.y += self.speed * time.dt
        if self.keys['down']:
            self.y -= self.speed * time.dt

        # Update camera position smoothly
        camera.position = self.position
        camera.rotation = self.rotation

    def input(self, key):
        # Movement keys
        if key == 'w': self.keys['forward'] = True
        if key == 's': self.keys['backward'] = True
        if key == 'a': self.keys['left'] = True
        if key == 'd': self.keys['right'] = True
        if key == 'space': self.keys['up'] = True
        if key == 'shift': self.keys['down'] = True

        if key == 'w up': self.keys['forward'] = False
        if key == 's up': self.keys['backward'] = False
        if key == 'a up': self.keys['left'] = False
        if key == 'd up': self.keys['right'] = False
        if key == 'space up': self.keys['up'] = False
        if key == 'shift up': self.keys['down'] = False

        # Toggle mouse lock
        if key == 'f':
            self.mouse_enabled = not self.mouse_enabled
            mouse.locked = self.mouse_enabled
            print(f"Mouse: {'Locked' if mouse.locked else 'Unlocked'}")


# 🎯 MINIMAL WORKING EDITOR (no complex code, just basics)
class SimpleMapEditor:
    def __init__(self):
        self.app = Ursina()

        # Create simple scene
        self.create_scene()

        # Simple noclip camera (working version)
        self.editor_camera = NoClipCamera()

        # Basic UI
        self.create_ui()

        # Input
        self.bind_input()

        print("🎮 NoClip Editor Ready!")
        print("• WASD: Move  • Mouse: Look")
        print("• SPACE/SHIFT: Up/Down  • F: Toggle Mouse")

    def create_scene(self):
        # Simple ground
        Entity(
            model='plane',
            scale=64,
            texture='grass',
            collider='box'
        )

        # Some walls to edit
        for i in range(5):
            Entity(
                model='cube',
                position=(i * 3, 1, 5),
                scale=(2, 2, 2),
                color=color.gray,
                collider='box'
            )

        # Lighting
        DirectionalLight(shadows=True)
        Sky()

    def create_ui(self):
        # Simple mode button
        self.mode_btn = Button(
            text='BUILD MODE',
            position=(-0.8, 0.45),
            scale=(0.2, 0.05),
            color=color.blue
        )

        # Status text
        self.status = Text(
            text='NoClip Active',
            position=(-0.85, -0.45),
            scale=1.2
        )

    def bind_input(self):
        def input_handler(key):
            if key == 'left mouse down':
                self.place_block()
            elif key == 'right mouse down':
                self.remove_block()
            elif key == 'escape':
                self.app.quit()

        self.app.input_handler = input_handler

    def place_block(self):
        hit_info = raycast(
            self.editor_camera.position,
            self.editor_camera.forward,
            distance=10
        )

        if hit_info.hit:
            new_pos = hit_info.world_point + hit_info.normal * 0.5
            Entity(
                model='cube',
                position=new_pos,
                scale=0.9,
                color=color.orange,
                collider='box'
            )
            self.status.text = 'Block placed!'

    def remove_block(self):
        hit_info = raycast(
            self.editor_camera.position,
            self.editor_camera.forward,
            distance=10
        )

        if hit_info.hit and hit_info.entity != self:
            destroy(hit_info.entity)
            self.status.text = 'Block removed!'

    def run(self):
        self.app.run()


# 🚀 RUN IT
# if __name__ == "__main__":
#     editor = SimpleMapEditor()
#     editor.run()

class OptimizedMapEditor:
    def __init__(self):
        # 🚀 Performance settings
        application.development_mode = True
        window.title = "StubbornBackroom: 3D Map Editor"
        window.borderless = False

        # Initialize Ursina
        self.app = Ursina(
            vsync=True,
            fullscreen=False,
            size=(1280, 720)
        )

        # Editor state
        self.mode = EditorMode.BUILD
        self.current_tool = "wall"
        self.current_entity_type = "chair"
        self.is_running = True
        self.chunk_size = 16  # For chunk loading
        self.loaded_chunks = {}

        # Map data
        self.map_data = {
            "width": 32,  # Increased for larger maps
            "height": 32,
            "seed": 42,
            "start_pos": [1, 1],
            "end_pos": [30, 30],
            "map": [],
            "entities": [],
            "chunks": {}  # Chunk-based storage
        }

        # Performance optimization
        self.grid_entities = []
        self.entity_objects = []
        self.room_size = 4.0
        self.wall_height = 3.0
        self.visualization_distance = 20.0  # Only render nearby chunks

        # Create initial map
        self.create_empty_map()

        # Setup scene with optimizations
        self.setup_scene()

        # Create UI
        self.create_ui()

        # Bind input
        self.bind_input()

        # Performance info
        self.performance_text = Text(
            text="",
            position=(-0.85, 0.45),
            scale=0.8,
            color=color.white33
        )

    def create_empty_map(self):
        """Create empty map with optimized chunk structure"""
        # Initialize map as chunks
        self.map_data["chunks"] = {}

        # Create border walls
        for x in range(self.map_data["width"]):
            self.set_cell(x, 0, 1)  # Top border
            self.set_cell(x, self.map_data["height"] - 1, 1)  # Bottom border

        for y in range(self.map_data["height"]):
            self.set_cell(0, y, 1)  # Left border
            self.set_cell(self.map_data["width"] - 1, y, 1)  # Right border

        # Clear existing entities
        self.clear_entities()

        # Generate visual map (optimized)
        self.generate_visual_map()

    def clear_entities(self):
        """Optimized entity cleanup"""
        # Use destroy() with delay for better performance
        for entity in self.grid_entities:
            destroy(entity, delay=0.01)
        for entity in self.entity_objects:
            destroy(entity, delay=0.01)

        self.grid_entities.clear()
        self.entity_objects.clear()

    def get_chunk_key(self, x, z):
        """Get chunk coordinates for position"""
        chunk_x = x // self.chunk_size
        chunk_z = z // self.chunk_size
        return (chunk_x, chunk_z)

    def set_cell(self, x, z, cell_type):
        """Set cell value in chunk-based storage"""
        if 0 <= x < self.map_data["width"] and 0 <= z < self.map_data["height"]:
            chunk_key = self.get_chunk_key(x, z)
            if chunk_key not in self.map_data["chunks"]:
                self.map_data["chunks"][chunk_key] = {}

            local_x = x % self.chunk_size
            local_z = z % self.chunk_size
            self.map_data["chunks"][chunk_key][(local_x, local_z)] = cell_type

    def get_cell(self, x, z):
        """Get cell value from chunk-based storage"""
        if 0 <= x < self.map_data["width"] and 0 <= z < self.map_data["height"]:
            chunk_key = self.get_chunk_key(x, z)
            if chunk_key in self.map_data["chunks"]:
                local_x = x % self.chunk_size
                local_z = z % self.chunk_size
                return self.map_data["chunks"][chunk_key].get((local_x, local_z), 0)
        return 0

    def generate_visual_map(self):
        """Optimized visual generation with chunk loading"""
        self.clear_entities()

        # Get camera position for distance-based rendering
        cam_pos = self.editor_camera.position if hasattr(self, 'editor_camera') else Vec3(0, 5, 0)

        # Generate chunks within visualization distance
        for chunk_key in list(self.map_data["chunks"].keys()):
            chunk_x, chunk_z = chunk_key
            world_x = chunk_x * self.chunk_size * self.room_size
            world_z = chunk_z * self.chunk_size * self.room_size

            # Distance from camera
            distance = (Vec3(world_x, 0, world_z) - Vec3(cam_pos.x, 0, cam_pos.z)).length()

            if distance <= self.visualization_distance:
                self.generate_chunk(chunk_key)

        # Generate entities
        self.create_entity_objects()

    def generate_chunk(self, chunk_key):
        """Generate a single chunk"""
        chunk_x, chunk_z = chunk_key

        for local_x in range(self.chunk_size):
            for local_z in range(self.chunk_size):
                x = chunk_x * self.chunk_size + local_x
                z = chunk_z * self.chunk_size + local_z

                if x >= self.map_data["width"] or z >= self.map_data["height"]:
                    continue

                cell_type = self.get_cell(x, z)

                # Create floor
                floor_y = 0
                floor_color = self.get_floor_color(cell_type)

                floor = Entity(
                    model='plane',
                    scale=(self.room_size, 1, self.room_size),
                    position=Vec3(x * self.room_size, floor_y, z * self.room_size),
                    color=floor_color,
                    collider='box',
                    texture='white_cube',
                    texture_scale=(1, 1),
                    shader=basic_lighting_shader
                )
                self.grid_entities.append(floor)

                # Create walls/doors
                if cell_type == 1:  # Wall
                    wall = Entity(
                        model='cube',
                        scale=(self.room_size, self.wall_height, 0.5),
                        position=Vec3(x * self.room_size, self.wall_height / 2,
                                      z * self.room_size + self.room_size / 2),
                        color=color.gray.tint(-0.2),
                        collider='box',
                        shader=basic_lighting_shader
                    )
                    self.grid_entities.append(wall)

                elif cell_type == 2:  # Door
                    door = Entity(
                        model='cube',
                        scale=(self.room_size * 0.8, self.wall_height * 0.8, 0.3),
                        position=Vec3(x * self.room_size, self.wall_height / 2, z * self.room_size),
                        color=color.brown.tint(0.2),
                        collider='box',
                        shader=basic_lighting_shader
                    )
                    self.grid_entities.append(door)

    def get_floor_color(self, cell_type):
        """Get floor color based on cell type"""
        colors = {
            0: color.white.tint(-0.3),  # Path
            1: color.gray.tint(-0.4),  # Wall area
            2: color.brown.tint(-0.2),  # Door area
            3: color.orange.tint(-0.1)  # Special
        }
        return colors.get(cell_type, color.white.tint(-0.3))

    def create_entity_objects(self):
        """Create entity objects with optimizations"""
        for entity_data in self.map_data["entities"]:
            x = entity_data["x"]
            z = entity_data["z"]
            y = entity_data.get("y", 0)
            entity_type = entity_data["type"]

            # Create entity with level-of-detail
            scale_mult = 1.0
            entity_obj = None

            if entity_type == "chair":
                entity_obj = Entity(
                    model='cube',
                    scale=(0.8 * scale_mult, 0.8 * scale_mult, 0.8 * scale_mult),
                    position=Vec3(x * self.room_size, y + 0.4, z * self.room_size),
                    color=color.blue.tint(-0.2),
                    collider='box',
                    shader=basic_lighting_shader
                )
            elif entity_type == "table":
                entity_obj = Entity(
                    model='cube',
                    scale=(1.2 * scale_mult, 0.2 * scale_mult, 1.0 * scale_mult),
                    position=Vec3(x * self.room_size, y + 0.1, z * self.room_size),
                    color=color.brown.tint(0.1),
                    collider='box',
                    shader=basic_lighting_shader
                )
            elif entity_type == "plant":
                entity_obj = Entity(
                    model='cube',
                    scale=(0.5 * scale_mult, 1.0 * scale_mult, 0.5 * scale_mult),
                    position=Vec3(x * self.room_size, y + 0.5, z * self.room_size),
                    color=color.green.tint(0.2),
                    collider='box',
                    shader=basic_lighting_shader
                )
            elif entity_type == "light":
                entity_obj = Entity(
                    model='cube',
                    scale=(0.3 * scale_mult, 0.1 * scale_mult, 0.3 * scale_mult),
                    position=Vec3(x * self.room_size, y + 2.0, z * self.room_size),
                    color=color.yellow.tint(0.3),
                    unlit=True,
                    collider='box'
                )
            else:  # Default
                entity_obj = Entity(
                    model='cube',
                    scale=(0.6 * scale_mult, 0.6 * scale_mult, 0.6 * scale_mult),
                    position=Vec3(x * self.room_size, y + 0.3, z * self.room_size),
                    color=color.red.tint(-0.2),
                    collider='box',
                    shader=basic_lighting_shader
                )

            if entity_obj:
                self.entity_objects.append(entity_obj)

    def setup_scene(self):
        """Optimized scene setup"""
        # Lighting - optimized for performance
        sun = DirectionalLight(shadows=True, shadow_map_resolution=(1024, 1024))
        sun.color = color.white
        sun.rotation = (45, -45, 0)

        # Ambient lighting
        ambient = AmbientLight(color=color.rgba(80, 80, 100, 0.3))

        # Fog for depth
        scene.fog_color = color.gray.tint(-0.3)
        scene.fog_density = 0.01

        # Sky
        Sky(texture='sky_sunset')

        # NoClip camera (optimized)
        self.editor_camera = NoClipCamera()
        camera.parent = self.editor_camera
        camera.fov = 80

        # Grid helper
        self.create_grid_helper()

    def create_grid_helper(self):
        """Create performance-optimized grid helper"""
        # Only create grid lines every 5 units
        spacing = 5
        size = 100

        for i in range(-size, size + spacing, spacing):
            # X lines
            Entity(
                model='quad',
                scale=(0.05, 0.05, size * 2),
                position=(i, 0.01, 0),
                rotation=(90, 0, 0),
                color=color.rgba(200, 200, 255, 30),
                unlit=True
            )
            # Z lines
            Entity(
                model='quad',
                scale=(size * 2, 0.05, 0.05),
                position=(0, 0.01, i),
                rotation=(90, 0, 90),
                color=color.rgba(200, 200, 255, 30),
                unlit=True
            )

    def create_ui(self):
        """Enhanced UI with performance indicators"""
        # Mode selection (optimized buttons)
        mode_buttons = []
        mode_colors = {
            EditorMode.BUILD: color.blue,
            EditorMode.EDIT: color.green,
            EditorMode.ENTITY: color.orange,
            EditorMode.PAINT: color.cyan
        }

        for i, (mode, color_val) in enumerate(mode_colors.items()):
            btn = Button(
                text=f'{mode.name.capitalize()}',
                position=window.top_left + Vec2(0.05, -0.05 - i * 0.06),
                scale=(0.12, 0.04),
                color=color_val,
                highlight_color=color_val.tint(0.2)
            )
            btn.on_click = lambda m=mode: self.set_mode(m)
            mode_buttons.append(btn)

        # Tool selector
        self.tool_label = Text(
            text=f'Current Tool: {self.current_tool.capitalize()}',
            position=window.top_left + Vec2(0.25, -0.05),
            scale=1.2,
            color=color.white
        )

        # Performance monitor
        self.perf_btn = Button(
            text='📊',
            position=window.top_right + Vec2(-0.05, -0.05),
            scale=(0.04, 0.04),
            color=color.gray
        )
        self.perf_btn.on_click = self.toggle_performance_info

        # File operations
        file_btns = [
            ('💾 Save', lambda: self.save_map(), color.green),
            ('📥 Load', lambda: self.load_map(), color.blue),
            ('🆕 New', lambda: self.create_empty_map(), color.red),
            ('🔄 Refresh', lambda: self.generate_visual_map(), color.yellow)
        ]

        for i, (text, func, color_val) in enumerate(file_btns):
            btn = Button(
                text=text,
                position=window.top_right + Vec2(-0.25, -0.05 - i * 0.05),
                scale=(0.08, 0.04),
                color=color_val,
                highlight_color=color_val.tint(0.2)
            )
            btn.on_click = func
            mode_buttons.append(btn)

        # Entity selector (visible only in entity mode)
        self.entity_selector = Slider(
            min=0,
            max=4,
            default=0,
            position=window.top_left + Vec2(0.25, -0.12),
            scale=(0.15, 0.02),
            dynamic=True,
            visible=False
        )
        self.entity_selector.on_value_changed = self.on_entity_type_change

        self.entity_type_text = Text(
            text=f'Entity: {self.current_entity_type.capitalize()}',
            position=window.top_left + Vec2(0.25, -0.15),
            scale=1.0,
            color=color.white,
            visible=False
        )

        # Status bar
        self.status_text = Text(
            text='Ready • NoClip Camera Active',
            position=window.bottom_left + Vec2(0.02, 0.02),
            scale=1.0,
            color=color.white
        )

    def toggle_performance_info(self):
        """Toggle performance information display"""
        self.performance_text.enabled = not self.performance_text.enabled

    def set_mode(self, mode):
        """Set editor mode with UI update"""
        self.mode = mode
        mode_names = {
            EditorMode.BUILD: "Build",
            EditorMode.EDIT: "Edit",
            EditorMode.ENTITY: "Entity",
            EditorMode.PAINT: "Paint"
        }
        self.tool_label.text = f'Editor Mode: {mode_names[mode]}'

        # Update UI visibility
        is_entity_mode = (mode == EditorMode.ENTITY)
        self.entity_selector.visible = is_entity_mode
        self.entity_type_text.visible = is_entity_mode

        # Update status
        self.status_text.text = f'{mode_names[mode]} Mode Active • Use WASD+Mouse to navigate'

    def on_entity_type_change(self):
        """Handle entity type change"""
        entity_types = ["chair", "table", "plant", "light", "door"]
        idx = int(self.entity_selector.value)
        if 0 <= idx < len(entity_types):
            self.current_entity_type = entity_types[idx]
            self.entity_type_text.text = f'Entity: {self.current_entity_type.capitalize()}'

    def bind_input(self):
        """Optimized input binding"""

        def input_handler(key):
            if key == 'left mouse down':
                self.handle_mouse_click()
            elif key == 'right mouse down':
                self.handle_right_click()
            elif key == 'escape':
                self.app.quit()
            elif key == 'f1':
                # Cycle through modes
                modes = list(EditorMode)
                current_idx = modes.index(self.mode)
                next_idx = (current_idx + 1) % len(modes)
                self.set_mode(modes[next_idx])
            elif key == 'f2':
                # Toggle grid helper
                for entity in scene.entities:
                    if hasattr(entity, 'unlit') and entity.unlit and entity.color.a == 30:
                        entity.enabled = not entity.enabled

        self.app.input_handler = input_handler

    def handle_mouse_click(self):
        """Optimized mouse click handling"""
        hit_info = raycast(
            self.editor_camera.position,
            self.editor_camera.forward,
            distance=50,
            ignore=(self.editor_camera,)
        )

        if hit_info.hit:
            # Calculate grid position
            grid_x = round(hit_info.world_point.x / self.room_size)
            grid_z = round(hit_info.world_point.z / self.room_size)

            # Boundary check
            if 0 <= grid_x < self.map_data["width"] and 0 <= grid_z < self.map_data["height"]:
                if self.mode == EditorMode.BUILD:
                    # Toggle based on current tool
                    tool_mapping = {"wall": 1, "door": 2, "special": 3, "floor": 0}
                    new_type = tool_mapping.get(self.current_tool, 0)
                    self.set_cell(grid_x, grid_z, new_type)
                    self.generate_visual_map()
                    self.status_text.text = f'Placed {self.current_tool} at ({grid_x}, {grid_z})'

                elif self.mode == EditorMode.ENTITY:
                    # Add/remove entity
                    existing_idx = None
                    for i, entity in enumerate(self.map_data["entities"]):
                        if int(entity["x"]) == grid_x and int(entity["z"]) == grid_z:
                            existing_idx = i
                            break

                    if existing_idx is not None:
                        del self.map_data["entities"][existing_idx]
                        self.status_text.text = f'Removed entity at ({grid_x}, {grid_z})'
                    else:
                        self.map_data["entities"].append({
                            "type": self.current_entity_type,
                            "x": float(grid_x),
                            "y": 0.0,
                            "z": float(grid_z)
                        })
                        self.status_text.text = f'Added {self.current_entity_type} at ({grid_x}, {grid_z})'

                    self.create_entity_objects()

    def handle_right_click(self):
        """Optimized right click handling"""
        hit_info = raycast(
            self.editor_camera.position,
            self.editor_camera.forward,
            distance=50,
            ignore=(self.editor_camera,)
        )

        if hit_info.hit:
            grid_x = round(hit_info.world_point.x / self.room_size)
            grid_z = round(hit_info.world_point.z / self.room_size)

            if 0 <= grid_x < self.map_data["width"] and 0 <= grid_z < self.map_data["height"]:
                self.set_cell(grid_x, grid_z, 0)  # Set to floor
                self.generate_visual_map()
                self.status_text.text = f'Clear cell at ({grid_x}, {grid_z})'

    def save_map(self):
        """Save map with chunk optimization"""
        try:
            os.makedirs("maps", exist_ok=True)

            # Convert chunks to flat map for saving
            flat_map = []
            for y in range(self.map_data["height"]):
                row = []
                for x in range(self.map_data["width"]):
                    row.append(self.get_cell(x, y))
                flat_map.append(row)

            save_data = {
                "width": self.map_data["width"],
                "height": self.map_data["height"],
                "seed": self.map_data["seed"],
                "start_pos": self.map_data["start_pos"],
                "end_pos": self.map_data["end_pos"],
                "map": flat_map,
                "entities": self.map_data["entities"]
            }

            filename = f"maps/map_{len(os.listdir('maps')) if os.path.exists('maps') else 0}.json"
            with open(filename, 'w') as f:
                json.dump(save_data, f, indent=2)

            self.status_text.text = f'✅ Map saved: {filename}'
            print(f"Map saved to {filename}")

        except Exception as e:
            self.status_text.text = f'❌ Save error: {e}'
            print(f"Error saving map: {e}")

    def load_map(self):
        """Load map with performance optimizations"""
        try:
            # Look for map files
            map_files = []
            if os.path.exists("maps"):
                map_files = [f for f in os.listdir("maps") if f.endswith('.json')]

            if not map_files:
                self.status_text.text = '🆕 Creating new empty map'
                self.create_empty_map()
                return

            # Load most recent map
            latest_map = max(map_files, key=lambda f: os.path.getmtime(f"maps/{f}"))
            # filename = f"maps/{latest_map}"
            filename = f"maps/first_map_from_AdvancedMapEditor.json"

            with open(filename, 'r') as f:
                loaded_data = json.load(f)

            # Convert flat map to chunks
            self.map_data.update(loaded_data)
            self.map_data["chunks"] = {}

            # Convert to chunk format
            for z, row in enumerate(self.map_data["map"]):
                for x, cell_type in enumerate(row):
                    self.set_cell(x, z, cell_type)

            # Clear map array to save memory
            if "map" in self.map_data:
                del self.map_data["map"]

            self.generate_visual_map()
            self.status_text.text = f'✅ Loaded: {latest_map}'
            print(f"Map loaded from {filename}")

        except Exception as e:
            self.status_text.text = f'❌ Load error: {e}'
            print(f"Error loading map: {e}")
            self.create_empty_map()

    def update(self):
        """Performance monitoring"""
        if self.performance_text.enabled:
            entity_count = len(self.grid_entities) + len(self.entity_objects)
            chunk_count = len(self.loaded_chunks)
            fps = int(1 / time.dt) if time.dt > 0 else 0

            self.performance_text.text = f'FPS: {fps}\nEntities: {entity_count}\nChunks: {chunk_count}'

    def run(self):
        """Start the editor"""
        print("🎮 Liminalcore Map Editor Started")
        print("🔧 Controls:")
        print("• WASD: Move          • Mouse: Look")
        print("• SPACE/SHIFT: Fly    • TAB: Toggle Speed")
        print("• F: Toggle Mouse     • F1: Cycle Modes")
        print("• LMB: Place          • RMB: Remove")
        print("• ESC: Quit")

        self.app.run()


# Run the editor
if __name__ == "__main__":
    editor = OptimizedMapEditor()
    window.fps_counter.enabled = True
    editor.run()