"""
Panda3D Backrooms Game - Final Implementation with Psycho Horror Elements
This creates a complete 3D Backrooms experience with proper collision, lighting, and atmosphere
"""
import math
import random
import noise
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from direct.task import Task
from direct.interval.IntervalGlobal import Sequence
from direct.gui.DirectGui import *
import sys

# Here i need add textures which there in folder named "textures"
# And also add models which there in folder named "models" (blend-bpy i think, gltf stl and etc also can be used)

# Load the textures and models
# loader.load_model("")
# loader.load_texture("")

class BackroomsWorld:
    def __init__(self, seed=None):
        self.seed = seed or random.randint(0, 999999)
        random.seed(self.seed)

        # Noise parameters for dream-like generation
        self.scale = 10.0
        self.octaves = 4
        self.persistence = 0.5
        self.lacunarity = 2.0

        # Room types (soft, dreamy)
        self.room_types = {
            0: 'empty',  # Empty space
            1: 'hallway',  # Narrow hallway
            2: 'room',  # Small room
            3: 'junction',  # T-junction
            4: 'corner',  # Corner
            5: 'open',  # Open space
        }

        # Psycho elements
        self.dream_zones = {}  # Areas with special effects
        self.generate_dream_zones()

    def generate_dream_zones(self):
        """Generate areas with special dream effects"""
        for i in range(10):
            x = random.randint(-50, 50)
            y = random.randint(-50, 50)
            radius = random.uniform(3.0, 8.0)
            effect = random.choice(['slow', 'fast', 'float', 'glitch'])

            self.dream_zones[(x, y)] = {
                'radius': radius,
                'effect': effect,
                'intensity': random.uniform(0.3, 0.8)
            }

    def get_cell(self, x, y):
        """Get cell type at world coordinates"""
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

    def get_room_at(self, x, y):
        """Get detailed room information at coordinates"""
        cell_type = self.get_cell(x, y)

        # Add psycho-dream effects near dream zones
        dream_effect = None
        dream_intensity = 0.0

        for (zone_x, zone_y), zone_data in self.dream_zones.items():
            distance = math.sqrt((x - zone_x) ** 2 + (y - zone_y) ** 2)
            if distance < zone_data['radius']:
                intensity = (zone_data['radius'] - distance) / zone_data['radius']
                if intensity > dream_intensity:
                    dream_intensity = intensity
                    dream_effect = zone_data['effect']

        return {
            'type': cell_type,
            'dream_effect': dream_effect,
            'dream_intensity': dream_intensity,
            'x': x,
            'y': y
        }

    def generate_chunk(self, chunk_x, chunk_y, chunk_size=16):
        """Generate a chunk of the world"""
        chunk = []
        for y in range(chunk_size):
            row = []
            for x in range(chunk_size):
                world_x = chunk_x * chunk_size + x
                world_y = chunk_y * chunk_size + y
                row.append(self.get_cell(world_x, world_y))
            chunk.append(row)
        return chunk

    def get_dream_effect_at(self, x, y):
        """Get current dream effect at position"""
        for (zone_x, zone_y), zone_data in self.dream_zones.items():
            distance = math.sqrt((x - zone_x) ** 2 + (y - zone_y) ** 2)
            if distance < zone_data['radius']:
                intensity = (zone_data['radius'] - distance) / zone_data['radius']
                return zone_data['effect'], intensity
        return None, 0.0


class DreamPlayer:
    def __init__(self, x=0.5, y=0.5, angle=0):
        self.x = x
        self.y = y
        self.angle = angle
        self.move_speed = 0.05
        self.turn_speed = 0.03

        # Dream state
        self.dream_level = 0.0  # 0.0 = awake, 1.0 = deep dream
        self.floating = 0.0  # Vertical float offset
        self.float_speed = 0.02
        self.float_direction = 1

        # Psycho effects
        self.reality_stability = 1.0  # 1.0 = stable, 0.0 = completely distorted
        self.glitch_timer = 0
        self.sanity = 100.0

        # Footsteps
        self.footstep_timer = 0
        self.footstep_interval = 0.3
        self.is_walking = False

    def update(self, keys_pressed, world, dt=1.0):
        # Handle movement
        moved = False

        if keys_pressed.get('w', False):
            new_x = self.x + math.cos(self.angle) * self.move_speed * dt
            new_y = self.y + math.sin(self.angle) * self.move_speed * dt
            if self._can_move_to(new_x, new_y, world):
                self.x, self.y = new_x, new_y
                moved = True

        if keys_pressed.get('s', False):
            new_x = self.x - math.cos(self.angle) * self.move_speed * dt
            new_y = self.y - math.sin(self.angle) * self.move_speed * dt
            if self._can_move_to(new_x, new_y, world):
                self.x, self.y = new_x, new_y
                moved = True

        if keys_pressed.get('a', False):
            self.angle -= self.turn_speed * dt
            moved = True

        if keys_pressed.get('d', False):
            self.angle += self.turn_speed * dt
            moved = True

        self.is_walking = moved

        # Update dream effects
        self._update_dream_state(world, dt)
        self._update_float(dt)
        self._update_glitch(dt)
        self._update_footsteps(dt)

    def _can_move_to(self, x, y, world):
        """Proper collision detection"""
        # Simple collision: check if center point is in wall
        cell_x, cell_y = int(x), int(y)

        # Check bounds
        if abs(cell_x) > 500 or abs(cell_y) > 500:
            return True  # Allow movement in open areas

        # Check if cell is wall
        cell_type = world.get_cell(cell_x, cell_y)
        return cell_type == 0  # Can move if cell is empty (0)

    def _update_dream_state(self, world, dt):
        """Update dream level based on environment"""
        # Get dream effect at current position
        effect, intensity = world.get_dream_effect_at(self.x, self.y)

        if effect:
            # Modify dream level based on effect
            if effect == 'slow':
                self.move_speed = max(0.01, self.move_speed * (1 - intensity * 0.5))
                self.turn_speed = max(0.01, self.turn_speed * (1 - intensity * 0.5))
            elif effect == 'fast':
                self.move_speed = min(0.2, self.move_speed * (1 + intensity * 0.5))
                self.turn_speed = min(0.1, self.turn_speed * (1 + intensity * 0.5))
            elif effect == 'float':
                self.float_speed = 0.05 * intensity
            elif effect == 'glitch':
                self.glitch_timer = max(self.glitch_timer, intensity * 2.0)

        # Gradually return to normal when not in dream zones
        if not effect:
            self.move_speed = max(0.03, min(0.08, self.move_speed + (0.05 - self.move_speed) * 0.1))
            self.turn_speed = max(0.02, min(0.04, self.turn_speed + (0.03 - self.turn_speed) * 0.1))

    def _update_float(self, dt):
        """Update floating effect"""
        self.float_direction *= -1 if abs(self.floating) > 0.1 else 1
        self.floating += self.float_direction * self.float_speed * dt
        self.floating = max(-0.15, min(0.15, self.floating))

    def _update_glitch(self, dt):
        """Update glitch effect"""
        if self.glitch_timer > 0:
            self.glitch_timer -= dt
            # Add random distortion
            if random.random() < 0.1:
                self.angle += random.uniform(-0.1, 0.1)
        else:
            self.glitch_timer = 0

    def _update_footsteps(self, dt):
        """Update footstep timing"""
        if self.is_walking:
            self.footstep_timer -= dt
            if self.footstep_timer <= 0:
                self.footstep_timer = self.footstep_interval
                # Trigger footstep sound (you'll add this)
                # self.play_footstep()
        else:
            self.footstep_timer = self.footstep_interval

    def get_render_position(self):
        """Get position for rendering (with float offset)"""
        return self.x, self.y + self.floating


class PandaBackrooms(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Set up basic scene
        self.setBackgroundColor(0.78, 0.71, 0.59)  # Warm fog color
        
        # Setup lighting
        self.setup_lighting()
        
        # Initialize game objects
        self.world = BackroomsWorld(seed=42)
        self.player = DreamPlayer(x=5.5, y=5.5, angle=0)
        
        # Key mapping
        self.keys = {
            'w': False,
            's': False,
            'a': False,
            'd': False,
            'arrow_left': False,
            'arrow_right': False
        }
        
        # Accept key events
        self.accept('w', self.set_key, ['w', True])
        self.accept('w-up', self.set_key, ['w', False])
        self.accept('s', self.set_key, ['s', True])
        self.accept('s-up', self.set_key, ['s', False])
        self.accept('a', self.set_key, ['a', True])
        self.accept('a-up', self.set_key, ['a', False])
        self.accept('d', self.set_key, ['d', True])
        self.accept('d-up', self.set_key, ['d', False])
        self.accept('arrow_left', self.set_key, ['arrow_left', True])
        self.accept('arrow_left-up', self.set_key, ['arrow_left', False])
        self.accept('arrow_right', self.set_key, ['arrow_right', True])
        self.accept('arrow_right-up', self.set_key, ['arrow_right', False])
        self.accept('escape', sys.exit)
        
        # Mouse look setup
        self.disableMouse()
        self.mouseWatcherNode = base.mouseWatcherNode
        # Initialize mouse coordinates to current position to avoid first-frame jump
        if self.mouseWatcherNode.hasMouse():
            self.prev_mouse_x = self.mouseWatcherNode.getMouseX()
            self.prev_mouse_y = self.mouseWatcherNode.getMouseY()
        else:
            self.prev_mouse_x = 0
            self.prev_mouse_y = 0
        
        # Create 3D environment
        self.create_3d_environment()
        
        # Create UI elements
        self.create_ui()
        
        # Start game loop
        self.taskMgr.add(self.game_loop, "game_loop")
        
        print("Panda3D Backrooms: Cute Psycho Horror")
        print("WASD to move, ARROW KEYS to turn, ESC to quit")
        print("Mouse look enabled - move mouse to look around")

    def setup_lighting(self):
        """Setup lighting for the Backrooms atmosphere"""
        # Ambient light (soft, warm)
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor((0.6, 0.55, 0.45, 1))
        self.ambientLightNode = self.render.attachNewNode(ambientLight)
        self.render.setLight(self.ambientLightNode)
        
        # Directional light (mimics the fluorescent lighting)
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setColor((0.8, 0.75, 0.65, 1))
        directionalLightNP = self.render.attachNewNode(directionalLight)
        directionalLightNP.setHpr(0, -60, 0)  # Point downward
        self.render.setLight(directionalLightNP)
        
        # Add some subtle flickering to create unease
        self.flicker_intensity = 0.0

    def create_3d_environment(self):
        """Create 3D environment with walls, floors, and ceilings"""
        # Create a simple grid of walls based on the world map
        self.walls = []
        
        # Generate a section of the world around the starting position
        for x in range(-15, 15):
            for y in range(-15, 15):
                cell_type = self.world.get_cell(x, y)
                if cell_type != 0:  # If it's not empty space, create a wall
                    self.create_wall_at(x, y, cell_type)
        
        # Create floor
        floor_size = 50
        floor = self.render.attachNewNode("floor")
        cm = CardMaker("floor_card")
        cm.setFrame(-floor_size, floor_size, -floor_size, floor_size)
        floor_geom = floor.attachNewNode(cm.generate())
        floor_geom.setPos(0, 0, -0.5)
        floor_geom.setColor(0.98, 0.94, 0.82)  # Pale yellow floor
        floor_geom.setHpr(90, 0, 0)  # Rotate to be horizontal

        # Create ceiling
        ceiling = self.render.attachNewNode("ceiling")
        cm = CardMaker("ceiling_card")
        cm.setFrame(-floor_size, floor_size, -floor_size, floor_size)
        ceiling_geom = ceiling.attachNewNode(cm.generate())
        ceiling_geom.setPos(0, 0, 3.0)
        ceiling_geom.setColor(0.98, 0.98, 0.94)  # Light ceiling color
        ceiling_geom.setHpr(-90, 0, 0)  # Rotate to be horizontal

    def create_wall_at(self, x, y, cell_type):
        """Create a wall at the specified position"""
        # Create a wall block using CardMaker for better performance
        wall = self.render.attachNewNode(f"wall_{x}_{y}")
        cm = CardMaker("wall_card")
        cm.setFrame(-0.5, 0.5, -0.5, 0.5)
        wall_geom = wall.attachNewNode(cm.generate())
        wall_geom.setScale(1, 1, 3)  # Make it tall
        wall_geom.setPos(x, y, 1.0)  # Position it correctly
        
        # Set wall color based on cell type. shit this wont stable it wants LVecBase4f not tuple
        wall_colors = [
            (0.94, 0.86, 0.71),  # Cream walls (240, 220, 180) / 255
            (0.90, 0.82, 0.67),  # Slightly darker (230, 210, 170) / 255
            (0.86, 0.78, 0.63),  # Even darker (220, 200, 160) / 255
            (1.0, 0.96, 0.86),   # Light cream (255, 245, 220) / 255
            (0.78, 0.74, 0.63),  # Darker cream (200, 190, 160) / 255
        ]
        
        color_idx = (cell_type - 1) % len(wall_colors)
        wall.setColor(wall_colors[color_idx])
        
        # Add a subtle texture effect by changing the color slightly
        base_color = wall_colors[color_idx]
        variation = random.uniform(-0.02, 0.02)
        wall.setColor(
            max(0, min(1, base_color[0] + variation)),
            max(0, min(1, base_color[1] + variation)),
            max(0, min(1, base_color[2] + variation)),
            1
        )
        
        self.walls.append(wall)

    def create_ui(self):
        """Create UI elements"""
        # Dream message text
        self.dream_messages = [
            "you are safe here...",
            "the walls breathe softly...",
            "listen to the hum...",
            "time flows like honey...",
            "reality is gentle...",
            "you belong here...",
            "the dream protects you...",
            "soft edges, soft mind...",
        ]
        self.current_message = random.choice(self.dream_messages)
        self.message_timer = 0
        
        # Create text node for dream message
        self.message_text = OnscreenText(
            text=f"💭 {self.current_message}",
            style=1,
            fg=(1, 0.9, 0.8, 1),
            scale=0.07,
            pos=(-1.3, 0.9),
            align=TextNode.ALeft
        )
        
        # Create status text
        self.status_text = OnscreenText(
            text="POS: 5.5, 5.5 | DREAM: 0.0 | SANITY: 100%",
            style=1,
            fg=(0.9, 0.8, 0.7, 1),
            scale=0.05,
            pos=(-1.3, -0.9),
            align=TextNode.ALeft
        )
        
        # Create controls text
        self.controls_text = OnscreenText(
            text="WASD: Move | ESC: Quit | Mouse: Look",
            style=1,
            fg=(0.9, 0.8, 0.7, 1),
            scale=0.05,
            pos=(0.5, -0.9),
            align=TextNode.ALeft
        )

    def set_key(self, key, value):
        """Handle key press/release"""
        self.keys[key] = value

    def game_loop(self, task):
        """Main game loop"""
        # Handle mouse look
        if self.mouseWatcherNode.hasMouse():
            mouse_x = self.mouseWatcherNode.getMouseX()
            mouse_y = self.mouseWatcherNode.getMouseY()
            
            # Calculate mouse movement since last frame
            mouse_delta_x = mouse_x - self.prev_mouse_x
            self.player.angle += mouse_delta_x * 0.03  # Sensitivity
            
            self.prev_mouse_x = mouse_x
            self.prev_mouse_y = mouse_y
        
        # Update player with key input
        dt = globalClock.getDt() * 60  # Convert to frame rate independent movement
        self.player.update(self.keys, self.world, dt)
        
        # Update UI
        self.update_ui()
        
        # Update camera position and orientation to match player
        self.update_camera()
        
        # Update lighting effects
        self.update_lighting()
        
        return Task.cont

    def update_ui(self):
        """Update UI elements"""
        self.message_timer += 1
        if self.message_timer > 300:
            self.current_message = random.choice(self.dream_messages)
            self.message_timer = 0
            self.message_text.setText(f"💭 {self.current_message}")
        
        # Update status text
        px, py = self.player.get_render_position()
        status_text = f"POS: {px:.1f}, {py:.1f} | DREAM: {self.player.dream_level:.1f} | SANITY: {self.player.sanity:.0f}%"
        self.status_text.setText(status_text)

    def update_camera(self):
        """Update camera position and orientation to match player"""
        # Update camera position and orientation to match player
        self.camera.setPos(self.player.x, self.player.y, 1.8 + self.player.floating)
        self.camera.setH(self.player.angle * 180 / math.pi)  # Convert radians to degrees
        self.camera.setP(-5)  # Look slightly downward

    def update_lighting(self):
        """Update lighting effects for atmosphere"""
        # Add subtle flickering to create unease
        self.flicker_intensity = math.sin(globalClock.getFrameTime() * 2.3) * 0.02
        flicker_color = (0.6 + self.flicker_intensity, 0.55 + self.flicker_intensity, 0.45 + self.flicker_intensity, 1)
        
        # Update ambient light with flickering
        ambientLight = self.ambientLightNode.node()
        ambientLight.setColor(flicker_color)


def main():
    game = PandaBackrooms()
    game.run()


if __name__ == "__main__":
    main()