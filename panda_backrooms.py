"""
Panda3D Backrooms Game - Psycho Horror with Room Generation
This is a conversion of the Pygame raycasting game to Panda3D
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


class Raycaster:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.fov = math.pi / 3  # 60 degrees
        self.ray_angle_step = self.fov / width

        # Color palette (soft, dreamy colors)
        self.colors = {
            'walls': [
                (240, 220, 180),  # Cream walls
                (230, 210, 170),  # Slightly darker
                (220, 200, 160),  # Even darker
                (255, 245, 220),  # Light cream
            ],
            'floors': [
                (250, 240, 210),  # Pale yellow floor
                (255, 250, 230),  # Lighter
            ],
            'ceilings': [
                (255, 255, 245),  # Almost white ceiling
                (250, 250, 240),  # Slightly warm
            ],
            'fog': (200, 180, 150)  # Warm fog
        }

        self.wave_offset = 0
        self.flicker_intensity = 0.0

    def cast_rays(self, player_x, player_y, player_angle, world, draw_distance=10):
        """Cast rays and return render data"""
        rays = []
        half_fov = self.fov / 2

        for x in range(self.width):
            # Calculate ray angle
            ray_angle = player_angle + (x / self.width - 0.5) * self.fov

            # Cast ray
            distance, wall_type, side = self._cast_single_ray(
                player_x, player_y, ray_angle, world, draw_distance
            )

            # Apply fog
            fog_factor = min(1.0, distance / draw_distance)

            # Apply dream effects
            wave_effect = math.sin(self.wave_offset + x * 0.01) * 0.3
            distance *= (1.0 + wave_effect * 0.05)

            rays.append({
                'x': x,
                'distance': distance,
                'wall_type': wall_type,
                'side': side,  # 'x' or 'y' for texture correction
                'fog_factor': fog_factor
            })

        self.wave_offset += 0.03
        self.flicker_intensity = math.sin(self.wave_offset * 2) * 0.1

        return rays

    def _cast_single_ray(self, start_x, start_y, angle, world, max_distance):
        """Working DDA raycaster"""
        # Ray direction
        ray_dir_x = math.cos(angle)
        ray_dir_y = math.sin(angle)

        # Player position in map grid
        map_x = int(start_x)
        map_y = int(start_y)

        # Delta distance (how far to next grid line)
        delta_dist_x = abs(1.0 / ray_dir_x) if ray_dir_x != 0 else float('inf')
        delta_dist_y = abs(1.0 / ray_dir_y) if ray_dir_y != 0 else float('inf')

        # Step direction
        step_x = 1 if ray_dir_x > 0 else -1
        step_y = 1 if ray_dir_y > 0 else -1

        # Initial side distance
        if ray_dir_x < 0:
            side_dist_x = (start_x - map_x) * delta_dist_x
        else:
            side_dist_x = (map_x + 1.0 - start_x) * delta_dist_x

        if ray_dir_y < 0:
            side_dist_y = (start_y - map_y) * delta_dist_y
        else:
            side_dist_y = (map_y + 1.0 - start_y) * delta_dist_y

        # DDA loop
        distance = 0.0
        hit = False
        side = 'x'  # which side was hit

        while not hit and distance < max_distance:
            # Jump to next map square
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 'x'
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 'y'

            # Check for wall hit
            try:
                # Use world.get_cell() with proper bounds
                if abs(map_x) < 1000 and abs(map_y) < 1000:
                    wall_type = world.get_cell(map_x, map_y)
                    if wall_type > 0:
                        hit = True
                        # Calculate exact distance
                        if side == 'x':
                            distance = abs((map_x - start_x + (0 if step_x > 0 else 1)) / ray_dir_x)
                        else:
                            distance = abs((map_y - start_y + (0 if step_y > 0 else 1)) / ray_dir_y)
                else:
                    # Too far away - treat as open space
                    wall_type = 0
            except:
                wall_type = 0

            # Safety break
            if abs(map_x) > 2000 or abs(map_y) > 2000:
                distance = max_distance
                wall_type = 0
                break

        if not hit:
            distance = max_distance
            wall_type = 0

        return distance, wall_type, side

    def get_wall_color(self, wall_type, ray_data):
        """Get wall color with dream effects"""
        if wall_type == 0:
            return (0, 0, 0)  # Transparent (shouldn't be drawn)

        # Select base color
        color_idx = (wall_type - 1) % len(self.colors['walls'])
        base_color = list(self.colors['walls'][color_idx])

        # Add flicker effect
        flicker = 1.0 + self.flicker_intensity * random.uniform(-0.1, 0.1)
        base_color[0] = min(255, int(base_color[0] * flicker))
        base_color[1] = min(255, int(base_color[1] * flicker))
        base_color[2] = min(255, int(base_color[2] * flicker))

        # Add fog
        fog = self.colors['fog']
        fog_factor = ray_data['fog_factor']
        final_color = [
            int(base_color[0] * (1 - fog_factor * 0.5) + fog[0] * fog_factor * 0.5),
            int(base_color[1] * (1 - fog_factor * 0.5) + fog[1] * fog_factor * 0.5),
            int(base_color[2] * (1 - fog_factor * 0.5) + fog[2] * fog_factor * 0.5)
        ]

        return tuple(final_color)


class PandaBackrooms(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Set up basic scene
        self.setBackgroundColor(0.78, 0.71, 0.59)  # Warm fog color
        
        # Initialize game objects
        self.width, self.height = 1024, 768
        self.raycaster = Raycaster(self.width, self.height)
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
        self.camera.setPos(0, 0, 0)
        self.mouse_x = 0
        self.mouse_y = 0
        
        # Create a texture buffer for raycasting
        self.setup_ray_texture()
        
        # Create UI elements
        self.create_ui()
        
        # Start game loop
        self.taskMgr.add(self.game_loop, "game_loop")
        
        print("Panda3D Backrooms: Cute Psycho Horror")
        print("WASD to move, ARROW KEYS to turn, ESC to quit")
        print("Mouse look enabled - move mouse to look around")

    def setup_ray_texture(self):
        """Set up texture for raycasting display"""
        # Create a texture buffer to draw the raycasted view
        win_props = WindowProperties()
        win_props.setSize(self.width, self.height)
        
        # Create texture buffer
        self.ray_buffer = self.win.makeTextureBuffer("ray_buffer", self.width, self.height)
        self.ray_buffer.setClearColor(Vec4(0.78, 0.71, 0.59, 1))
        
        # Create display region for the ray buffer
        self.ray_dr = self.ray_buffer.makeDisplayRegion()
        self.ray_dr.setClearDepthActive(True)
        self.ray_dr.setClearColorActive(True)
        
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
            text=self.current_message,
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
            if hasattr(self, 'prev_mouse_x'):
                mouse_delta_x = mouse_x - self.prev_mouse_x
                self.player.angle += mouse_delta_x * 0.03  # Sensitivity
            
            self.prev_mouse_x = mouse_x
            self.prev_mouse_y = mouse_y
        
        # Update player with key input
        dt = globalClock.getDt() * 60  # Convert to frame rate independent movement
        self.player.update(self.keys, self.world, dt)
        
        # Update UI
        self.update_ui()
        
        # Render raycasted view
        self.render_raycast_view()
        
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

    def render_raycast_view(self):
        """Render the raycasted 3D view"""
        # Cast rays
        px, py = self.player.get_render_position()
        rays = self.raycaster.cast_rays(px, py, self.player.angle, self.world, draw_distance=15)
        
        # For now, just update the camera to match player position
        # In a real implementation, we'd draw the raycasted view to the texture buffer
        self.camera.setPos(self.player.x, self.player.y, 1.8 + self.player.floating)
        self.camera.setH(self.player.angle * 180 / math.pi)  # Convert radians to degrees
        self.camera.setP(-5)  # Look slightly downward

    def update_raycast_texture(self):
        """Update the raycast texture with current view"""
        # This would be where we draw the raycasted view to a texture
        # For now, this is a placeholder
        pass


def main():
    game = PandaBackrooms()
    game.run()


if __name__ == "__main__":
    main()