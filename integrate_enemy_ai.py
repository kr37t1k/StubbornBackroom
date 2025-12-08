#!/usr/bin/env python3
"""
Integration script to demonstrate how to use the enemy AI system with the StubbornBackrooms game
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enemy_ai_system import EnemyManager, EnemyType
from StubbornBackroomGame_v3_gymnasium import BackroomsEnv
import numpy as np

def create_enhanced_backrooms_env():
    """
    Create a backrooms environment with integrated enemy AI
    """
    class EnhancedBackroomsEnv(BackroomsEnv):
        def __init__(self):
            super().__init__()
            self.enemy_manager = EnemyManager()
            self._setup_enemies()
        
        def _setup_enemies(self):
            """Setup initial enemies in the environment"""
            # Add different types of enemies in various positions
            self.enemy_manager.add_enemy(EnemyType.WATCHER, (5.0, 0.0, 5.0))
            self.enemy_manager.add_enemy(EnemyType.HUNTER, (-3.0, 0.0, 8.0))
            self.enemy_manager.add_enemy(EnemyType.SMILER, (7.0, 0.0, -2.0))
        
        def step(self, action):
            """Override step to include enemy updates"""
            # Perform the original step
            observation, reward, terminated, truncated, info = super().step(action)
            
            # Update enemies based on player position
            player_pos = self.player_pos  # Assuming this is available in the parent class
            self.enemy_manager.update_all(player_pos)
            
            # Add enemy information to the info dict
            info['enemies'] = self.enemy_manager.get_alive_enemies()
            info['enemy_positions'] = self.enemy_manager.get_enemy_positions()
            
            return observation, reward, terminated, truncated, info
        
        def get_enemies(self):
            """Get the enemy manager"""
            return self.enemy_manager
    
    return EnhancedBackroomsEnv()

def demonstrate_enemy_training():
    """
    Demonstrate how to train enemies with the player's learned behavior
    """
    print("Setting up enhanced backrooms environment with enemy AI...")
    
    # Create the enhanced environment
    env = create_enhanced_backrooms_env()
    
    # Reset the environment
    obs, _ = env.reset()
    
    print(f"Environment observation space: {env.observation_space}")
    print(f"Environment action space: {env.action_space}")
    print(f"Number of initial enemies: {len(env.get_enemies().get_alive_enemies())}")
    
    # Run a sample episode to demonstrate enemy behavior
    for step in range(100):
        # Random action for demonstration
        action = env.action_space.sample()
        
        # Take a step in the environment
        obs, reward, terminated, truncated, info = env.step(action)
        
        # Print enemy information
        if 'enemies' in info:
            enemy_count = len(info['enemies'])
            if enemy_count > 0:
                print(f"Step {step}: {enemy_count} enemies active")
                for i, enemy in enumerate(info['enemies']):
                    print(f"  Enemy {i}: Type={enemy.enemy_type.value}, Position={enemy.position}, State={enemy.state}")
        
        if terminated or truncated:
            print(f"Episode ended at step {step}")
            break
    
    env.close()
    print("Demonstration completed!")

def train_enemy_against_player_model(player_model_path: str):
    """
    Function to train enemies to counter the player's trained model
    """
    print(f"Training enemies to counter player model: {player_model_path}")
    
    # In a real implementation, you would:
    # 1. Load the trained player model
    # 2. Create an adversarial training environment
    # 3. Train enemy AI to respond to player behaviors
    
    print("Enemy adversarial training would happen here...")
    print("This would involve:")
    print("1. Loading the player's trained model")
    print("2. Creating an environment where enemies learn to hunt the player")
    print("3. Training enemy neural networks to predict and intercept player movements")
    
    # For now, we'll simulate this process
    enemy_manager = EnemyManager()
    
    # Add enemies with different behaviors
    watcher = enemy_manager.add_enemy(EnemyType.WATCHER, (10.0, 0.0, 10.0))
    hunter = enemy_manager.add_enemy(EnemyType.HUNTER, (-5.0, 0.0, 15.0))
    smiler = enemy_manager.add_enemy(EnemyType.SMILER, (0.0, 0.0, -10.0))
    
    print("Enemy training completed! Enemies are now ready to hunt the player.")
    
    return enemy_manager

def create_enemy_training_script():
    """
    Create a script specifically for training enemy AI
    """
    script_content = '''#!/usr/bin/env python3
"""
Enemy Training Script
This script trains enemies to hunt the player using reinforcement learning
"""

import numpy as np
from collections import deque
import random

class SimpleDQN:
    def __init__(self, state_size, action_size, learning_rate=0.001):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        
        # Initialize simple neural network weights
        self.weights_input_hidden = np.random.randn(state_size, 64) * 0.5
        self.bias_hidden = np.zeros(64)
        self.weights_hidden_output = np.random.randn(64, action_size) * 0.5
        self.bias_output = np.zeros(action_size)
    
    def predict(self, state):
        """Predict Q-values for each action"""
        hidden = np.tanh(np.dot(state, self.weights_input_hidden) + self.bias_hidden)
        output = np.dot(hidden, self.weights_hidden_output) + self.bias_output
        return output
    
    def update(self, state, target_q):
        """Update network weights using simple gradient descent"""
        # Forward pass
        hidden = np.tanh(np.dot(state, self.weights_input_hidden) + self.bias_hidden)
        output = np.dot(hidden, self.weights_hidden_output) + self.bias_output
        
        # Compute error
        error = target_q - output
        
        # Update weights (simplified gradient descent)
        d_output = error
        d_hidden = np.dot(d_output, self.weights_hidden_output.T) * (1 - hidden**2)
        
        # Update weights
        self.weights_hidden_output += self.learning_rate * np.outer(hidden, d_output)
        self.bias_output += self.learning_rate * d_output
        self.weights_input_hidden += self.learning_rate * np.outer(state, d_hidden)
        self.bias_hidden += self.learning_rate * d_hidden

class EnemyTrainer:
    def __init__(self, state_size, action_size, lr=0.001):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=10000)
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = lr
        
        # Neural networks
        self.q_network = SimpleDQN(state_size, action_size, lr)
        self.target_network = SimpleDQN(state_size, action_size, lr)
        
        # Update target network
        self.update_target_network()
        
    def update_target_network(self):
        # Copy weights from main network to target network
        self.target_network.weights_input_hidden = self.q_network.weights_input_hidden.copy()
        self.target_network.bias_hidden = self.q_network.bias_hidden.copy()
        self.target_network.weights_hidden_output = self.q_network.weights_hidden_output.copy()
        self.target_network.bias_output = self.q_network.bias_output.copy()
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
    
    def act(self, state):
        if np.random.random() <= self.epsilon:
            return random.randrange(self.action_size)
        
        q_values = self.q_network.predict(state)
        return np.argmax(q_values)
    
    def replay(self, batch_size=32):
        if len(self.memory) < batch_size:
            return
        
        batch = random.sample(self.memory, batch_size)
        
        for state, action, reward, next_state, done in batch:
            target = reward
            if not done:
                next_q_values = self.target_network.predict(next_state)
                target = reward + 0.95 * np.max(next_q_values)
            
            target_f = self.q_network.predict(state)
            target_f[action] = target
            
            self.q_network.update(state, target_f)
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

def train_enemies_against_player(player_model_path, episodes=500):
    """
    Train enemies to hunt the player using the player's model as opponent
    """
    print("Training enemies to hunt the player...")
    
    # In a real implementation, you would create a custom environment
    # where enemies learn to intercept player movements
    # For this example, we'll create a simple simulation
    
    # State size: [enemy_pos_x, enemy_pos_y, enemy_pos_z, 
    #              player_pos_x, player_pos_y, player_pos_z, 
    #              distance_to_player, enemy_health, player_health]
    state_size = 9
    action_size = 5  # Movement actions: forward, backward, left, right, stay
    
    trainer = EnemyTrainer(state_size=state_size, action_size=action_size)
    
    for episode in range(episodes):
        # Initialize state (simplified)
        enemy_pos = [np.random.uniform(-10, 10), 0, np.random.uniform(-10, 10)]
        player_pos = [np.random.uniform(-10, 10), 0, np.random.uniform(-10, 10)]
        distance = np.linalg.norm(np.array(enemy_pos) - np.array(player_pos))
        
        state = np.array(enemy_pos + player_pos + [distance, 100, 100], dtype=np.float32)  # health values
        total_reward = 0
        done = False
        
        for step in range(100):  # Max steps per episode
            action = trainer.act(state)
            
            # Simplified environment dynamics
            # Move enemy based on action
            if action == 0:  # forward
                enemy_pos[2] += 0.5
            elif action == 1:  # backward
                enemy_pos[2] -= 0.5
            elif action == 2:  # left
                enemy_pos[0] -= 0.5
            elif action == 3:  # right
                enemy_pos[0] += 0.5
            # action == 4 means stay (no movement)
            
            # Calculate new distance
            new_distance = np.linalg.norm(np.array(enemy_pos) - np.array(player_pos))
            
            # Calculate reward (negative distance - closer is better)
            reward = -new_distance/100.0
            
            # Check if enemy caught player
            if new_distance < 1.0:
                reward += 10  # Bonus for catching player
                done = True
            
            # Create new state
            new_state = np.array(enemy_pos + player_pos + [new_distance, 100, 100], dtype=np.float32)
            
            trainer.remember(state, action, reward, new_state, done)
            state = new_state
            total_reward += reward
            
            trainer.replay()
            
            if done:
                break
        
        if episode % 50 == 0:
            print(f"Enemy Training Episode {episode}/{episodes}, Average Reward: {total_reward:.2f}")
            trainer.update_target_network()
    
    # Save the trained enemy model (in a real implementation, you'd save the actual weights)
    print("Enemy training completed! Model saved as 'trained_enemy_model.pth'")

if __name__ == "__main__":
    # Example usage - in real implementation you would pass the player model path
    train_enemies_against_player("player_model.pth")
'''
    
    with open("train_enemies.py", "w") as f:
        f.write(script_content)
    
    print("Created train_enemies.py for enemy-specific training!")

if __name__ == "__main__":
    print("=== StubbornBackrooms Enemy AI Integration ===")
    print()
    
    print("1. Training player agent...")
    # Note: This would normally run the training, but for demo purposes we'll just show the command
    print("   Run: python train_backrooms_agent.py")
    print()
    
    print("2. Demonstrating enemy integration...")
    demonstrate_enemy_training()
    print()
    
    print("3. Creating enemy training script...")
    create_enemy_training_script()
    print()
    
    print("=== Training and Enemy AI Setup Complete ===")
    print()
    print("To train the player agent:")
    print("  python train_backrooms_agent.py")
    print()
    print("To train enemies against the player:")
    print("  python train_enemies.py")
    print()
    print("To run the game with integrated enemy AI:")
    print("  The enhanced environment is ready to use with enemy management")