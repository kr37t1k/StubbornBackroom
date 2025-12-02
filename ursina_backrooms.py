"""
Ursina-based Psycho Backrooms Game
A 3D horror exploration game with psychological elements
"""
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import math
import random
import noise
import numpy as np

class BackroomsWorld:
    def __init__(self, seed=None):
        self.seed = seed or random.randint(0, 999999)
        random.seed(self.seed)
        
        # Noise parameters for procedural generation
        self.scale = 10.0
        self.octaves = 4
        self.persistence = 0.5
        self.lacunarity = 2.0
        
        # Room types
        self.room_types = {
            0: 'empty',    # Empty space (walkable)
            1: 'wall',     # Wall
            2: 'room',     # Small room
            3: 'junction', # T-junction
            4: 'corner',   # Corner
            5: 'open',     # Open space
        }
        
        # Psycho elements
        self.dream_zones = {}
        self.generate_dream_zones()
        
        # Store generated chunks to avoid regenerating
        self.chunks = {}
    
    def generate_dream_zones(self):
        """Generate areas with special dream effects"""
        for i in range(10):
            x = random.randint(-50, 50)
            y = random.randint(-50, 50)
            radius = random.uniform(3.0, 8.0)
            effect = random.choice(['slow', 'fast', 'float', 'glitch', 'panic'])
            
            self.dream_zones[(x, y)] = {
                'radius': radius,
                'effect': effect,
                'intensity': random.uniform(0.3, 0.8)
            }
    
    def get_cell(self, x, y):
        """Get cell type at world coordinates"""
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
            return 1  # Wall
        elif value < -0.2:
            return 2  # Room
        elif value < 0.2:
            return 3  # Junction
        elif value < 0.6:
            return 4  # Corner
        else:
            return 1  # Wall (more walls for maze-like structure)
    
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


class DreamPlayer(FirstPersonController):
    def __init__(self, world=None, **kwargs):
        super().__init__(**kwargs)
        
        # Player stats
        self.speed = 3
        self.dream_level = 0.0  # 0.0 = awake, 1.0 = deep dream
        self.sanity = 100.0
        self.reality_stability = 1.0  # 1.0 = stable, 0.0 = distorted
        
        # Psycho effects
        self.glitch_timer = 0
        self.panic_mode = False
        self.panic_timer = 0
        
        # Visual effects
        self.breathing_effect = 0
        self.breathing_direction = 1
        
        # World reference
        self.world = world
        
        # Initialize position
        self.position = Vec3(5.5, 1, 5.5)
    
    def update(self):
        # Call parent update
        super().update()
        
        # Update dream effects
        self.update_dream_effects()
        self.update_psycho_effects()
        self.update_ui()
    
    def update_dream_effects(self):
        """Update dream level based on environment"""
        # Get dream effect at current position
        if self.world:
            effect, intensity = self.world.get_dream_effect_at(self.position.x, self.position.z)
        else:
            effect, intensity = None, 0.0
        
        if effect:
            if effect == 'slow':
                self.speed = max(1, 3 * (1 - intensity * 0.5))
            elif effect == 'fast':
                self.speed = min(8, 3 * (1 + intensity * 0.5))
            elif effect == 'glitch':
                self.glitch_timer = max(self.glitch_timer, intensity * 2.0)
            elif effect == 'panic':
                self.panic_mode = True
                self.panic_timer = intensity * 5.0
                self.sanity = max(0, self.sanity - intensity * 0.1)
        
        # Gradually return to normal when not in dream zones
        if not effect:
            self.speed = 3  # Reset to normal speed
    
    def update_psycho_effects(self):
        """Update psychological effects"""
        # Update glitch effect
        if self.glitch_timer > 0:
            self.glitch_timer -= time.dt
            # Add random distortion
            if random.random() < 0.1:
                self.rotation_y += random.uniform(-2, 2)
        
        # Update panic mode
        if self.panic_mode:
            self.panic_timer -= time.dt
            if self.panic_timer <= 0:
                self.panic_mode = False
        
        # Update breathing effect
        self.breathing_direction *= -1 if abs(self.breathing_effect) > 0.1 else 1
        self.breathing_effect += self.breathing_direction * 0.5 * time.dt
        self.breathing_effect = max(-0.1, min(0.1, self.breathing_effect))
        
        # Apply breathing effect to camera
        self.y += self.breathing_effect * 0.1
    
    def update_ui(self):
        """Update UI elements"""
        # This would update health, sanity, etc. in a real implementation
        pass


class PsychoBackroomsGame:
    def __init__(self):
        # Initialize Ursina app
        self.app = Ursina()
        
        # Set window properties
        window.title = 'Psycho Backrooms - Ursina'
        window.borderless = False
        window.fullscreen = False
        window.exit_button.visible = False
        window.fps_counter.enabled = True
        
        # Create game objects
        self.world = BackroomsWorld(seed=42)
        self.player = DreamPlayer(world=self.world)
        
        # Create the backrooms environment
        self.create_backrooms()
        
        # Create UI elements
        self.create_ui()
        
        # Audio (if available)
        self.setup_audio()
        
        # Game state
        self.game_paused = False
        self.dream_messages = [
            "you are safe here...",
            "the walls breathe softly...",
            "listen to the hum...",
            "time flows like honey...",
            "reality is gentle...",
            "you belong here...",
            "the dream protects you...",
            "soft edges, soft mind...",
            "the walls are watching...",
            "something moves in the distance...",
            "the fluorescent lights flicker...",
            "you hear footsteps behind you...",
            "the temperature drops...",
            "your sanity is fading...",
            "the exit is always one room away..."
        ]
        self.current_message = random.choice(self.dream_messages)
        self.message_timer = 0
        
        # Bind input
        self.setup_input()
    
    def create_backrooms(self):
        """Create the backrooms environment"""
        # Create a grid of rooms based on the world generation
        chunk_size = 16
        world_size = 20  # 20x20 chunks
        
        for chunk_x in range(-world_size//2, world_size//2):
            for chunk_y in range(-world_size//2, world_size//2):
                chunk = self.world.generate_chunk(chunk_x, chunk_y, chunk_size)
                
                for x in range(chunk_size):
                    for y in range(chunk_size):
                        world_x = chunk_x * chunk_size + x
                        world_y = chunk_y * chunk_size + y
                        
                        cell_type = chunk[y][x]
                        
                        # Create walls where needed
                        if cell_type == 1:  # Wall
                            wall = Entity(
                                model='cube',
                                color=color.white,
                                scale=(1, 3, 1),
                                position=(world_x, 1.5, world_y),
                                collider='box',
                                texture='white_cube',
                                texture_scale=(0.5, 0.5)
                            )
                            # Add subtle color variation to walls
                            wall.color = color.rgb(
                                random.randint(230, 255),
                                random.randint(220, 240),
                                random.randint(200, 220)
                            )
                        elif cell_type in [2, 3, 4, 5]:  # Room types
                            # Create floor
                            floor = Entity(
                                model='cube',
                                color=color.white,
                                scale=(1, 0.1, 1),
                                position=(world_x, 0, world_y),
                                collider='box',
                                texture='white_cube',
                                texture_scale=(0.5, 0.5)
                            )
                            # Add subtle color variation to floors
                            floor.color = color.rgb(
                                random.randint(240, 255),
                                random.randint(230, 250),
                                random.randint(210, 230)
                            )
        
        # Create ceiling
        ceiling = Entity(
            model='plane',
            color=color.white,
            scale=(world_size * chunk_size, 1, world_size * chunk_size),
            position=(0, 3, 0),
            rotation=(0, 0, 180),
            texture='white_cube',
            texture_scale=(world_size * chunk_size * 0.1, world_size * chunk_size * 0.1)
        )
        ceiling.color = color.rgb(255, 255, 245)  # Slightly off-white ceiling
        
        # Add some random details to make it more interesting
        self.add_details()
        
        # Add lighting
        DirectionalLight().look_at(Vec3(1, -1, -1))
        AmbientLight(color=color.rgba(100, 100, 100, 255))
    
    def add_details(self):
        """Add additional details to make the backrooms more interesting"""
        # Add some random fluorescent lights
        for i in range(50):
            x = random.randint(-50, 50)
            z = random.randint(-50, 50)
            # Only place lights in open areas
            if self.world.get_cell(x, z) != 1:  # Not a wall
                light = Entity(
                    model='cube',
                    color=color.yellow,
                    scale=(0.2, 0.1, 0.2),
                    position=(x, 2.9, z),
                    texture='white_cube'
                )
                light.color = color.rgb(255, 255, 200)  # Warm light
        
        # Add some random objects to make it feel more eerie
        for i in range(30):
            x = random.randint(-50, 50)
            z = random.randint(-50, 50)
            if self.world.get_cell(x, z) != 1:  # Not a wall
                obj_type = random.choice(['chair', 'table', 'box'])
                if obj_type == 'chair':
                    chair = Entity(
                        model='cube',
                        color=color.brown,
                        scale=(0.5, 0.8, 0.5),
                        position=(x, 0.4, z),
                        texture='white_cube'
                    )
                    chair.color = color.rgb(139, 69, 19)  # Brown
                elif obj_type == 'table':
                    table = Entity(
                        model='cube',
                        color=color.gray,
                        scale=(1.2, 0.2, 0.8),
                        position=(x, 0.6, z),
                        texture='white_cube'
                    )
                    table.color = color.rgb(200, 200, 200)  # Gray
                elif obj_type == 'box':
                    box = Entity(
                        model='cube',
                        color=color.gray,
                        scale=(0.6, 0.6, 0.6),
                        position=(x, 0.3, z),
                        texture='white_cube'
                    )
                    box.color = color.rgb(180, 180, 180)  # Light gray
    
    def create_ui(self):
        """Create UI elements"""
        # Dream message
        self.message_text = Text(
            text=self.current_message,
            origin=(0, 0),
            position=(-0.8, 0.4),
            scale=1.5,
            color=color.orange
        )
        
        # Player status
        self.status_text = Text(
            text="",
            origin=(0, 0),
            position=(-0.8, -0.4),
            scale=1.2,
            color=color.white
        )
        
        # Controls help
        self.controls_text = Text(
            text="WASD: Move | Mouse: Look | ESC: Quit",
            origin=(0, 0),
            position=(0.7, -0.45),
            scale=0.8,
            color=color.gray
        )
    
    def setup_audio(self):
        """Setup audio system"""
        # Placeholder for audio implementation
        pass
    
    def setup_input(self):
        """Setup input handling"""
        self.input_handler = InputHandler()
        self.input_handler.bind('escape', 'quit_game')
    
    def update_ui(self):
        """Update UI elements"""
        # Update dream message periodically
        self.message_timer += time.dt
        if self.message_timer > 5:  # Change message every 5 seconds
            self.current_message = random.choice(self.dream_messages)
            self.message_text.text = self.current_message
            self.message_timer = 0
        
        # Update player status
        self.status_text.text = f"POS: {self.player.position.x:.1f}, {self.player.position.z:.1f}\nDREAM: {self.player.dream_level:.1f}\nSANITY: {self.player.sanity:.0f}%"
    
    def input(self, key):
        """Handle input"""
        if key == 'escape':
            application.quit()
    
    def update(self):
        """Main update loop"""
        if not self.game_paused:
            self.update_ui()
    
    def run(self):
        """Run the game"""
        self.app.run()


if __name__ == "__main__":
    game = PsychoBackroomsGame()
    game.run()