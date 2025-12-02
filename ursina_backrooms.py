import json
import random
from ursina import Ursina, Entity, Vec3, color, held_keys, mouse, camera, time, destroy, Text, Sky, DirectionalLight


def rgb_to_color(rgb_list):
    """Convert RGB list to Ursina color object"""
    if len(rgb_list) >= 3:
        return color.rgb(rgb_list[0], rgb_list[1], rgb_list[2])
    else:
        return color.white


class PsychoBackroomsGame:
    def __init__(self):
        self.app = Ursina()
        self.player = None
        self.world_data = {}
        self.loaded_chunks = {}
        self.dream_messages = [
            "The walls are breathing...",
            "You feel a presence watching you...",
            "Reality feels unstable here...",
            "Something is not right...",
            "The silence is deafening...",
            "Time moves differently here...",
            "You're not alone...",
            "The walls whisper...",
            "You feel lost...",
            "The fluorescent lights flicker...",
            "Your sanity is slipping...",
            "The air tastes strange...",
            "You can't remember how you got here...",
            "The rooms repeat endlessly...",
            "Your footsteps echo...",
            "The walls seem to pulse...",
            "You hear breathing...",
            "The temperature drops...",
            "You feel dizzy...",
            "The lights dim..."
        ]
        self.current_message = ""
        self.message_timer = 0
        self.sanity = 75
        self.reality_stability = 80
        self.speed_effects = []
        self.glitch_effects = []
        self.panic_effects = []

        # Load world data
        self.load_world_data()
        self.setup_game()

    def load_world_data(self):
        """Load pre-generated world data"""
        try:
            with open('generated_world.json', 'r') as f:
                self.world_data = json.load(f)
            print(f"Loaded {len(self.world_data)} rooms from generated_world.json")
        except FileNotFoundError:
            print("Error: generated_world.json not found. Please run generate_rooms.py first.")
            exit()

    def setup_game(self):
        """Setup game environment"""
        # Sky and lighting
        Sky(color=color.dark_gray)

        # Directional light for better visibility
        self.directional_light = DirectionalLight()
        self.directional_light.look_at(Vec3(-1, -1, -1))
        self.directional_light.color = color.white
        self.directional_light.intensity = 0.5

        # Ground plane
        Entity(model='plane', scale=100, texture='white_cube', texture_scale=(100, 100),
               rotation_x=90, color=color.gray)

        # Player setup
        self.player = Entity(model='cube', color=color.blue, scale=1, collider='box')
        self.player.y = 1.5  # Eye level

        # Camera setup
        camera.parent = self.player
        camera.position = Vec3(0, 0, 0)
        camera.rotation = Vec3(0, 0, 0)

        # Load initial chunks around player
        self.load_chunks_around_player()

        # Initial dream message
        self.update_dream_message()

        # UI
        self.status_text = Text(
            position=Vec3(-0.8, 0.4, 0),
            scale=1.5,
            color=color.white
        )
        self.message_text = Text(
            position=Vec3(0, 0.3, 0),
            scale=2,
            color=color.orange,
            origin=(0, 0)
        )

        # Game loop
        self.app.update = self.update

    def load_chunks_around_player(self):
        """Load chunks around player position"""
        px, pz = int(self.player.x), int(self.player.z)

        # Clear existing chunks
        for chunk in self.loaded_chunks.values():
            for entity in chunk:
                destroy(entity)
        self.loaded_chunks.clear()

        # Load new chunks (3x3 grid around player)
        for x in range(px - 1, px + 2):
            for z in range(pz - 1, pz + 2):
                self.load_chunk(x, z)

    def load_chunk(self, chunk_x, chunk_z):
        """Load a single chunk from pre-generated data"""
        entities = []

        # Generate rooms in this chunk
        for dx in range(2):
            for dz in range(2):
                room_x = chunk_x * 2 + dx
                room_z = chunk_z * 2 + dz
                room_key = f"{room_x},{room_z}"

                if room_key in self.world_data:
                    room = self.world_data[room_key]
                    room_entities = self.create_room(room_x, room_z, room)
                    entities.extend(room_entities)

        self.loaded_chunks[(chunk_x, chunk_z)] = entities

    def create_room(self, x, z, room_data):
        """Create a room based on pre-generated data"""
        entities = []

        # Floor
        floor_color = rgb_to_color(room_data['floor_color'])
        floor = Entity(
            model='plane',
            scale=10,
            position=Vec3(x * 10, 0, z * 10),
            rotation=Vec3(90, 0, 0),
            color=floor_color,
            collider='mesh'
        )
        entities.append(floor)

        # Ceiling
        ceiling = Entity(
            model='plane',
            scale=10,
            position=Vec3(x * 10, 5, z * 10),
            rotation=Vec3(-90, 0, 0),
            color=color.gray,
            collider='mesh'
        )
        entities.append(ceiling)

        # Walls
        wall_color = rgb_to_color(room_data['wall_color'])
        wall_positions = [
            (x * 10, 2.5, z * 10 + 5),  # North
            (x * 10, 2.5, z * 10 - 5),  # South
            (x * 10 + 5, 2.5, z * 10),  # East
            (x * 10 - 5, 2.5, z * 10)  # West
        ]

        for pos in wall_positions:
            wall = Entity(
                model='cube',
                scale=(10, 5, 1),
                position=pos,
                color=wall_color,
                collider='box'
            )
            entities.append(wall)

        # Furniture
        furniture_colors = {
            'chair': color.brown,
            'table': color.brown,
            'lamp': color.yellow,
            'plant': color.green,
            'bookshelf': color.brown,
            'couch': color.red
        }

        for furn in room_data['furniture']:
            furn_color = furniture_colors.get(furn['type'], color.brown)
            furn_entity = Entity(
                model='cube',
                scale=1,
                position=Vec3(
                    x * 10 + furn['position'][0],
                    furn['position'][1],
                    z * 10 + furn['position'][2]
                ),
                rotation_y=furn['rotation'],
                color=furn_color
            )
            entities.append(furn_entity)

        # Light
        if room_data['has_light'] and room_data['light']:
            light_color = rgb_to_color(room_data['light']['color'])
            light_entity = Entity(
                model='sphere',
                scale=0.2,
                position=Vec3(x * 10, 4, z * 10),
                color=light_color
            )
            entities.append(light_entity)

        # Apply dream zone effects
        if room_data['dream_zone']:
            self.apply_dream_zone_effects(x, z, room_data['dream_effects'])

        return entities

    def apply_dream_zone_effects(self, x, z, effects):
        """Apply dream zone effects to player"""
        for effect in effects:
            if effect == 'slow':
                self.speed_effects.append((x, z, time.time() + 5))
            elif effect == 'fast':
                self.speed_effects.append((x, z, time.time() + 5))
            elif effect == 'glitch':
                self.glitch_effects.append((x, z, time.time() + 3))
            elif effect == 'panic':
                self.panic_effects.append((x, z, time.time() + 4))

    def update_dream_message(self):
        """Update dream message periodically"""
        self.current_message = random.choice(self.dream_messages)
        self.message_timer = 5  # Show for 5 seconds

    def update(self):
        """Main game update loop"""
        # Player movement
        self.player.y = 1.5  # Maintain eye level
        speed = 5 * time.dt

        # Apply speed effects
        player_chunk_x = int(self.player.x // 20)
        player_chunk_z = int(self.player.z // 20)

        for x, z, end_time in self.speed_effects:
            if time.time() < end_time and abs(player_chunk_x - x // 10) <= 1 and abs(player_chunk_z - z // 10) <= 1:
                room_key = f"{x},{z}"
                if room_key in self.world_data:
                    room = self.world_data[room_key]
                    if 'fast' in room.get('dream_effects', []):
                        speed *= 1.5
                    elif 'slow' in room.get('dream_effects', []):
                        speed *= 0.7

        # Movement with WASD
        if held_keys['w']:
            self.player.position += self.player.forward * speed
        if held_keys['s']:
            self.player.position -= self.player.forward * speed
        if held_keys['a']:
            self.player.position -= self.player.right * speed
        if held_keys['d']:
            self.player.position += self.player.right * speed

        # Mouse look
        camera.rotation_y += mouse.velocity[0] * 100 * time.dt
        camera.rotation_x -= mouse.velocity[1] * 100 * time.dt
        camera.rotation_x = max(min(camera.rotation_x, 90), -90)

        # Check if player moved to new chunk
        chunk_x = int(self.player.x // 20)
        chunk_z = int(self.player.z // 20)
        if (chunk_x, chunk_z) not in self.loaded_chunks:
            self.load_chunks_around_player()

        # Update dream message timer
        if self.message_timer > 0:
            self.message_timer -= time.dt
            self.message_text.text = self.current_message
            if self.message_timer <= 0:
                self.message_text.text = ""
        else:
            if random.random() < 0.001:  # 0.1% chance per frame
                self.update_dream_message()

        # Update status text
        self.status_text.text = f"Sanity: {int(self.sanity)}%\nReality: {int(self.reality_stability)}%"

        # Apply psychological effects
        if random.random() < 0.0005:  # Random sanity drain
            self.sanity = max(0, self.sanity - 0.1)
        if random.random() < 0.0005:  # Random reality instability
            self.reality_stability = max(0, self.reality_stability - 0.1)

        # Handle glitch effects
        for x, z, end_time in self.glitch_effects[:]:
            if time.time() >= end_time:
                self.glitch_effects.remove((x, z, end_time))

        # Handle panic effects
        for x, z, end_time in self.panic_effects[:]:
            if time.time() >= end_time:
                self.panic_effects.remove((x, z, end_time))


if __name__ == "__main__":
    game = PsychoBackroomsGame()
    game.app.run()