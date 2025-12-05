from ursina import *
from ursina.shaders import lit_with_shadows_shader
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import math
from collections import deque

app = Ursina()
random.seed(0)

Entity.default_shader = lit_with_shadows_shader

# 🌍 WORLD SETUP
ground = Entity(
    model='plane',
    position=(20, 25, 20),
    scale=(100,10,100),
    color=color.yellow.tint(-.2),
    texture='white_cube',
    texture_scale=(100,100),
    collider='box'
)


# 🎯 AMMO AND LOOT SYSTEM
class Ammo(Entity):
    def __init__(self, position, amount=10):
        super().__init__(
            parent=scene,
            model='cube',
            scale=0.3,
            color=color.yellow.tint(-0.5),
            position=position,
            collider='box'
        )
        self.amount = amount
        self.blinking = False

        # Floating animation
        self.animate_y(self.y + 0.5, duration=2, loop=True, curve=curve.in_out_sine)

        # Pulse effect
        self.animate_scale(0.4, duration=1, loop=True, curve=curve.in_out_sine)

    def collect(self, player):
        player.ammo += self.amount
        destroy(self)


class HealthPack(Entity):
    def __init__(self, position, amount=25):
        super().__init__(
            parent=scene,
            model='cube',
            scale=0.3,
            color=color.green.tint(-0.3),
            position=position,
            collider='box'
        )
        self.amount = amount
        self.animate_y(self.y + 0.5, duration=2, loop=True, curve=curve.in_out_sine)
        self.animate_scale(0.4, duration=1, loop=True, curve=curve.in_out_sine)


# 🎮 PLAYER CLASS (Enhanced)
class Player(FirstPersonController):
    def __init__(self):
        super().__init__(
            model='cube',
            position=(0, 0, 0),
            color=color.orange,
            origin_y=-0.5,
            speed=8,
            collider='box'
        )
        self.collider = BoxCollider(self, Vec3(0, 1, 0), Vec3(1, 2, 1))

        # 🔫 WEAPON SYSTEM
        self.gun = Entity(
            model='cube',
            parent=camera,
            position=(0.5, -0.25, 0.25),
            scale=(0.3, 0.2, 1),
            origin_z=-0.5,
            color=color.red,
            on_cooldown=False
        )
        self.gun.muzzle_flash = Entity(
            parent=self.gun,
            z=1,
            world_scale=0.5,
            model='quad',
            color=color.yellow,
            enabled=False
        )

        # 📦 INVENTORY
        self.ammo = 30
        self.max_ammo = 50
        self.health = 75
        self.max_health = 100
        self.knife_only = False

        # 🎯 UI ELEMENTS
        self.ammo_text = Text(
            text=f'Ammo: {self.ammo}',
            position=(-0.85, 0.45),
            origin=(-0.5, 0),
            scale=1.5,
            color=color.white
        )
        self.health_text = Text(
            text=f'Health: {self.health}',
            position=(-0.85, 0.4),
            origin=(-0.5, 0),
            scale=1.5,
            color=color.white
        )

        # 🏠 SPAWN POINT
        self.gravity = 1
        self.spawn_point = Vec3(0, 35, 0)
        self.position = self.spawn_point

    def shoot(self):
        if self.knife_only:
            return  # Can't shoot with knife only

        if self.ammo > 0 and not self.gun.on_cooldown:
            self.ammo -= 1
            self.ammo_text.text = f'Ammo: {self.ammo}'

            self.gun.on_cooldown = True
            self.gun.muzzle_flash.enabled = True
            invoke(self.gun.muzzle_flash.disable, delay=0.05)
            invoke(setattr, self.gun, 'on_cooldown', False, delay=0.15)

            # Hit detection
            hit_info = raycast(
                self.world_position + Vec3(0, 1.5, 0),
                self.forward,
                distance=50,
                ignore=(self,)
            )

            if hit_info.entity and hasattr(hit_info.entity, 'hp'):
                hit_info.entity.take_damage(25)
                hit_info.entity.blink(color.red)

    def update(self):
        super().update()

        # 🔫 SHOOTING
        if held_keys['left mouse']:
            self.shoot()

        # 🧠 ENEMY DETECTION (for debugging)
        try:
            for enemy in enemies:
                dist = distance_xz(self.position, enemy.position)
                if dist < 30 and enemy.can_see_player():
                    enemy.state = 'chasing'
                elif dist > 30:
                    enemy.state = 'patrolling'
        except:
            for enemy in enemies:
                dist = distance_xz(self.position, enemy.position)
                if dist < 30 and enemy.can_see_player():
                    enemy.state = 'chasing'
                elif dist > 30:
                    enemy.state = 'patrolling'

    def take_damage(self, amount):
        self.health -= amount
        self.health_text.text = f'Health: {self.health}'

        if self.health <= 0:
            self.die()

    def die(self):
        # 💀 DROP AMMO
        if self.ammo > 0:
            Ammo(position=self.position, amount=self.ammo)

        # 🏠 RESPAWN
        self.position = self.spawn_point
        self.health = self.max_health
        self.health_text.text = f'Health: {self.health}'
        self.ammo = 0  # Only knife
        self.knife_only = True
        self.ammo_text.text = 'Knife Only'

        # Spawn knife indicator
        invoke(setattr, self, 'knife_only', False, delay=5)  # Knife only for 5 seconds
        invoke(self.restore_ammo, delay=5)

    def restore_ammo(self):
        self.ammo = 10  # Start with some ammo
        self.knife_only = False
        self.ammo_text.text = f'Ammo: {self.ammo}'


# 👾 ENEMY CLASS (Advanced AI)
class Enemy(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            parent=shootables_parent,
            model='cube',
            scale=(1,2,1),
            origin_y=-0.5,
            color=color.light_gray,
            highlight_color=color.orange,
            collider='box',
            **kwargs
        )

        # 🧠 AI STATES
        self.state = 'patrolling'  # patrolling, chasing, shooting
        self.patrol_points = self.generate_patrol_points()
        self.current_patrol_point = 0
        self.patrol_timer = 0
        self.shoot_timer = 0
        self.last_shot_time = 0

        # ❤️ HEALTH SYSTEM
        self.max_hp = random.randrange(50, 150, 25)
        self.hp = self.max_hp

        # 📊 HEALTH BAR
        self.health_bar = Entity(
            parent=self,
            y=1.2,
            model='cube',
            color=color.red,
            world_scale=(1.5, 0.1, 0.1)
        )

        # 🎯 LOOT TABLE
        self.loot_table = [
            ('ammo', 0.7, lambda: Ammo(position=self.position, amount=random.randint(5, 15))),
            ('health', 0.3, lambda: HealthPack(position=self.position, amount=random.randint(10, 30)))
        ]

        # 🏠 BASE POSITION
        self.base_position = Vec3(self.x, self.y, self.z)

    def generate_patrol_points(self):
        """Generate random patrol points around base"""
        points = []
        for _ in range(4):
            angle = random.uniform(0, math.pi * 2)
            distance = random.uniform(5, 15)
            x = self.x + math.cos(angle) * distance
            z = self.z + math.sin(angle) * distance
            points.append(Vec3(x, self.y, z))
        return points

    def can_see_player(self):
        """Check if enemy has line of sight to player"""
        hit_info = raycast(
            self.world_position + Vec3(0, 1, 0),
            player.position - (self.world_position + Vec3(0, 1, 0)),
            distance=30,
            ignore=(self,)
        )
        return hit_info.entity == player

    def take_damage(self, amount):
        self.hp -= amount
        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
        self.health_bar.alpha = 1

        if self.hp <= 0:
            self.die()

    def die(self):
        # 💰 DROP LOOT
        for item_type, probability, spawn_func in self.loot_table:
            if random.random() < probability:
                spawn_func()

        # 🔄 RESPATWN
        invoke(self.respawn, delay=random.uniform(5, 10))
        destroy(self)

    def respawn(self):
        """Respawn enemy at base position"""
        new_enemy = Enemy(
            x=self.base_position.x,
            y=self.base_position.y,
            z=self.base_position.z
        )
        enemies.append(new_enemy)
        enemies.remove(self)

    def update(self):
        # 🧠 STATE MACHINE
        player_dist = distance_xz(player.position, self.position)

        # State transitions
        if player_dist < 15 and self.can_see_player():
            self.state = 'shooting'
        elif player_dist < 30 and self.can_see_player():
            self.state = 'chasing'
        else:
            self.state = 'patrolling'

        # 🎯 STATE BEHAVIOR
        if self.state == 'chasing':
            # Move toward player
            direction = player.position - self.position
            direction.y = 0  # Stay on ground
            if direction.length() > 0:
                direction = direction.normalized()
                self.position += direction * time.dt * 3

                # Look at player
                self.look_at_2d(player.position, 'y')

        elif self.state == 'shooting':
            # Look at player and shoot
            self.look_at_2d(player.position, 'y')

            # Shooting cooldown
            if time.time() - self.last_shot_time > 1.5:
                self.shoot_at_player()
                self.last_shot_time = time.time()

        elif self.state == 'patrolling':
            # Move to patrol points
            target_point = self.patrol_points[self.current_patrol_point]
            distance_to_target = (target_point - self.position).length()

            if distance_to_target < 1:
                # Reached patrol point, go to next
                self.current_patrol_point = (self.current_patrol_point + 1) % len(self.patrol_points)
                self.patrol_timer = random.uniform(1, 3)
            elif self.patrol_timer <= 0:
                # Move toward patrol point
                direction = target_point - self.position
                direction.y = 0
                if direction.length() > 0:
                    direction = direction.normalized()
                    self.position += direction * time.dt * 2

                    # Look in movement direction
                    self.look_at_2d(target_point, 'y')
            else:
                self.patrol_timer -= time.dt

        # 📊 HEALTH BAR FADE
        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)

    def shoot_at_player(self):
        """Enemy shoots at player"""
        # Create enemy bullet
        bullet = Entity(
            model='sphere',
            color=color.red,
            scale=0.1,
            position=self.world_position + Vec3(0, 1, 0),
            collider='sphere'
        )

        # Direction toward player
        direction = player.position - bullet.position
        direction = direction.normalized()

        # Move bullet
        bullet.animate_position(
            bullet.position + direction * 50,
            duration=1,
            curve=curve.linear
        )

        # Damage player on hit
        def check_hit():
            try:
                if bullet.enabled and distance(bullet.position, player.position) < 1.5:
                    player.take_damage(10)
            except:
                if bullet.enabled: player.take_damage(10)
            destroy(bullet)

        invoke(check_hit, delay=0.1)
        invoke(destroy, bullet, delay=1)


# 🌐 GAME SETUP
shootables_parent = Entity()
mouse.traverse_target = shootables_parent

player = Player()

# 🏗️ ENVIRONMENT
for i in range(64):
    brick = Entity(
        model='cube',
        origin_y=-0.5,
        scale=2,
        texture='brick',
        texture_scale=(1, 2),
        position=(random.randint(-16, 32),25,random.randint(-16, 32) + 8),
        collider='box',
        scale_y=random.uniform(2, 3),
        color=color.hsv(0, 0, random.uniform(0.9, 1))
    )
    # if brick collides with other brick its need to distance < 2, like distance(this_brick,other_brick) < 2, destroy it
    #     destroy(brick) - we need bricks placed like on grid,every one on his grid pos

# 👾 ENEMY SPAWN
enemies = []
for i in range(32):  # Start with 5 enemies
    enemy = Enemy(
        position=(random.uniform(-16, 16),25,random.uniform(-16, 16))
    )
    enemies.append(enemy)


# 🎵 INPUT HANDLING
def input(key):
    if key == 'z':
        player.position = player.spawn_point
    if key == 'f':
        player.y += 10
    if key == 'escape':
        application.quit()
    if key == 'tab':
        # Toggle editor camera - its doent work + its not needed for now
        editor_camera.enabled = not editor_camera.enabled
        player.visible_self = editor_camera.enabled
        player.cursor.enabled = not editor_camera.enabled
        player.gun.enabled = not editor_camera.enabled
        mouse.locked = not editor_camera.enabled
        editor_camera.position = player.position
        application.paused = editor_camera.enabled


editor_camera = EditorCamera(enabled=False, ignore_paused=True)
pause_handler = Entity(ignore_paused=True, input=input)

# 🌞 LIGHTING
sun = DirectionalLight()
sun.look_at(Vec3(1, -1, -1))
Sky()


# 🎯 AUTO-COLLECT SYSTEM
def update():
    # Auto-collect items when close
    for entity in scene.entities[:]:
        if isinstance(entity, (Ammo, HealthPack)):
            if distance(player.position, entity.position) < 1.5:
                if isinstance(entity, Ammo):
                    player.ammo += entity.amount
                    player.ammo_text.text = f'Ammo: {player.ammo}'
                    destroy(entity)
                elif isinstance(entity, HealthPack):
                    player.health = min(player.max_health, player.health + entity.amount)
                    player.health_text.text = f'Health: {player.health}'
                    destroy(entity)


# 📋 INSTRUCTIONS
instructions = Text(
    text="WASD: Move | MOUSE: Aim | LMB: Shoot\nRMB: Not used | TAB: Editor mode",
    position=(0, -0.45),
    origin=(0, 0),
    scale=1.2,
    color=color.white33
)

app.run()