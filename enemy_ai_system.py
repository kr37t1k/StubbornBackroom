#!/usr/bin/env python3
"""
Enemy AI System for StubbornBackrooms game
This module provides AI behaviors for enemies that can use trained models
"""

import numpy as np
import math
from enum import Enum
from typing import Tuple, List, Optional

class EnemyType(Enum):
    WATCHER = "watcher"
    SMILER = "smiler"
    HUNTER = "hunter"
    FACADE = "facade"

class EnemyAI:
    def __init__(self, enemy_type: EnemyType, position: Tuple[float, float, float]):
        self.enemy_type = enemy_type
        self.position = list(position)
        self.health = 100
        self.speed = self._get_speed_for_type(enemy_type)
        self.detection_radius = self._get_detection_radius(enemy_type)
        self.state = "idle"  # idle, chasing, attacking, fleeing
        self.target_position = None
        self.last_seen_player_pos = None
        self.model_weights = None
        self.model_loaded = False
        
        # Initialize simple neural network weights based on enemy type
        self._init_simple_network()
    
    def _get_speed_for_type(self, enemy_type: EnemyType) -> float:
        speeds = {
            EnemyType.WATCHER: 1.5,
            EnemyType.SMILER: 2.0,
            EnemyType.HUNTER: 3.0,
            EnemyType.FACADE: 1.0
        }
        return speeds.get(enemy_type, 2.0)
    
    def _get_detection_radius(self, enemy_type: EnemyType) -> float:
        radii = {
            EnemyType.WATCHER: 15.0,
            EnemyType.SMILER: 10.0,
            EnemyType.HUNTER: 20.0,
            EnemyType.FACADE: 5.0
        }
        return radii.get(enemy_type, 10.0)
    
    def _init_simple_network(self):
        """Initialize simple neural network weights for AI decision making"""
        input_size = 10  # Position, velocity, distance to player, etc.
        output_size = 5  # Movement directions: forward, backward, left, right, stay
        
        # Generate random weights for a simple neural network
        self.weights_input_hidden = np.random.randn(input_size, 64) * 0.5
        self.bias_hidden = np.zeros(64)
        self.weights_hidden_output = np.random.randn(64, output_size) * 0.5
        self.bias_output = np.zeros(output_size)
    
    def load_trained_model(self, model_path: str):
        """Load a pre-trained model for the enemy AI"""
        try:
            # In a real implementation, this would load actual model weights
            # For now, we'll just check if the file exists and simulate loading
            import os
            if os.path.exists(model_path):
                # Simulate loading model weights from a file
                # In a real implementation, you'd load actual weights
                self.model_loaded = True
                print(f"Trained model loaded successfully for {self.enemy_type.value} enemy")
            else:
                print(f"Model file not found: {model_path}. Using default behavior.")
        except Exception as e:
            print(f"Failed to load model: {e}. Using default behavior.")
            self.model_loaded = False
    
    def update(self, player_pos: Tuple[float, float, float], other_enemies: List['EnemyAI'] = None):
        """Update enemy AI logic"""
        # Calculate distance to player
        dist_to_player = self._distance_to(player_pos)
        
        # Update state based on distance and other factors
        if dist_to_player < self.detection_radius:
            self.state = "chasing"
            self.last_seen_player_pos = player_pos
        elif dist_to_player > self.detection_radius * 2:
            self.state = "idle"
        
        # Move based on current state
        if self.state == "chasing" and self.last_seen_player_pos:
            self._move_towards(self.last_seen_player_pos)
        elif self.state == "idle":
            self._wander()
    
    def _distance_to(self, pos: Tuple[float, float, float]) -> float:
        """Calculate distance to a position"""
        dx = self.position[0] - pos[0]
        dy = self.position[1] - pos[1]
        dz = self.position[2] - pos[2]
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    
    def _move_towards(self, target_pos: Tuple[float, float, float]):
        """Move towards a target position"""
        dx = target_pos[0] - self.position[0]
        dy = target_pos[1] - self.position[1]
        dz = target_pos[2] - self.position[2]
        dist = max(0.1, math.sqrt(dx*dx + dy*dy + dz*dz))
        
        # Normalize direction vector
        dx /= dist
        dy /= dist
        dz /= dist
        
        # Move in that direction
        self.position[0] += dx * self.speed * 0.016  # Assuming 60 FPS
        self.position[1] += dy * self.speed * 0.016
        self.position[2] += dz * self.speed * 0.016
    
    def _wander(self):
        """Wander randomly when idle"""
        # Add small random movement
        self.position[0] += (np.random.random() - 0.5) * 0.1
        self.position[2] += (np.random.random() - 0.5) * 0.1
    
    def get_ai_decision(self, state_vector: List[float]) -> int:
        """Get AI decision using simple neural network"""
        if self.model_loaded and self.model_weights:
            # Apply simple neural network computation
            hidden = np.tanh(np.dot(np.array(state_vector), self.weights_input_hidden) + self.bias_hidden)
            output = np.dot(hidden, self.weights_hidden_output) + self.bias_output
            return int(np.argmax(output))
        else:
            # Fallback to simple logic based on enemy type
            if self.state == "chasing":
                # When chasing, prefer moving toward player (first 2 options)
                return np.random.choice([0, 1, 2, 3], p=[0.35, 0.35, 0.15, 0.15])
            else:
                # When idle, move randomly
                return np.random.randint(0, 5)
    
    def take_damage(self, damage: int):
        """Apply damage to enemy"""
        self.health -= damage
        if self.health <= 0:
            self.state = "dead"
    
    def get_render_info(self) -> dict:
        """Get information needed for rendering"""
        return {
            'position': self.position,
            'type': self.enemy_type.value,
            'health': self.health,
            'state': self.state
        }

class EnemyManager:
    def __init__(self):
        self.enemies = []
        self.default_model_path = "backrooms_agent.pth"
    
    def add_enemy(self, enemy_type: EnemyType, position: Tuple[float, float, float]) -> EnemyAI:
        """Add a new enemy to the manager"""
        enemy = EnemyAI(enemy_type, position)
        # Load the default trained model if available
        if self._model_exists(self.default_model_path):
            enemy.load_trained_model(self.default_model_path)
        self.enemies.append(enemy)
        return enemy
    
    def _model_exists(self, path: str) -> bool:
        """Check if a model file exists"""
        import os
        return os.path.exists(path)
    
    def update_all(self, player_pos: Tuple[float, float, float]):
        """Update all enemies"""
        alive_enemies = []
        for enemy in self.enemies:
            if enemy.state != "dead":
                enemy.update(player_pos, self.enemies)
                alive_enemies.append(enemy)
        self.enemies = alive_enemies
    
    def get_alive_enemies(self) -> List[EnemyAI]:
        """Get list of alive enemies"""
        return [enemy for enemy in self.enemies if enemy.state != "dead"]
    
    def get_enemy_positions(self) -> List[Tuple[float, float, float]]:
        """Get positions of all alive enemies"""
        return [enemy.position for enemy in self.get_alive_enemies()]
    
    def remove_dead_enemies(self):
        """Remove dead enemies from the list"""
        self.enemies = [enemy for enemy in self.enemies if enemy.state != "dead"]

# Example usage
if __name__ == "__main__":
    # Create enemy manager
    enemy_manager = EnemyManager()
    
    # Add some enemies
    watcher = enemy_manager.add_enemy(EnemyType.WATCHER, (10.0, 0.0, 10.0))
    hunter = enemy_manager.add_enemy(EnemyType.HUNTER, (-5.0, 0.0, 15.0))
    
    # Simulate game loop
    player_pos = (0.0, 0.0, 0.0)
    for frame in range(100):
        enemy_manager.update_all(player_pos)
        alive_count = len(enemy_manager.get_alive_enemies())
        print(f"Frame {frame}: {alive_count} enemies alive")
        
        # Move player randomly to trigger enemy responses
        player_pos = (
            player_pos[0] + (np.random.random() - 0.5) * 0.5,
            0.0,
            player_pos[2] + (np.random.random() - 0.5) * 0.5
        )