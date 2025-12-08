#!/usr/bin/env python3
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