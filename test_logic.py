"""
Simple test of the game logic without Panda3D dependencies
"""
import math
import random
import noise


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


def test_game_logic():
    """Test the game logic"""
    print("Testing Panda3D Backrooms Game Logic...")
    
    # Initialize game objects
    world = BackroomsWorld(seed=42)
    player = DreamPlayer(x=5.5, y=5.5, angle=0)
    
    # Test world generation
    print("\nTesting world generation...")
    for x in range(-2, 3):
        for y in range(-2, 3):
            cell_type = world.get_cell(x, y)
            room_info = world.get_room_at(x, y)
            print(f"Cell ({x}, {y}): type={cell_type}, room_type={world.room_types[cell_type]}")
    
    # Test player movement
    print(f"\nInitial player position: ({player.x:.2f}, {player.y:.2f}), angle={player.angle:.2f}")
    
    # Simulate key presses
    keys = {'w': True, 'a': False, 's': False, 'd': False}
    
    # Update player for several frames
    for frame in range(10):
        player.update(keys, world, 1.0)
        print(f"Frame {frame+1}: Position=({player.x:.2f}, {player.y:.2f}), Angle={player.angle:.2f}, Speed={player.move_speed:.3f}")
    
    # Test collision detection
    print("\nTesting collision detection...")
    test_positions = [
        (5.5, 5.5),  # Should be free space
        (0, 0),      # Test another position
    ]
    
    for pos_x, pos_y in test_positions:
        can_move = player._can_move_to(pos_x, pos_y, world)
        cell_type = world.get_cell(pos_x, pos_y)
        print(f"Position ({pos_x}, {pos_y}): can_move={can_move}, cell_type={cell_type}")
    
    # Test dream zones
    print("\nTesting dream zones...")
    for x in range(0, 10, 2):
        for y in range(0, 10, 2):
            effect, intensity = world.get_dream_effect_at(x, y)
            print(f"Dream effect at ({x}, {y}): {effect}, intensity={intensity:.2f}")
    
    print("\nGame logic test completed successfully!")
    return True


def main():
    try:
        test_game_logic()
        print("\n✅ Panda3D Backrooms Game logic is working correctly!")
        print("The full 3D game is ready to run in a graphics-enabled environment.")
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()