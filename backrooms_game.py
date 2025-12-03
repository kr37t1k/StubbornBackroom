"""
Backrooms Game - Complete Panda3D Implementation
Based on GUIDE_PANDA3D.md with full OOP design, mouse/keyboard controls, and camera movement
"""
import math
import random
import noise
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from direct.task import Task
from direct.gui.DirectGui import *
import sys
import os
import json


class BackroomsWorld:
    """Procedural world generation system for the Backrooms"""
    def __init__(self, seed=None, level_file=None):
        if level_file:
            # Load from level file
            self.load_level_from_file(level_file)
        else:
            # Generate procedurally
            self.seed = seed or random.randint(0, 999999)
            random.seed(self.seed)
            self.chunk_size = 16
            self.loaded_chunks = {}
            self.visible_chunks = set()
            
            # Noise parameters for procedural generation
            self.scale = 10.0
            self.octaves = 4
            self.persistence = 0.5
            self.lacunarity = 2.0
            
            # Room types
            self.room_types = {
                0: 'empty',    # Empty space
                1: 'hallway',  # Narrow hallway
                2: 'room',     # Small room
                3: 'junction', # T-junction
                4: 'corner',   # Corner
                5: 'open',     # Open space
            }
            
            # Reality stability factors
            self.reality_stability = 1.0
            self.hallucination_level = 0.0
            
            # For procedural generation, store a grid representation
            self.grid = None

    def load_level_from_file(self, level_file):
        """Load level data from a JSON file."""
        with open(level_file, 'r') as f:
            self.level_data = json.load(f)
        
        self.width = self.level_data['width']
        self.height = self.level_data['height']
        self.grid = [row[:] for row in self.level_data['map']]  # Deep copy
        self.rooms = self.level_data.get('rooms', [])
        self.doors = self.level_data.get('doors', [])
        self.corridors = self.level_data.get('corridors', [])
        self.hazards = self.level_data.get('hazards', [])
        self.seed = self.level_data.get('seed', 0)
        
        # Set up other attributes
        self.chunk_size = 16
        self.loaded_chunks = {}
        self.visible_chunks = set()
        
        # Reality stability factors
        self.reality_stability = 1.0
        self.hallucination_level = 0.0

    def get_cell(self, x, y):
        """Get cell type at world coordinates"""
        if self.grid is not None:
            # Using loaded level data
            grid_x = int(x)
            grid_y = int(y)
            
            # Check if coordinates are within bounds
            if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
                # Convert tile types to our internal representation
                tile_type = self.grid[grid_y][grid_x]
                
                # Map tile types to our internal room types
                if tile_type == 0:  # Empty
                    return 0  # Empty space
                elif tile_type == 1:  # Wall
                    return 1  # Hallway (treated as wall in our system)
                elif tile_type == 2:  # Floor
                    return 0  # Empty space
                elif tile_type == 3:  # Door
                    return 0  # Empty space (passable)
                elif tile_type == 4:  # Corridor
                    return 1  # Hallway
                elif tile_type == 5:  # Room
                    return 2  # Room
                elif tile_type == 6:  # Hazard
                    return 0  # Empty space but with hazard effect
            else:
                return 1  # Treat out of bounds as wall/hallway
        else:
            # Use procedural generation
            # Convert to integer grid
            grid_x = int(x)
            grid_y = int(y)

            # Use Perlin noise for smooth transitions
            nx = grid_x / self.scale
            ny = grid_y / self.scale

            value = noise.pnoise2(
                nx, ny,
                octaves=self.octaves,
                persistence=self.persistence,
                lacunarity=self.lacunarity,
                repeatx=1024,
                repeaty=1024,
                base=self.seed
            )

            # Convert noise to room types
            if value < -0.6:
                return 1  # Hallway
            elif value < -0.2:
                return 2  # Room
            elif value < 0.2:
                return 3  # Junction
            elif value < 0.6:
                return 4  # Corner
            else:
                return 5  # Open space
        grid_x = int(x)
        grid_y = int(y)

        # Use Perlin noise for smooth transitions
        nx = grid_x / self.scale
        ny = grid_y / self.scale

        value = noise.pnoise2(
            nx, ny,
            octaves=self.octaves,
            persistence=self.persistence,
            lacunarity=self.lacunarity,
            repeatx=1024,
            repeaty=1024,
            base=self.seed
        )

        # Convert noise to room types
        if value < -0.6:
            return 1  # Hallway
        elif value < -0.2:
            return 2  # Room
        elif value < 0.2:
            return 3  # Junction
        elif value < 0.6:
            return 4  # Corner
        else:
            return 5  # Open space

    def generate_chunk(self, chunk_x, chunk_y):
        """Generate a single chunk using 3D noise"""
        chunk_node = NodePath(f"chunk_{chunk_x}_{chunk_y}")
        
        # Generate walls and geometry
        for x in range(self.chunk_size):
            for z in range(self.chunk_size):
                world_x = chunk_x * self.chunk_size + x
                world_z = chunk_y * self.chunk_size + z
                
                # Height determined by 3D noise
                height = self._get_height(world_x, world_z)
                
                # Wall generation probability based on noise
                wall_prob = noise.pnoise2(world_x * 0.1, world_z * 0.1, base=self.seed)
                
                if wall_prob < -0.3:  # Hallway sections
                    self._create_wall(chunk_node, world_x, world_z, height)
                elif wall_prob < 0.2 and random.random() < 0.3:  # Random room sections
                    self._create_wall(chunk_node, world_x, world_z, height)
        
        return chunk_node

    def _get_height(self, x, z):
        """Get wall height with procedural variation"""
        base_height = 3.0  # Standard Backrooms height
        variation = noise.pnoise2(x * 0.05, z * 0.05, base=self.seed) * 0.5
        return base_height + variation

    def _create_wall(self, chunk_node, x, z, height):
        """Create a wall at the specified position"""
        # Create wall using CardMaker for performance
        wall = chunk_node.attachNewNode(f"wall_{x}_{z}")
        cm = CardMaker("wall_card")
        cm.setFrame(-0.5, 0.5, -0.5, 0.5)
        wall_geom = wall.attachNewNode(cm.generate())
        wall_geom.setScale(1, 1, height)
        wall_geom.setPos(x, z, height / 2)
        
        # Apply base color with variation
        base_color = (0.94, 0.86, 0.71)  # Cream color
        variation = random.uniform(-0.02, 0.02)
        wall.setColor(
            max(0, min(1, base_color[0] + variation)),
            max(0, min(1, base_color[1] + variation)),
            max(0, min(1, base_color[2] + variation)),
            1
        )
        
        return wall


class PlayerController:
    """Player controller with psychological elements and 8-direction movement"""
    def __init__(self, x=0.5, y=0.5, z=1.8):
        self.x = x
        self.y = y
        self.z = z
        self.angle = 0  # Looking angle in radians
        self.pitch = 0  # Looking up/down angle
        self.move_speed = 5.0  # Movement speed
        self.look_sensitivity = 0.3  # Mouse sensitivity
        self.gravity = -9.8  # Gravity constant
        self.velocity = LVector3(0, 0, 0)
        self.on_ground = True
        
        # Psychological state
        self.sanity = 100.0
        self.is_panicking = False
        self.panic_level = 0.0
        self.reality_stability = 1.0
        self.perceived_position = LPoint3(x, y, z)
        
        # Input state
        self.keys = {
            'forward': False,
            'backward': False,
            'left': False,
            'right': False,
            'up': False,
            'down': False,
            'jump': False
        }

    def set_key(self, key, value):
        """Set key state"""
        if key in self.keys:
            self.keys[key] = value

    def handle_input(self, dt, world):
        """Handle player input for movement and rotation"""
        # Calculate movement direction based on current angle
        move_x = 0
        move_y = 0
        
        # Forward/backward movement (W/S)
        if self.keys['forward']:
            move_x += math.cos(self.angle)
            move_y += math.sin(self.angle)
        if self.keys['backward']:
            move_x -= math.cos(self.angle)
            move_y -= math.sin(self.angle)
            
        # Strafe left/right (A/D)
        if self.keys['left']:
            move_x += math.cos(self.angle + math.pi/2)  # 90 degrees left
            move_y += math.sin(self.angle + math.pi/2)
        if self.keys['right']:
            move_x += math.cos(self.angle - math.pi/2)  # 90 degrees right
            move_y += math.sin(self.angle - math.pi/2)
            
        # Normalize diagonal movement
        if move_x != 0 or move_y != 0:
            length = math.sqrt(move_x**2 + move_y**2)
            move_x = move_x / length
            move_y = move_y / length
        
        # Apply movement
        speed = self.move_speed
        if self.is_panicking:
            speed *= (0.5 + self.panic_level * 0.5)
        
        self.velocity.x = move_x * speed
        self.velocity.y = move_y * speed
        
        # Jumping
        if self.keys['jump'] and self.on_ground:
            self.velocity.z = 8.0  # Jump velocity
            self.on_ground = False

    def update(self, dt, world):
        """Update player state"""
        # Handle input
        self.handle_input(dt, world)
        
        # Apply gravity
        if not self.on_ground:
            self.velocity.z += self.gravity * dt
        
        # Update position
        new_x = self.x + self.velocity.x * dt
        new_y = self.y + self.velocity.y * dt
        new_z = self.z + self.velocity.z * dt
        
        # Collision detection with world boundaries
        if self._can_move_to(new_x, self.y, world):
            self.x = new_x
        else:
            self.velocity.x = 0  # Stop horizontal movement
        
        if self._can_move_to(self.x, new_y, world):
            self.y = new_y
        else:
            self.velocity.y = 0  # Stop horizontal movement
        
        # Vertical collision (simple floor check)
        if new_z <= 0:
            new_z = 0
            self.velocity.z = 0
            self.on_ground = True
        else:
            self.on_ground = False
            
        self.z = new_z
        
        # Update psychological state
        self._update_psychological_state(dt, world)

    def _can_move_to(self, x, y, world):
        """Check if movement is possible (simple collision detection)"""
        cell_x, cell_y = int(x), int(y)
        cell_type = world.get_cell(cell_x, cell_y)
        return cell_type == 0  # Can move if cell is empty (0)

    def _update_psychological_state(self, dt, world):
        """Update player's sanity and psychological state"""
        # Time-based sanity recovery when calm
        if not self.is_panicking:
            self.sanity = min(100.0, self.sanity + 0.5 * dt)
        
        # Sanity drain from environmental factors
        sanity_drain = 0.0
        
        # Reality instability effect
        if self.reality_stability < 0.5:
            sanity_drain += (0.5 - self.reality_stability) * 0.8
        
        # Apply sanity drain
        self.sanity = max(0.0, self.sanity - sanity_drain * dt)
        
        # Update panic state
        new_panic = self.sanity < 30.0
        if new_panic != self.is_panicking:
            self.is_panicking = new_panic
        
        # Panic level intensity
        if self.is_panicking:
            self.panic_level = min(1.0, self.panic_level + dt * 0.2)
        else:
            self.panic_level = max(0.0, self.panic_level - dt * 0.3)

    def get_position(self):
        """Get player's current position"""
        return LPoint3(self.x, self.y, self.z)

    def get_forward_vector(self):
        """Get forward direction vector"""
        return LVector3(math.cos(self.angle), math.sin(self.angle), 0).normalized()

    def get_right_vector(self):
        """Get right direction vector"""
        return LVector3(math.cos(self.angle + math.pi/2), math.sin(self.angle + math.pi/2), 0).normalized()


class AtmosphericLighting:
    """Atmospheric lighting system for horror atmosphere"""
    def __init__(self, render):
        self.render = render
        self.light_sources = []
        self.ambient_level = 0.2  # Base darkness level
        
    def setup_dynamic_lights(self):
        """Create limited visibility through dynamic lights"""
        # Player flashlight
        self.flashlight = PointLight("player_flashlight")
        self.flashlight.set_color((1.0, 0.9, 0.8, 1.0))  # Warm white
        self.flashlight.set_attenuation((0.0, 0.5, 0.01))  # Quadratic attenuation
        self.flashlight_node = self.render.attach_new_node(self.flashlight)
        self.render.set_light(self.flashlight_node)
        
        # Distant flickering lights
        for i in range(5):
            light = PointLight(f"ambient_light_{i}")
            light.set_color((0.8, 0.85, 1.0, 1.0))  # Cool blue-white
            light.set_attenuation((0.0, 0.3, 0.02))
            node = self.render.attach_new_node(light)
            node.set_pos(
                random.uniform(-50, 50),
                random.uniform(1.5, 2.5),
                random.uniform(-50, 50)
            )
            self.light_sources.append({
                'node': node,
                'base_intensity': random.uniform(0.3, 0.7),
                'flicker_speed': random.uniform(0.5, 3.0),
                'flicker_amount': random.uniform(0.2, 0.6)
            })

    def update(self, player_pos, reality_stability, dt):
        """Update lighting based on player position and reality state"""
        # Move flashlight with player
        self.flashlight_node.set_pos(player_pos.x, player_pos.y, player_pos.z + 0.5)
        
        # Update flickering lights
        for light in self.light_sources:
            base = light['base_intensity']
            speed = light['flicker_speed']
            amount = light['flicker_amount']
            
            # Flicker intensity
            flicker = (math.sin(globalClock.get_frame_time() * speed) + 1) * 0.5
            intensity = base + flicker * amount
            
            # Distance-based dimming
            dist = light['node'].get_pos().distance(player_pos)
            if dist > 15.0:
                intensity *= max(0.0, 1.0 - (dist - 15.0) / 10.0)
            
            # Reality distortion affects light stability
            if reality_stability < 0.7:
                intensity *= (0.5 + random.random() * 0.5)
            
            light['node'].set_color((intensity, intensity, intensity, 1.0))


class BackroomsGame(ShowBase):
    """Main game class implementing the Backrooms experience"""
    def __init__(self, level_file=None):
        ShowBase.__init__(self)
        
        # Disable default mouse control to implement FPS-style camera
        self.disableMouse()
        
        # Set up basic scene
        self.setBackgroundColor(0.1, 0.1, 0.15)  # Dark blue-gray for loneliness aesthetic
        
        # Initialize core systems
        self.world = BackroomsWorld(seed=42, level_file=level_file)
        # Set player start position based on level type
        if level_file and hasattr(self.world, 'rooms') and self.world.rooms:
            # Start player in the first room if available
            start_x, start_y = self.world.rooms[0][0], self.world.rooms[0][1]
            self.player = PlayerController(x=start_x+0.5, y=start_y+0.5, z=1.8)
        else:
            self.player = PlayerController(x=5.5, y=5.5, z=1.8)
        self.lighting = AtmosphericLighting(self.render)
        
        # Setup lighting
        self.lighting.setup_dynamic_lights()
        
        # Load textures if available
        self.floor_texture = None
        self.wall_texture = None
        self.load_textures()
        
        # Create 3D environment
        self.create_3d_environment()
        
        # Setup input handling
        self.setup_input()
        
        # Initialize mouse look variables
        self.mouse_x = 0
        self.mouse_y = 0
        self.prev_mouse_x = 0
        self.prev_mouse_y = 0
        self.mouse_locked = False
        
        # Create UI elements
        self.create_ui()
        
        # Start game loop
        self.taskMgr.add(self.game_loop, "game_loop")
        
        print("Backrooms Game: FPS-style Controls Active")
        print("WASD: 8-direction movement | Mouse: Look around | Space: Jump | ESC: Quit")
        
    def load_textures(self):
        """Load textures from the textures folder"""
        # Try to load floor texture
        floor_paths = ["textures/floor_texture.png", "textures/floor.png", "textures/ground.png"]
        for path in floor_paths:
            if os.path.exists(path):
                try:
                    self.floor_texture = loader.loadTexture(path)
                    print(f"Loaded floor texture: {path}")
                    break
                except Exception as e:
                    print(f"Could not load floor texture {path}: {e}")
        
        if not self.floor_texture:
            print("Warning: No floor texture found, using default color")
        
        # Try to load wall texture
        wall_paths = ["textures/wall_texture.png", "textures/wall.png", "textures/texture.png"]
        for path in wall_paths:
            if os.path.exists(path):
                try:
                    self.wall_texture = loader.loadTexture(path)
                    print(f"Loaded wall texture: {path}")
                    break
                except Exception as e:
                    print(f"Could not load wall texture {path}: {e}")
        
        if not self.wall_texture:
            print("Warning: No wall texture found, using default color")

    def create_3d_environment(self):
        """Create 3D environment with walls, floors, and ceilings"""
        # Determine the bounds of the level to create
        if hasattr(self.world, 'grid') and self.world.grid:
            # Using loaded level data
            start_x, end_x = 0, self.world.width
            start_y, end_y = 0, self.world.height
        else:
            # Using procedural generation
            start_x, end_x = -15, 15
            start_y, end_y = -15, 15

        # Generate the environment based on the level data
        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                cell_type = self.world.get_cell(x, y)
                if cell_type != 0:  # If it's not empty space, create a wall
                    self.create_wall_at(x, y, cell_type)

        # Create floor based on level size
        if hasattr(self.world, 'grid') and self.world.grid:
            floor_size = max(self.world.width, self.world.height) / 2
        else:
            floor_size = 50

        floor = self.render.attachNewNode("floor")
        cm = CardMaker("floor_card")
        cm.setFrame(-floor_size, floor_size, -floor_size, floor_size)
        floor_geom = floor.attachNewNode(cm.generate())
        floor_geom.setPos(0, 0, -0.5)
        floor_geom.setHpr(90, 0, 0)  # Rotate to be horizontal

        # Apply floor texture if available
        if self.floor_texture:
            floor_geom.setTexture(self.floor_texture)
        else:
            floor_geom.setColor(0.98, 0.94, 0.82)  # Pale yellow floor

        # Create ceiling
        ceiling = self.render.attachNewNode("ceiling")
        cm = CardMaker("ceiling_card")
        cm.setFrame(-floor_size, floor_size, -floor_size, floor_size)
        ceiling_geom = ceiling.attachNewNode(cm.generate())
        ceiling_geom.setPos(0, 0, 3.0)
        ceiling_geom.setHpr(-90, 0, 0)  # Rotate to be horizontal

        # Apply ceiling texture if available (or use same as floor)
        if self.floor_texture:
            ceiling_geom.setTexture(self.floor_texture)
        else:
            ceiling_geom.setColor(0.98, 0.98, 0.94)  # Light ceiling color

    def create_wall_at(self, x, y, cell_type):
        """Create a wall at the specified position"""
        # Create a wall block using CardMaker for better performance
        wall = self.render.attachNewNode(f"wall_{x}_{y}")
        cm = CardMaker("wall_card")
        cm.setFrame(-0.5, 0.5, -0.5, 0.5)
        wall_geom = wall.attachNewNode(cm.generate())
        wall_geom.setScale(1, 1, 3)  # Make it tall
        wall_geom.setPos(x, y, 1.0)  # Position it correctly
        
        # Apply wall texture if available
        if self.wall_texture:
            wall_geom.setTexture(self.wall_texture)
        else:
            # Set wall color based on cell type
            wall_colors = [
                (0.94, 0.86, 0.71),  # Cream walls (240, 220, 180) / 255
                (0.90, 0.82, 0.67),  # Slightly darker (230, 210, 170) / 255
                (0.86, 0.78, 0.63),  # Even darker (220, 200, 160) / 255
                (1.0, 0.96, 0.86),   # Light cream (255, 245, 220) / 255
                (0.78, 0.74, 0.63),  # Darker cream (200, 190, 160) / 255
            ]
            
            color_idx = (cell_type - 1) % len(wall_colors)
            base_color = wall_colors[color_idx]
            variation = random.uniform(-0.02, 0.02)
            wall.setColor(
                max(0, min(1, base_color[0] + variation)),
                max(0, min(1, base_color[1] + variation)),
                max(0, min(1, base_color[2] + variation)),
                1
            )

    def setup_input(self):
        """Setup keyboard and mouse input handlers"""
        # Keyboard controls
        self.accept('w', self.player.set_key, ['forward', True])
        self.accept('w-up', self.player.set_key, ['forward', False])
        self.accept('s', self.player.set_key, ['backward', True])
        self.accept('s-up', self.player.set_key, ['backward', False])
        self.accept('a', self.player.set_key, ['left', True])
        self.accept('a-up', self.player.set_key, ['left', False])
        self.accept('d', self.player.set_key, ['right', True])
        self.accept('d-up', self.player.set_key, ['right', False])
        self.accept('space', self.player.set_key, ['jump', True])
        self.accept('space-up', self.player.set_key, ['jump', False])
        self.accept('escape', sys.exit)
        
        # Mouse input for looking around
        self.accept('mouse1', self.lock_mouse)
        
        # Center mouse cursor initially
        self.win.movePointer(0, int(self.win.getProperties().getXSize() / 2), int(self.win.getProperties().getYSize() / 2))

    def lock_mouse(self):
        """Lock mouse cursor for FPS-style look controls"""
        self.mouse_locked = not self.mouse_locked
        if self.mouse_locked:
            self.win.requestProperties(WindowProperties().setCursorHidden(True))
        else:
            self.win.requestProperties(WindowProperties().setCursorHidden(False))

    def create_ui(self):
        """Create UI elements for the game"""
        # Create status text
        self.status_text = OnscreenText(
            text="POS: 5.5, 5.5, 1.8 | SANITY: 100%",
            style=1,
            fg=(0.9, 0.8, 0.7, 1),
            scale=0.05,
            pos=(-1.3, -0.9),
            align=TextNode.ALeft
        )
        
        # Create controls text
        self.controls_text = OnscreenText(
            text="WASD: Move | Mouse: Look | Space: Jump | ESC: Quit",
            style=1,
            fg=(0.9, 0.8, 0.7, 1),
            scale=0.05,
            pos=(0.5, -0.9),
            align=TextNode.ALeft
        )

    def game_loop(self, task):
        """Main game loop"""
        dt = globalClock.getDt()
        
        # Handle mouse look if mouse is locked
        if self.mouse_locked and self.mouseWatcherNode.hasMouse():
            # Get current mouse position
            self.mouse_x = self.mouseWatcherNode.getMouseX()
            self.mouse_y = self.mouseWatcherNode.getMouseY()
            
            # Calculate mouse movement since last frame
            mouse_delta_x = self.mouse_x - self.prev_mouse_x
            mouse_delta_y = self.mouse_y - self.prev_mouse_y
            
            # Apply mouse sensitivity to player rotation
            self.player.angle += mouse_delta_x * self.player.look_sensitivity
            self.player.pitch = max(-90, min(90, self.player.pitch - mouse_delta_y * self.player.look_sensitivity))
            
            # Center mouse cursor again to prevent it from going off screen
            center_x = self.win.getProperties().getXSize() / 2
            center_y = self.win.getProperties().getYSize() / 2
            self.win.movePointer(0, int(center_x), int(center_y))
            
            # Update previous mouse position
            self.prev_mouse_x = center_x
            self.prev_mouse_y = center_y
        else:
            # Update mouse position if not locked
            if self.mouseWatcherNode.hasMouse():
                self.prev_mouse_x = self.mouseWatcherNode.getMouseX()
                self.prev_mouse_y = self.mouseWatcherNode.getMouseY()
        
        # Update player
        self.player.update(dt, self.world)
        
        # Update lighting
        player_pos = self.player.get_position()
        self.lighting.update(player_pos, self.player.reality_stability, dt)
        
        # Update camera to follow player
        self.update_camera()
        
        # Update UI
        self.update_ui()
        
        return Task.cont

    def update_camera(self):
        """Update camera position and orientation to match player"""
        player_pos = self.player.get_position()
        
        # Set camera position
        self.camera.setPos(player_pos.x, player_pos.y, player_pos.z)
        
        # Set camera orientation (look in the direction the player is facing)
        self.camera.setH(-math.degrees(self.player.angle))
        self.camera.setP(-self.player.pitch)

    def update_ui(self):
        """Update UI elements"""
        # Update status text
        pos = self.player.get_position()
        status_text = f"POS: {pos.x:.1f}, {pos.y:.1f}, {pos.z:.1f} | SANITY: {self.player.sanity:.0f}%"
        self.status_text.setText(status_text)


def main():
    """Main function to run the game"""
    game = BackroomsGame()
    game.run()


if __name__ == "__main__":
    main()