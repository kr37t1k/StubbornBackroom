import gymnasium
from gymnasium import spaces
import numpy as np


class BotEnv(gymnasium.Env):
    """
    FPS Game Bot Environment
    This environment is designed to work with FPS games like sample_fps_game.py
    """
    def __init__(self, **kwargs):
        super().__init__()
        
        # Define action space: [move_forward, move_backward, move_left, move_right, jump, shoot]
        self.action_space = spaces.MultiDiscrete([2, 2, 2, 2, 2, 2])  # Each action can be 0 or 1
        
        # Observation space: [player_x, player_y, player_z, health, ammo, enemies_nearby, distance_to_closest_enemy]
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(7,), dtype=np.float32
        )
        
        # Game state
        self.player_pos = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        self.health = 100.0
        self.ammo = 30.0
        self.enemies_nearby = 0
        self.closest_enemy_distance = 10.0
        self.max_steps = 1000
        self.current_step = 0

    def step(self, action):
        # Decode action
        move_forward, move_backward, move_left, move_right, jump, shoot = action
        
        # Update player position based on actions
        move_speed = 0.1
        if move_forward:
            self.player_pos[2] += move_speed
        if move_backward:
            self.player_pos[2] -= move_speed
        if move_left:
            self.player_pos[0] -= move_speed
        if move_right:
            self.player_pos[0] += move_speed
        if jump:
            self.player_pos[1] += 0.05  # Small jump
        
        # Simulate shooting
        if shoot and self.ammo > 0:
            self.ammo -= 1
            # If there's an enemy nearby, we might hit it
            if self.enemies_nearby > 0 and np.random.random() < 0.3:  # 30% hit chance
                self.enemies_nearby = max(0, self.enemies_nearby - 1)
        
        # Update environment state
        self._update_environment()
        
        # Calculate reward
        reward = self._calculate_reward()
        
        # Check termination
        terminated = self.health <= 0 or self.current_step >= self.max_steps
        truncated = self.current_step >= self.max_steps
        
        # Get observation
        observation = np.array([
            self.player_pos[0],
            self.player_pos[1], 
            self.player_pos[2],
            self.health / 100.0,  # Normalize
            self.ammo / 50.0,     # Normalize
            float(self.enemies_nearby),
            self.closest_enemy_distance
        ], dtype=np.float32)
        
        self.current_step += 1
        
        return observation, reward, terminated, truncated, {}

    def _update_environment(self):
        # Simulate enemies moving around
        if np.random.random() < 0.1:  # 10% chance of enemy spawning
            self.enemies_nearby = min(5, self.enemies_nearby + 1)
        
        # Update closest enemy distance (simplified)
        if self.enemies_nearby > 0:
            self.closest_enemy_distance = np.random.uniform(1.0, 10.0)
        else:
            self.closest_enemy_distance = 10.0
        
        # Random damage to player
        if np.random.random() < 0.05 and self.enemies_nearby > 0:  # 5% chance of taking damage
            self.health -= np.random.uniform(1.0, 5.0)
        
        # Random health/ammo pickup
        if np.random.random() < 0.02:  # 2% chance of health pickup
            self.health = min(100.0, self.health + 10.0)
        if np.random.random() < 0.03:  # 3% chance of ammo pickup
            self.ammo = min(50.0, self.ammo + 5.0)

    def _calculate_reward(self):
        reward = 0.0
        
        # Positive reward for staying alive
        reward += 0.1
        
        # Reward for eliminating enemies
        if self.enemies_nearby < getattr(self, '_prev_enemies', 1):
            reward += 10.0
        
        # Penalty for taking damage
        if hasattr(self, '_prev_health'):
            if self.health < self._prev_health:
                reward -= (self._prev_health - self.health) * 0.1
        
        # Reward for collecting ammo
        if hasattr(self, '_prev_ammo'):
            if self.ammo > self._prev_ammo:
                reward += (self.ammo - self._prev_ammo) * 0.2
        
        # Penalty for running out of ammo
        if self.ammo <= 0:
            reward -= 0.1
        
        # Update previous values for next calculation
        self._prev_health = self.health
        self._prev_ammo = self.ammo
        self._prev_enemies = self.enemies_nearby
        
        return reward

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        # Reset game state
        self.player_pos = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        self.health = 100.0
        self.ammo = 30.0
        self.enemies_nearby = 0
        self.closest_enemy_distance = 10.0
        self.current_step = 0
        
        # Initialize previous values
        self._prev_health = self.health
        self._prev_ammo = self.ammo
        self._prev_enemies = self.enemies_nearby
        
        observation = np.array([
            self.player_pos[0],
            self.player_pos[1], 
            self.player_pos[2],
            self.health / 100.0,  # Normalize
            self.ammo / 50.0,     # Normalize
            float(self.enemies_nearby),
            self.closest_enemy_distance
        ], dtype=np.float32)
        
        return observation, {}

    def render(self, mode='human'):
        # Simple text-based rendering
        print(f"Player: ({self.player_pos[0]:.2f}, {self.player_pos[1]:.2f}, {self.player_pos[2]:.2f}) "
              f"Health: {self.health:.1f}, Ammo: {self.ammo:.1f}, Enemies: {self.enemies_nearby}")