# player.py - Player with dream-like movement
import math
import random


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

        if 'w' in keys_pressed:
            new_x = self.x + math.cos(self.angle) * self.move_speed * dt
            new_y = self.y + math.sin(self.angle) * self.move_speed * dt
            if self._can_move_to(new_x, new_y, world):
                self.x, self.y = new_x, new_y
                moved = True

        if 's' in keys_pressed:
            new_x = self.x - math.cos(self.angle) * self.move_speed * dt
            new_y = self.y - math.sin(self.angle) * self.move_speed * dt
            if self._can_move_to(new_x, new_y, world):
                self.x, self.y = new_x, new_y
                moved = True

        if 'a' in keys_pressed:
            self.angle -= self.turn_speed * dt
            moved = True

        if 'd' in keys_pressed:
            self.angle += self.turn_speed * dt
            moved = True

        self.is_walking = moved

        # Update dream effects
        self._update_dream_state(world, dt)
        self._update_float(dt)
        self._update_glitch(dt)
        self._update_footsteps(dt)

    def _can_move_to(self, x, y, world):
        """✅ FIXED: Proper collision detection"""
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