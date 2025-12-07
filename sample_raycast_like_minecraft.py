from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import math
import gc

# 🌸 CUTE COLOR PALETTE
SOFT_PINK = color.hsv(340, 0.2, 0.95)
CREAM = color.hsv(40, 0.1, 0.92)
MINT = color.hsv(160, 0.3, 0.85)
LAVENDER = color.hsv(270, 0.25, 0.88)
WARM_YELLOW = color.hsv(45, 0.15, 0.95)

app = Ursina(
    title="•••",
    forced_aspect_ratio=16 / 9,
    vsync=True,  # Enable for smoother experience
    render_mode='default'
)


# 🧸 CUTE OPTIMIZED VOXEL (Memory efficient)
class DreamVoxel(Button):
    # Shared mesh and texture for memory efficiency
    _mesh = None
    _texture = None

    def __init__(self, position=(0, 0, 0), voxel_type='normal'):
        # Create shared resources only once
        if DreamVoxel._mesh is None:
            DreamVoxel._mesh = load_model('cube')
        if DreamVoxel._texture is None:
            DreamVoxel._texture = 'white_cube'

        # CUTE COLORS BY TYPE
        colors = {
            'normal': CREAM,
            'special': SOFT_PINK,
            'growth': MINT,
            'dream': LAVENDER,
            'warning': color.hsv(30, 0.3, 0.9)
        }

        # GENTLE GLOW EFFECT
        glow_colors = {
            'normal': color.rgba(255, 245, 235, 15),
            'special': color.rgba(255, 230, 240, 25),
            'growth': color.rgba(230, 255, 240, 20),
            'dream': color.rgba(240, 230, 255, 30),
            'warning': color.rgba(255, 240, 230, 20)
        }

        super().__init__(
            parent=scene,
            position=position,
            model=DreamVoxel._mesh,  # Shared mesh
            origin_y=0.5,
            texture=DreamVoxel._texture,  # Shared texture
            color=colors.get(voxel_type, CREAM),
            highlight_color=colors[voxel_type].tint(0.2),
            collider='box',
            scale=0.98  # Slight gap for floating effect
        )

        # Add soft glow
        self.glow = Entity(
            parent=self,
            model='cube',
            scale=1.04,
            color=glow_colors.get(voxel_type, glow_colors['normal']),
            unlit=True
        )

        self.voxel_type = voxel_type
        self.created_time = time.time()

    def destroy(self, delay=0):
        # Clean up glow entity
        if hasattr(self, 'glow') and self.glow:
            destroy(self.glow)
        destroy(self, delay)


# 🌈 OPTIMIZED WORLD GENERATION (Chunk-based)
class DreamWorld:
    def __init__(self):
        self.chunk_size = 32
        self.loaded_chunks = {}
        self.max_chunks = 8  # Memory limit
        self.voxels = []  # Track all voxels for cleanup

    def generate_chunk(self, chunk_x, chunk_z):
        """Generate a chunk of voxels"""
        chunk_key = (chunk_x, chunk_z)
        if chunk_key in self.loaded_chunks:
            return

        # Create chunk node for easy cleanup
        chunk_node = Entity(name=f'chunk_{chunk_x}_{chunk_z}')
        chunk_voxels = []

        # Generate voxels with cute patterns
        for x in range(self.chunk_size):
            for z in range(self.chunk_size):
                world_x = chunk_x * self.chunk_size + x
                world_z = chunk_z * self.chunk_size + z

                # Create floor
                voxel = DreamVoxel(
                    position=(world_x, 0, world_z),
                    voxel_type=self._get_voxel_type(world_x, world_z)
                )
                chunk_voxels.append(voxel)
                self.voxels.append(voxel)

        chunk_node.children = chunk_voxels
        self.loaded_chunks[chunk_key] = chunk_node

        # Manage memory - unload old chunks
        self._manage_memory()

    def _get_voxel_type(self, x, z):
        """Get voxel type based on position for cute patterns"""
        # Center area - special voxels
        if abs(x) < 3 and abs(z) < 3:
            return 'special'

        # Spiral pattern
        angle = math.atan2(z, x)
        radius = math.sqrt(x * x + z * z)
        spiral_value = (radius * 0.5 + angle) % 4

        if spiral_value < 1:
            return 'growth'
        elif spiral_value < 2:
            return 'dream'
        elif spiral_value < 3:
            return 'normal'
        else:
            return 'warning'

    def _manage_memory(self):
        """Unload chunks when over memory limit"""
        if len(self.loaded_chunks) <= self.max_chunks:
            return

        # Unload oldest chunk
        oldest_key = min(self.loaded_chunks.keys(),
                         key=lambda k: self.loaded_chunks[k].created_time
                         if hasattr(self.loaded_chunks[k], 'created_time') else 0)

        chunk = self.loaded_chunks[oldest_key]
        destroy(chunk)
        del self.loaded_chunks[oldest_key]

        # Force garbage collection
        gc.collect()

    def cleanup(self):
        """Clean up all voxels"""
        for voxel in self.voxels[:]:
            destroy(voxel)
        self.voxels.clear()
        for chunk in self.loaded_chunks.values():
            destroy(chunk)
        self.loaded_chunks.clear()


# 🧘 CUTE PLAYER CONTROLLER
class DreamWalker(FirstPersonController):
    def __init__(self):
        super().__init__()
        # CUTE PLAYER APPEARANCE
        self.model = 'cube'
        self.color = SOFT_PINK.tint(0.1)
        self.scale = (0.8, 1.6, 0.8)
        self.position = (0, 2, 0)

        # DREAMY PARTICLE TRAIL
        self.particles = []
        self.particle_timer = 0

        # SAVE POINT SYSTEM
        self.save_point = Vec3(0, 2, 0)

        # OPTIMIZED PHYSICS
        self.speed = 6
        self.jump_height = 2
        self.gravity = 0.8

        # FLOATING EFFECT
        self.float_offset = 0
        self.float_speed = 1.2
        self.float_amount = 0.1

    def update(self):
        super().update()

        # FLOATING EFFECT
        self.float_offset = math.sin(time.time() * self.float_speed) * self.float_amount
        self.y = max(1, self.y + self.float_offset)

        # PARTICLE TRAIL (optimized)
        self.particle_timer += time.dt
        if self.particle_timer > 0.2 and (abs(self.direction[0]) > 0.1 or abs(self.direction[2]) > 0.1):
            self.create_particle()
            self.particle_timer = 0

    def create_particle(self):
        """Create cute floating particles"""
        if len(self.particles) > 10:  # Limit particles for performance
            return

        particle = Entity(
            parent=scene,
            model='circle',
            color=color.rgba(255, 240, 250, 150),
            scale=random.uniform(0.05, 0.1),
            position=self.position + Vec3(
                random.uniform(-0.5, 0.5),
                random.uniform(0, 1),
                random.uniform(-0.5, 0.5)
            ),
            unlit=True
        )

        # Float upward and fade
        particle.animate_y(particle.y + 2, duration=1.5)
        particle.animate_color(particle.color.tint(0.2), duration=1.5)
        particle.animate_scale(0, duration=1.5)
        destroy(particle, delay=1.5)

        self.particles.append(particle)

        # Cleanup
        self.particles = [p for p in self.particles if p.enabled]


# 🌟 DREAMY ENVIRONMENT
class DreamEnvironment:
    def __init__(self):
        # SOFT SKYBOX
        Sky(color=color.hsv(220, 0.05, 0.95))

        # GENTLE FOG
        scene.fog_color = CREAM.tint(-0.2)
        scene.fog_density = 0.01

        # AMBIENT LIGHT
        AmbientLight(color=color.hsv(220, 0.1, 0.7))

        # DIRECTIONAL LIGHT (soft shadows)
        self.sun = DirectionalLight(shadows=True, shadow_map_resolution=[1024,1024])
        self.sun.look_at(Vec3(-1, -1, 1))
        self.sun.color = color.hsv(220, 0.2, 0.8)

    def update(self):
        # Subtle sun movement for day/night cycle
        angle = time.time() * 0.001
        self.sun.look_at(Vec3(-math.cos(angle), -0.5, -math.sin(angle)))


# ⭐ CUTENESS SYSTEM
class CutenessManager:
    def __init__(self):
        self.messages = [
            "you're doing great! ",
            "so soft, so dreamy... ",
            "take your time, little friend ",
            "the world is gentle here... ",
            "breathe in, breathe out... ️",
            "you belong in this dream... "
        ]
        self.current_message = ""
        self.display_time = 0
        self.message_timer = 0

    def show_message(self, message=None):
        """Show a cute message"""
        if message:
            self.current_message = message
        else:
            self.current_message = random.choice(self.messages)

        self.display_time = time.time()
        self.message_timer = 3  # Show for 3 seconds

    def update(self):
        if self.message_timer > 0:
            self.message_timer -= time.dt

            # Fade text
            alpha = (self.message_timer / 3) * 0.8 + 0.2
            cute_text.color = color.rgba(255, 240, 245, alpha * 255)

    def cleanup(self):
        destroy(cute_text)


# 🎮 INPUT HANDLER (Optimized)
def input(key):
    if key == 'right mouse down':
        hit_info = raycast(camera.world_position, camera.forward, distance=8)
        if hit_info.hit:
            # CUTE PLACEMENT EFFECT
            voxel = DreamVoxel(
                position=hit_info.entity.position + hit_info.normal,
                voxel_type=random.choice(['normal', 'growth', 'dream'])
            )
            world.voxels.append(voxel)

            # Show success message
            cuteness.show_message("new friend added! ")

    elif key == 'left mouse down' and mouse.hovered_entity:
        destroy(mouse.hovered_entity)
        # Remove from world tracking
        if mouse.hovered_entity in world.voxels:
            world.voxels.remove(mouse.hovered_entity)
        cuteness.show_message("gentle goodbye... ")

    elif key == 'e':
        # OPTIMIZED BULLET (single entity reuse)
        if not hasattr(input, 'bullet') or not input.bullet.enabled:
            input.bubble = Entity(
                parent=camera,
                model='circle',
                scale=0.2,
                color=color.rgba(100, 200, 255, 200),
                unlit=True
            )

        bullet = input.bubble
        bullet.position = Vec3(0, 0, 0)
        bullet.world_parent = scene

        # CUTE TRAIL
        trail = Entity(
            parent=bullet,
            model='quad',
            scale=(0.05, 2),
            color=color.rgba(150, 220, 255, 100),
            rotation_z=90
        )

        bullet.animate_position(
            bullet.position + bullet.forward * 50,
            duration=0.8,
            curve=curve.out_expo
        )

        # Cleanup
        def cleanup():
            destroy(bullet)
            destroy(trail)

        invoke(cleanup, delay=0.3)

    elif key == 'z':
        player.save_point = player.position
        cuteness.show_message("safe place marked! ")

    elif key == 'r':
        if hasattr(player, 'save_point'):
            player.position = player.save_point
            cuteness.show_message("welcome back! ")
        else:
            cuteness.show_message("no save point yet... ")

    elif key == 'q':
        world.cleanup()
        cuteness.show_message("until next dream... ")
        invoke(application.quit, delay=2)

    elif key == 'escape':
        application.quit()


# 🌸 CREATE GAME WORLD
world = DreamWorld()
environment = DreamEnvironment()
player = DreamWalker()
cuteness = CutenessManager()

# INITIAL CHUNK GENERATION
for x in range(-2, 3):
    for z in range(-2, 3):
        world.generate_chunk(x, z)

# CUTE UI ELEMENTS
cute_text = Text(
    text="welcome to dream world...  ",
    origin=(0, 0),
    y=-0.4,
    color=color.rgba(255, 240, 245, 200),
    scale=1.2,
    font='fonts/PixelifySans.ttf'  # Optional: add cute font
)

# PERFORMANCE INFO (hidden by default)
fps_text = Text(
    text="",
    position=(-0.85, 0.45),
    color=color.white33,
    scale=0.8
)

# Generated by softness qwen model. We glad to be glad~
# 🌟 MAIN UPDATE LOOP
def update():
    environment.update()
    cuteness.update()

    # Show performance info when holding F3
    if held_keys['f3']:
        fps_text.text = f"FPS: {int(1 / time.dt) if time.dt > 0 else 0}\nVoxels: {len(world.voxels)}\nChunks: {len(world.loaded_chunks)}"
        fps_text.enabled = True
    else:
        fps_text.enabled = False

    # Generate chunks around player
    player_chunk = (
        int(player.x // 8),
        int(player.z // 8)
    )

    # Generate nearby chunks
    for dx in range(-1, 2):
        for dz in range(-1, 2):
            chunk_x = player_chunk[0] + dx
            chunk_z = player_chunk[1] + dz
            if (chunk_x, chunk_z) not in world.loaded_chunks:
                world.generate_chunk(chunk_x, chunk_z)


# 🎬 START GAME
window.title = "wthh"
window.fps_counter.enabled = False

app.run()