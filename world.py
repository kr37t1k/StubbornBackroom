# world.py - Infinite procedural Backrooms world
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