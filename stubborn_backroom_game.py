from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import math

app = Ursina(borderless=False)

# 🌸 CUTE DREAMY COLOR PALETTE (FIXED: Use hsv() instead of color())
DREAM_YELLOW = color.hsv(45, 0.15, 0.95)  # Soft cream
WARM_BEIGE = color.hsv(35, 0.1, 0.98)  # Gentle beige
SOFT_BLUE = color.hsv(200, 0.2, 0.9)  # Dreamy blue accents

# 🌌 DREAMY FOG AND ATMOSPHERE
scene.fog_color = WARM_BEIGE.tint(-0.3)
scene.fog_density = 0.02


# 🌀 REALITY DISTORTION SYSTEM
class RealityDistortion:
    def __init__(self):
        self.distortion_level = 0.0
        self.wave_offset = 0
        self.reality_stability = 1.0

    def update(self, dt):
        self.wave_offset += dt * 0.5
        # Reality becomes less stable the longer you stay in one place
        if not player.moved_recently:
            self.reality_stability = max(0.3, self.reality_stability - dt * 0.1)
        else:
            self.reality_stability = min(1.0, self.reality_stability + dt * 0.2)

        self.distortion_level = (1.0 - self.reality_stability) * 0.3


reality = RealityDistortion()


# 🏠 PROCEDURAL BACKROOMS GENERATOR (NO TEXTURES! - FIXED WITH DOORS & CEILINGS)
class BackroomsGenerator:
    def __init__(self):
        self.room_size = 5  # Slightly larger for doorways
        self.wall_height = 5
        self.ceiling_height = 3.5  # Ceiling sits below wall tops
        self.generated_positions = set()
        self.room_connections = {}  # Track connections between rooms
        self.last_generation_position = (0, 0)

    def generate_around_player(self, player_position):
        player_chunk = (
            math.floor(player_position.x / self.room_size),
            math.floor(player_position.z / self.room_size)
        )

        # Only regenerate if player moved to a new chunk
        if player_chunk == self.last_generation_position:
            return

        self.last_generation_position = player_chunk

        # Generate 3x3 grid of rooms around player
        for x in range(-2, 3):  # Larger generation radius
            for z in range(-2, 3):
                chunk_x = player_chunk[0] + x
                chunk_z = player_chunk[1] + z
                chunk_pos = (chunk_x, chunk_z)

                if chunk_pos not in self.generated_positions:
                    self.generate_room(chunk_x, chunk_z)
                    self.generated_positions.add(chunk_pos)

    def generate_room(self, x, z):
        room_center = Vec3(x * self.room_size, 0, z * self.room_size)
        room_key = (x, z)

        # ✅ FIXED: Create room type with connections
        room_type = self._determine_room_type(x, z)
        connection_directions = self._get_room_connections(x, z, room_type)

        # Create floor
        floor = Entity(
            model='plane',
            scale=(self.room_size, 1, self.room_size),
            position=room_center + Vec3(0, -0.1, 0),
            color=DREAM_YELLOW.tint(-0.1),
            collider='box'
        )

        # ✅ FIXED: Create ceiling (Backrooms signature!)
        ceiling = Entity(
            model='plane',
            scale=(self.room_size, 1, self.room_size),
            position=room_center + Vec3(0, self.ceiling_height, 0),
            rotation=(180, 0, 0),  # Flip to face downward
            color=DREAM_YELLOW.tint(0.1),  # Slightly lighter
            collider='box'
        )

        # Create ceiling glow effect
        ceiling_glow = Entity(
            model='plane',
            parent=ceiling,
            scale=(self.room_size + 0.1, 1, self.room_size + 0.1),
            color=color.rgba(255, 250, 230, 30),
            unlit=True
        )

        # Create walls with doorways
        self._create_walls_with_doorways(room_center, room_type, connection_directions)

    def _determine_room_type(self, x, z):
        """Determine room type based on position and neighbors"""
        # More hallways near origin, more rooms further out
        distance = math.sqrt(x * x + z * z)

        if distance < 3:
            return 'junction'  # Central area has more connections
        elif distance < 6:
            return random.choice(['hallway', 'corner', 'junction'])
        else:
            return random.choice(['hallway', 'room', 'corner'])

    def _get_room_connections(self, x, z, room_type):
        """Determine which directions have doorways"""
        connections = []

        # Base connections based on room type
        if room_type == 'junction':
            connections = ['north', 'south', 'east', 'west']
        elif room_type == 'hallway':
            # Hallways connect in two opposite directions
            if random.random() < 0.5:
                connections = ['north', 'south']
            else:
                connections = ['east', 'west']
        elif room_type == 'corner':
            # Corners connect in two adjacent directions
            choices = [
                ['north', 'east'],
                ['east', 'south'],
                ['south', 'west'],
                ['west', 'north']
            ]
            connections = random.choice(choices)
        elif room_type == 'room':
            # Rooms have 1-2 doors
            directions = ['north', 'south', 'east', 'west']
            random.shuffle(directions)
            connections = directions[:random.randint(1, 2)]

        # Ensure at least one connection for edge rooms
        if not connections:
            connections = random.choice([['north'], ['south'], ['east'], ['west']])

        return connections

    def _create_walls_with_doorways(self, room_center, room_type, connections):
        """Create walls with doorways in connected directions"""
        door_positions = {
            'north': (0, self.room_size / 2 - 2),
            'south': (0, -self.room_size / 2 + 2),
            'east': (self.room_size / 2 - 2, 0),
            'west': (-self.room_size / 2 + 2, 0)
        }

        door_size = 3  # Width of doorway
        wall_thickness = 0.5

        # North wall
        if 'north' not in connections:
            self._create_wall(room_center, 'north', wall_thickness)
        else:
            # Create two wall segments with doorway in middle
            self._create_wall_segment(room_center, 'north', -self.room_size / 2, -door_size / 2, wall_thickness)
            self._create_wall_segment(room_center, 'north', door_size / 2, self.room_size / 2, wall_thickness)

        # South wall
        if 'south' not in connections:
            self._create_wall(room_center, 'south', wall_thickness)
        else:
            self._create_wall_segment(room_center, 'south', -self.room_size / 2, -door_size / 2, wall_thickness)
            self._create_wall_segment(room_center, 'south', door_size / 2, self.room_size / 2, wall_thickness)

        # East wall
        if 'east' not in connections:
            self._create_wall(room_center, 'east', wall_thickness)
        else:
            self._create_wall_segment(room_center, 'east', -self.room_size / 2, -door_size / 2, wall_thickness)
            self._create_wall_segment(room_center, 'east', door_size / 2, self.room_size / 2, wall_thickness)

        # West wall
        if 'west' not in connections:
            self._create_wall(room_center, 'west', wall_thickness)
        else:
            self._create_wall_segment(room_center, 'west', -self.room_size / 2, -door_size / 2, wall_thickness)
            self._create_wall_segment(room_center, 'west', door_size / 2, self.room_size / 2, wall_thickness)

    def _create_wall(self, center, direction, thickness):
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
            color=DREAM_YELLOW,
            collider='box'
        )

        # Add subtle variations for dreamy feel
        wall.scale += Vec3(random.uniform(-0.05, 0.05), random.uniform(-0.05, 0.05), random.uniform(-0.05, 0.05))
        wall.color = wall.color.tint(random.uniform(-0.03, 0.03))

        # Create soft glow effect
        glow = Entity(
            model='cube',
            parent=wall,
            scale=wall.scale * 1.03,
            color=color.rgba(255, 240, 220, 40),
            unlit=True
        )

        return wall

    def _create_wall_segment(self, center, direction, start_pos, end_pos, thickness):
        """Create a wall segment (part of a wall with doorway)"""
        length = end_pos - start_pos

        if direction in ['north', 'south']:
            scale = (length, self.wall_height, thickness)
            y_pos = self.wall_height / 2
            z_pos = self.room_size / 2 if direction == 'north' else -self.room_size / 2
            x_pos = (start_pos + end_pos) / 2
            position = center + Vec3(x_pos, y_pos, z_pos)
        else:  # east, west
            scale = (thickness, self.wall_height, length)
            y_pos = self.wall_height / 2
            x_pos = self.room_size / 2 if direction == 'east' else -self.room_size / 2
            z_pos = (start_pos + end_pos) / 2
            position = center + Vec3(x_pos, y_pos, z_pos)

        wall = Entity(
            model='cube',
            scale=scale,
            position=position,
            color=DREAM_YELLOW,
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


# 🧘 CUTE FIRST-PERSON CONTROLLER (FIXED: No z-axis glitching)
class DreamWalker(FirstPersonController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cursor = Entity(parent=camera.ui, model='circle', color=SOFT_BLUE, scale=0.02)
        self.moved_recently = False
        self.move_timer = 0
        self.base_height = 0.9  # Store base height separately
        self.floating = False
        self.float_speed = 1.5
        self.float_amount = 0.05
        self.jump_height = 1.0  # Lower jump for Backrooms feel

    def update(self):
        # Store previous position for movement detection
        prev_position = self.position

        # Update physics first (let parent class handle movement)
        super().update()

        # Track movement for reality stability
        distance_moved = (self.position - prev_position).length()
        if distance_moved > 0.1:
            self.moved_recently = True
            self.move_timer = 0
        else:
            self.move_timer += time.dt
            if self.move_timer > 2.0:
                self.moved_recently = False

        # ✅ FIXED: Apply floating effect as offset to base position
        float_offset = math.sin(time.time() * self.float_speed) * self.float_amount
        self.y = self.base_height + float_offset

        # Reality distortion affects movement
        self.speed = 7 * reality.reality_stability
        self.jump_height = 2.0 * reality.reality_stability

        # Keep player at ground level
        self.y = max(0.8, self.y)


# 🌸 CREATE THE DREAM WORLD
world = BackroomsGenerator()

# ✅ FIXED: Proper player setup
player = DreamWalker(
    model='cube',
    y=0.9,
    origin_y=-0.5,
    color=DREAM_YELLOW.tint(0.2),
    gravity=1.0
)

# Add starting room
world.generate_room(0, 0)
world.generated_positions.add((0, 0))


# 🌙 DREAMY SKYBOX (code-generated gradient)
class DreamSky(Entity):
    def __init__(self):
        super().__init__(
            parent=scene,
            model='sphere',
            scale=1000,
            double_sided=True,
            unlit=True
        )

        # Default vertex shader code (no external file needed)
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

        # Fragment shader for gradient sky
        fragment_shader = '''
        #version 140
        uniform vec4 p3d_ColorScale;
        in vec2 texcoord;
        out vec4 fragColor;

        uniform float time;

        void main() {
            vec2 uv = texcoord;
            float gradient = uv.y * 0.5 + 0.5;
            vec3 color = mix(vec3(0.98, 0.95, 0.85), vec3(0.92, 0.88, 0.75), gradient);

            // Add dreamy wave effect
            float wave = sin(uv.x * 10.0 + time * 0.2) * 0.01;
            color += vec3(wave);

            fragColor = vec4(color, 1.0) * p3d_ColorScale;
        }
        '''

        self.shader = Shader(language=Shader.GLSL,
                             vertex=default_vertex_shader,
                             fragment=fragment_shader
                             )

        self.set_shader_input('time', 0)

    def update(self):
        self.set_shader_input('time', time.time())


DreamSky()


# 💫 DREAM PARTICLES (code-generated)
class DreamParticles(Entity):
    def __init__(self):
        super().__init__(parent=scene)
        self.particles = []

        # Create floating dream particles
        for _ in range(30):
            particle = Entity(
                parent=self,
                model='circle',
                color=color.rgba(255, 250, 240, 100),
                scale=random.uniform(0.05, 0.15),
                position=(
                    random.uniform(-20, 20),
                    random.uniform(1, 5),
                    random.uniform(-20, 20)
                ),
                unlit=True
            )
            self.particles.append({
                'entity': particle,
                'speed': random.uniform(0.3, 0.8),
                'direction': Vec3(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)).normalized()
            })

    def update(self):
        for p in self.particles:
            # Gentle floating movement
            p['entity'].y += math.sin(time.time() * p['speed']) * 0.05
            p['entity'].x += math.sin(time.time() * 0.3) * 0.02
            p['entity'].z += math.cos(time.time() * 0.4) * 0.02

            # Pulse transparency
            alpha = 50 + math.sin(time.time() * 2) * 30
            p['entity'].color = color.rgba(255, 250, 240, alpha)


DreamParticles()


# 💭 DREAM MESSAGES (appearing gently)
class DreamMessage(Text):
    def __init__(self):
        super().__init__(
            text='',
            origin=(0, 0),
            y=-0.4,
            color=WARM_BEIGE.tint(0.2),
            scale=1.5,
            alpha=0
        )
        self.messages = [
            "you are safe here...",
            "the walls breathe softly...",
            "listen to the hum...",
            "time flows like honey...",
            "reality is gentle...",
            "you belong here...",
            "the dream protects you...",
            "soft edges, soft mind...",
            "breathe in, breathe out...",
            "the yellow is warm...",
            "the ceiling watches...",
            "find the next room...",
            "the doors remember you..."
        ]
        self.current_message = ""
        self.timer = 0
        self.fade_timer = 0

    def update(self):
        self.timer += time.dt

        # Change message every 8 seconds
        if self.timer > 8 and not self.fade_timer:
            self.current_message = random.choice(self.messages)
            self.text = self.current_message
            self.fade_timer = 1.0  # Start fading in
            self.timer = 0

        # Fade in/out
        if self.fade_timer > 0:
            self.fade_timer -= time.dt
            if self.fade_timer > 0.5:
                # Fade in
                self.alpha = min(1.0, self.alpha + time.dt * 2)
            else:
                # Fade out
                self.alpha = max(0.0, self.alpha - time.dt * 2)
                if self.alpha <= 0:
                    self.text = ''
                    self.current_message = ''


DreamMessage()


# 🎮 INPUT HANDLING
def input(key):
    if key == 'escape':
        application.quit()

    if key == 'tab':
        # Toggle dream view (slows time, enhances colors)
        if application.time_scale == 1.0:
            application.time_scale = 0.3
            scene.fog_density = 0.05
            scene.fog_color = SOFT_BLUE.tint(-0.4)
        else:
            application.time_scale = 1.0
            scene.fog_density = 0.02
            scene.fog_color = WARM_BEIGE.tint(-0.3)

    if key == 'f1':
        # Toggle wireframe for development
        scene.show_wireframe = not scene.show_wireframe


# 🌟 MAIN UPDATE LOOP
def update():
    reality.update(time.dt)
    world.generate_around_player(player.position)

    # Reality distortion affects the whole scene
    if reality.distortion_level > 0:
        # Subtle screen shake
        camera.x = math.sin(time.time() * 5) * reality.distortion_level * 0.01
        camera.z = math.cos(time.time() * 3) * reality.distortion_level * 0.01

        # ✅ FIXED: Use hsv() consistently for fog color
        scene.fog_color = color.hsv(
            35 + reality.distortion_level * 20,
            0.1,
            0.98 - reality.distortion_level * 0.1
        )


# 🎬 START THE DREAM
scene.background_color = WARM_BEIGE.tint(-0.4)
window.title = 'StubbornBackrooms • A Psycho Dream'
window.fps_counter.enabled = True
window.exit_button.visible = False

# ✅ FIXED: Set proper window size to avoid warnings
window.size = (1280, 720)
window.position = (100, 100)

# Start player in a hallway for better initial experience
player.position = Vec3(0, 0.9, 0)

app.run()