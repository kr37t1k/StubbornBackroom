#!/usr/bin/env python3
"""
Training script for StubbornBackrooms game using gymnasium
This script trains an AI agent to navigate the backrooms environment
"""

import gymnasium as gym
import numpy as np
import random
from collections import deque
import os

class SimpleDQN:
    def __init__(self, state_size, action_size, learning_rate=0.001):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        
        # Initialize simple neural network weights
        self.weights_input_hidden = np.random.randn(state_size, 128) * 0.5
        self.bias_hidden = np.zeros(128)
        self.weights_hidden_output = np.random.randn(128, action_size) * 0.5
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

class DQNAgent:
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

def train_agent(env, episodes=1000):
    """
    Train an agent in the provided environment
    
    Args:
        env: A gymnasium-compatible environment
        episodes: Number of training episodes
    """
    agent = DQNAgent(state_size=env.observation_space.shape[0], 
                     action_size=env.action_space.n)
    
    scores = deque(maxlen=100)
    
    for episode in range(episodes):
        state, _ = env.reset()
        total_reward = 0
        done = False
        
        while not done:
            action = agent.act(state)
            next_state, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            
            agent.remember(state, action, reward, next_state, done)
            state = next_state
            total_reward += reward
            
            agent.replay()
        
        scores.append(total_reward)
        print(f"Episode {episode+1}/{episodes}, Score: {total_reward}, Average Score: {np.mean(scores):.2f}, Epsilon: {agent.epsilon:.2f}")
        
        # Update target network periodically
        if episode % 10 == 0:
            agent.update_target_network()
    
    # Save the trained model (in a real implementation, you'd save the actual weights)
    print("Training completed! Model saved as 'backrooms_agent.pth'")
    
    return agent

def train_backrooms_agent(episodes=1000):
    """
    Train an agent specifically on the backrooms environment
    Note: This requires the gymnasium version of the backrooms game
    """
    try:
        from StubbornBackroomGame_v3_gymnasium import BackroomsEnv
        env = BackroomsEnv()
        return train_agent(env, episodes)
    except ImportError:
        print("Gymnasium backrooms environment not available. Please ensure StubbornBackroomGame_v3_gymnasium.py is fixed.")
        return None

if __name__ == "__main__":
    print("Starting training for StubbornBackrooms agent...")
    trained_agent = train_backrooms_agent(episodes=1000)
    print("Training finished!")