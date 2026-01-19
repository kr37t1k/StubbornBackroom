"""
FPS Controller Component
Handles first-person shooter movement, aiming, and weapon mechanics
"""

from .engine import Component, Transform
import math
from ursina import Vec3, mouse, held_keys


class FPSController(Component):
    """First Person Shooter Controller component"""
    def __init__(self, sensitivity=30, speed=5, jump_height=8, gravity=1.0):
        super().__init__()
        self.sensitivity = sensitivity
        self.speed = speed
        self.jump_height = jump_height
        self.gravity = gravity
        
        # Movement state
        self.velocity = Vec3(0, 0, 0)
        self.is_grounded = False
        self.jump_cooldown = 0
        self.movement = Vec3(0, 0, 0)
        
        # Weapon state
        self.ammo = 30
        self.max_ammo = 30
        self.health = 100
        self.max_health = 100
        self.weapon_cooldown = 0
        
        # Camera controls
        self.pitch = 0  # Looking up/down
        self.yaw = 0    # Looking left/right
        self.roll = 0   # Tilting head
    
    def update(self, dt):
        # Handle mouse input for camera rotation
        self.handle_mouse_rotation()
        
        # Handle keyboard input for movement
        self.handle_movement(dt)
        
        # Handle weapon input
        self.handle_weapon(dt)
        
        # Apply gravity
        self.apply_gravity(dt)
        
        # Update cooldowns
        self.update_cooldowns(dt)
    
    def handle_mouse_rotation(self):
        """Handle mouse input for camera rotation"""
        if mouse.locked:
            self.yaw += mouse.velocity[0] * self.sensitivity
            self.pitch -= mouse.velocity[1] * self.sensitivity
            self.pitch = max(-90, min(90, self.pitch))  # Clamp pitch to prevent flipping
        
        # Update transform rotation
        if self.owner and hasattr(self.owner, 'transform'):
            self.owner.transform.rotation = Vec3(self.pitch, self.yaw, self.roll)
    
    def handle_movement(self, dt):
        """Handle keyboard input for movement"""
        # Reset movement vector
        self.movement = Vec3(0, 0, 0)
        
        # Forward/backward movement
        if held_keys['w'] or held_keys['up arrow']:
            self.movement += self.get_forward_vector()
        if held_keys['s'] or held_keys['down arrow']:
            self.movement -= self.get_forward_vector()
        
        # Strafe movement
        if held_keys['a'] or held_keys['left arrow']:
            self.movement -= self.get_right_vector()
        if held_keys['d'] or held_keys['right arrow']:
            self.movement += self.get_right_vector()
        
        # Normalize movement vector to prevent faster diagonal movement
        if self.movement.length() > 0:
            self.movement = self.movement.normalized()
        
        # Apply movement to position
        if self.owner and hasattr(self.owner, 'transform'):
            self.owner.transform.position += self.movement * self.speed * dt
    
    def handle_weapon(self, dt):
        """Handle weapon input and firing"""
        # Shooting
        if held_keys['left mouse down'] and self.weapon_cooldown <= 0 and self.ammo > 0:
            self.shoot()
            self.weapon_cooldown = 0.1  # Cooldown between shots
            self.ammo -= 1
    
    def apply_gravity(self, dt):
        """Apply gravity to the player"""
        if self.owner and hasattr(self.owner, 'transform'):
            # Apply gravity if not grounded
            if not self.is_grounded:
                self.velocity.y -= self.gravity * dt
                self.owner.transform.position.y += self.velocity.y * dt
    
    def update_cooldowns(self, dt):
        """Update various cooldown timers"""
        if self.jump_cooldown > 0:
            self.jump_cooldown -= dt
        
        if self.weapon_cooldown > 0:
            self.weapon_cooldown -= dt
    
    def get_forward_vector(self):
        """Get forward direction based on current rotation"""
        if self.owner and hasattr(self.owner, 'transform'):
            return self.owner.transform.get_forward_vector()
        else:
            # Default forward is -Z
            return Vec3(0, 0, -1)
    
    def get_right_vector(self):
        """Get right direction based on current rotation"""
        # Right vector is perpendicular to forward
        forward = self.get_forward_vector()
        right = Vec3(-forward.z, 0, forward.x).normalized()
        return right
    
    def shoot(self):
        """Handle shooting mechanics"""
        # This would typically create a projectile or raycast
        print("Firing weapon!")
        
        # In a real implementation, this would:
        # 1. Create a bullet/raycast
        # 2. Check for hits
        # 3. Apply damage to targets
        # 4. Add visual effects
    
    def take_damage(self, amount):
        """Apply damage to the player"""
        self.health -= amount
        if self.health <= 0:
            self.die()
    
    def die(self):
        """Handle player death"""
        print("Player died!")
        # Respawn logic would go here
        self.health = self.max_health
        self.ammo = self.max_ammo
        # Reset position to spawn point


class Weapon(Component):
    """Weapon component for handling shooting mechanics"""
    def __init__(self, damage=25, fire_rate=0.1, range=50, ammo_type="standard"):
        super().__init__()
        self.damage = damage
        self.fire_rate = fire_rate
        self.range = range
        self.ammo_type = ammo_type
        self.cooldown = 0
        self.projectile_speed = 50
    
    def update(self, dt):
        if self.cooldown > 0:
            self.cooldown -= dt
    
    def fire(self, position, direction):
        """Fire the weapon"""
        if self.cooldown <= 0:
            # Create projectile
            projectile = Projectile(
                position=position,
                direction=direction,
                speed=self.projectile_speed,
                damage=self.damage
            )
            self.cooldown = self.fire_rate
            return projectile
        return None


class Projectile:
    """Projectile fired by weapons"""
    def __init__(self, position, direction, speed, damage):
        self.position = position
        self.direction = direction.normalized()
        self.speed = speed
        self.damage = damage
        self.lifetime = 5.0  # Destroy after 5 seconds
        self.velocity = self.direction * self.speed
    
    def update(self, dt):
        """Update projectile position"""
        self.position += self.velocity * dt
        self.lifetime -= dt
        return self.lifetime > 0  # Return True if still alive