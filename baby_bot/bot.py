import gymnasium
import numpy as np
from baby_bot.bot_env import BotEnv


class SimpleBot:
    """
    A simple bot that can interact with gymnasium environments
    """
    def __init__(self, env):
        self.env = env
        self.action_space = env.action_space
        self.observation_space = env.observation_space
        
    def get_random_action(self):
        """Return a random action from the action space"""
        if hasattr(self.action_space, 'sample'):
            return self.action_space.sample()
        else:
            # For discrete action space
            return np.random.randint(0, self.action_space.n)
    
    def get_smart_action(self, observation):
        """
        Return a more intelligent action based on the observation
        This is a simple example - in practice, this would be a neural network
        """
        # Extract information from observation
        player_x, player_y, player_z, health_norm, ammo_norm, enemies_nearby, closest_enemy_dist = observation
        
        # Simple decision making
        action = np.zeros(6, dtype=int)  # [move_forward, move_backward, move_left, move_right, jump, shoot]
        
        # Move toward enemies if nearby
        if enemies_nearby > 0 and closest_enemy_dist < 5.0:
            # Move toward enemy
            action[0] = 1  # move_forward
            if ammo_norm > 0.1:  # Only shoot if we have ammo
                action[5] = 1  # shoot
        else:
            # Explore randomly
            if np.random.random() < 0.3:
                action[np.random.randint(0, 4)] = 1  # Random movement
        
        # Jump occasionally to avoid obstacles
        if np.random.random() < 0.05:
            action[4] = 1  # jump
        
        return action
    
    def train(self, episodes=1000):
        """Simple training loop"""
        for episode in range(episodes):
            obs, _ = self.env.reset()
            total_reward = 0
            done = False
            
            while not done:
                # Choose action (random for this simple example)
                action = self.get_smart_action(obs)
                
                # Take action
                obs, reward, terminated, truncated, info = self.env.step(action)
                done = terminated or truncated
                total_reward += reward
                
                # Print progress occasionally
                if episode % 100 == 0 and np.random.random() < 0.1:
                    print(f"Episode {episode}, Step reward: {reward:.2f}, Total: {total_reward:.2f}")
            
            if episode % 100 == 0:
                print(f"Episode {episode}, Total Reward: {total_reward:.2f}")
    
    def test(self, episodes=10):
        """Test the bot"""
        for episode in range(episodes):
            obs, _ = self.env.reset()
            total_reward = 0
            done = False
            step_count = 0
            
            while not done and step_count < 500:  # Limit steps for testing
                action = self.get_smart_action(obs)
                obs, reward, terminated, truncated, info = self.env.step(action)
                done = terminated or truncated
                total_reward += reward
                step_count += 1
                
                if step_count % 50 == 0:
                    print(f"Episode {episode}, Step {step_count}, Reward: {reward:.2f}")
            
            print(f"Episode {episode} finished with total reward: {total_reward:.2f}")


# Example usage
if __name__ == "__main__":
    # Import the new baby bot
    from baby_bot import BabyFPSBot
    
    # Create environment
    env = BotEnv()
    
    # Create bot
    bot = BabyFPSBot(env)
    
    # Train the bot
    print("Training bot...")
    bot.train(episodes=500)
    
    # Test the bot
    print("\nTesting bot...")
    bot.test(episodes=5)
    
    print("Bot training and testing completed!")
