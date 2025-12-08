import gymnasium
import numpy as np
from baby_bot.bot_env import BotEnv


class BabyFPSBot:
    """
    A simple FPS bot that can interact with gymnasium environments
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
            # For multi-discrete action space
            action = np.zeros(self.action_space.nvec.shape[0], dtype=int)
            for i in range(len(self.action_space.nvec)):
                action[i] = np.random.randint(0, self.action_space.nvec[i])
            return action
    
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


class BabyBackroomsBot:
    """
    A simple backrooms bot that can interact with gymnasium environments
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
        """
        # Extract information from observation
        player_x, player_y, player_z, distortion_level, reality_stability, reality_state = observation
        
        # Simple decision making based on reality state
        if reality_state == 3:  # CHAOTIC
            # Move randomly to try to escape chaotic state
            return np.random.randint(0, 5)
        elif reality_state == 2:  # LIMINAL
            # Move forward to explore
            return 0  # forward
        elif reality_state in [0, 1]:  # STABLE or DISTORTED
            # Move forward or right randomly
            return np.random.choice([0, 3])  # forward or right
        
        # Default action
        return np.random.randint(0, 5)
    
    def train(self, episodes=1000):
        """Simple training loop"""
        for episode in range(episodes):
            obs, _ = self.env.reset()
            total_reward = 0
            done = False
            
            while not done:
                # Choose action
                action = self.get_smart_action(obs)
                
                # Take action
                obs, reward, terminated, truncated, info = self.env.step(action)
                done = terminated or truncated
                total_reward += reward
                
                # Print progress occasionally
                if episode % 100 == 0 and np.random.random() < 0.1:
                    print(f"Backrooms Episode {episode}, Step reward: {reward:.2f}, Total: {total_reward:.2f}")
            
            if episode % 100 == 0:
                print(f"Backrooms Episode {episode}, Total Reward: {total_reward:.2f}")
    
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
                    print(f"Backrooms Episode {episode}, Step {step_count}, Reward: {reward:.2f}")
            
            print(f"Backrooms Episode {episode} finished with total reward: {total_reward:.2f}")


# Example usage
if __name__ == "__main__":
    # Create FPS environment
    fps_env = BotEnv()
    
    # Create FPS bot
    fps_bot = BabyFPSBot(fps_env)
    
    # Train the FPS bot
    print("Training FPS bot...")
    fps_bot.train(episodes=500)
    
    # Test the FPS bot
    print("\nTesting FPS bot...")
    fps_bot.test(episodes=5)
    
    # Create backrooms environment
    try:
        from StubbornBackroomGame_v4_masterpiece import BackroomsGymEnv
        backrooms_env = BackroomsGymEnv()
        
        # Create backrooms bot
        backrooms_bot = BabyBackroomsBot(backrooms_env)
        
        # Train the backrooms bot
        print("\nTraining Backrooms bot...")
        backrooms_bot.train(episodes=500)
        
        # Test the backrooms bot
        print("\nTesting Backrooms bot...")
        backrooms_bot.test(episodes=5)
        
    except ImportError:
        print("Backrooms gym environment not available")
    
    print("\nBaby bot training and testing completed!")