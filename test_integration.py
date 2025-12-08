#!/usr/bin/env python3
"""
Test script to verify that all components work together
"""

def test_imports():
    """Test that all modules can be imported without errors"""
    print("Testing imports...")
    
    # Test main game imports
    try:
        from StubbornBackroomGame_v4_masterpiece import BackroomsGymEnv
        print("✓ Masterpiece backrooms game imported successfully")
    except Exception as e:
        print(f"✗ Error importing masterpiece backrooms: {e}")
    
    # Test gymnasium environments
    try:
        import gymnasium
        print("✓ Gymnasium imported successfully")
    except Exception as e:
        print(f"✗ Error importing gymnasium: {e}")
    
    # Test baby bot imports
    try:
        from baby_bot.baby_bot import BabyFPSBot, BabyBackroomsBot
        print("✓ Baby bots imported successfully")
    except Exception as e:
        print(f"✗ Error importing baby bots: {e}")
    
    # Test FPS environment
    try:
        from baby_bot.bot_env import BotEnv
        print("✓ FPS bot environment imported successfully")
    except Exception as e:
        print(f"✗ Error importing FPS bot environment: {e}")
    
    # Test the baby FPS game environment
    try:
        from baby_bot.sample_fps_game import BabyFPSGameEnv
        print("✓ Baby FPS game environment imported successfully")
    except Exception as e:
        print(f"✗ Error importing baby FPS game environment: {e}")

def test_gym_environments():
    """Test that gym environments can be created and used"""
    print("\nTesting gym environments...")
    
    # Test backrooms environment
    try:
        from StubbornBackroomGame_v4_masterpiece import BackroomsGymEnv
        backrooms_env = BackroomsGymEnv()
        obs, info = backrooms_env.reset()
        print(f"✓ Backrooms gym environment created, observation shape: {obs.shape}")
        
        # Test a single step
        action = backrooms_env.action_space.sample()
        obs, reward, terminated, truncated, info = backrooms_env.step(action)
        print(f"✓ Backrooms step completed, reward: {reward}")
    except Exception as e:
        print(f"✗ Error testing backrooms environment: {e}")
    
    # Test FPS environment
    try:
        from baby_bot.bot_env import BotEnv
        fps_env = BotEnv()
        obs, info = fps_env.reset()
        print(f"✓ FPS bot environment created, observation shape: {obs.shape}")
        
        # Test a single step
        action = fps_env.action_space.sample()
        obs, reward, terminated, truncated, info = fps_env.step(action)
        print(f"✓ FPS step completed, reward: {reward}")
    except Exception as e:
        print(f"✗ Error testing FPS environment: {e}")
    
    # Test baby FPS environment
    try:
        from baby_bot.sample_fps_game import BabyFPSGameEnv
        baby_fps_env = BabyFPSGameEnv()
        obs, info = baby_fps_env.reset()
        print(f"✓ Baby FPS game environment created, observation shape: {obs.shape}")
        
        # Test a single step
        action = baby_fps_env.action_space.sample()
        obs, reward, terminated, truncated, info = baby_fps_env.step(action)
        print(f"✓ Baby FPS step completed, reward: {reward}")
    except Exception as e:
        print(f"✗ Error testing baby FPS environment: {e}")

def test_bots():
    """Test that bots can be created and used"""
    print("\nTesting bots...")
    
    try:
        from baby_bot.baby_bot import BabyFPSBot, BabyBackroomsBot
        from baby_bot.bot_env import BotEnv
        
        # Create FPS bot
        fps_env = BotEnv()
        fps_bot = BabyFPSBot(fps_env)
        print("✓ BabyFPSBot created successfully")
        
        # Test FPS bot action
        obs, info = fps_env.reset()
        action = fps_bot.get_smart_action(obs)
        print(f"✓ FPS bot smart action: {action}")
        
    except Exception as e:
        print(f"✗ Error testing FPS bot: {e}")
    
    try:
        from baby_bot.baby_bot import BabyBackroomsBot
        from StubbornBackroomGame_v4_masterpiece import BackroomsGymEnv
        
        # Create backrooms bot
        backrooms_env = BackroomsGymEnv()
        backrooms_bot = BabyBackroomsBot(backrooms_env)
        print("✓ BabyBackroomsBot created successfully")
        
        # Test backrooms bot action
        obs, info = backrooms_env.reset()
        action = backrooms_bot.get_smart_action(obs)
        print(f"✓ Backrooms bot smart action: {action}")
        
    except Exception as e:
        print(f"✗ Error testing backrooms bot: {e}")

if __name__ == "__main__":
    print("Testing StubbornBackrooms Game Integration")
    print("="*50)
    
    test_imports()
    test_gym_environments()
    test_bots()
    
    print("\n" + "="*50)
    print("Integration test completed!")