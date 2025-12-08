#!/usr/bin/env python3
"""
Demonstration of Enemy AI System for StubbornBackrooms game
This script demonstrates the enemy AI without requiring the full game
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enemy_ai_system import EnemyManager, EnemyType
import numpy as np

def demonstrate_enemy_system():
    """
    Demonstrate the enemy AI system
    """
    print("=== StubbornBackrooms Enemy AI Demonstration ===")
    print()
    
    # Create enemy manager
    enemy_manager = EnemyManager()
    
    # Add different types of enemies
    print("1. Creating enemies...")
    watcher = enemy_manager.add_enemy(EnemyType.WATCHER, (5.0, 0.0, 5.0))
    hunter = enemy_manager.add_enemy(EnemyType.HUNTER, (-3.0, 0.0, 8.0))
    smiler = enemy_manager.add_enemy(EnemyType.SMILER, (7.0, 0.0, -2.0))
    
    print(f"   Created {len(enemy_manager.get_alive_enemies())} enemies:")
    for i, enemy in enumerate(enemy_manager.get_alive_enemies()):
        print(f"   - Enemy {i+1}: {enemy.enemy_type.value} at {enemy.position}")
    print()
    
    # Simulate game loop
    print("2. Simulating game loop (100 steps)...")
    player_pos = (0.0, 0.0, 0.0)
    
    for step in range(100):
        # Move player randomly to trigger enemy responses
        player_pos = (
            player_pos[0] + (np.random.random() - 0.5) * 0.5,
            0.0,
            player_pos[2] + (np.random.random() - 0.5) * 0.5
        )
        
        # Update all enemies
        enemy_manager.update_all(player_pos)
        
        # Print status every 20 steps
        if step % 20 == 0:
            alive_count = len(enemy_manager.get_alive_enemies())
            print(f"   Step {step}: {alive_count} enemies alive")
            for i, enemy in enumerate(enemy_manager.get_alive_enemies()):
                print(f"     - {enemy.enemy_type.value}: State={enemy.state}, Pos={enemy.position[:2]}")
    
    final_count = len(enemy_manager.get_alive_enemies())
    print(f"   Final: {final_count} enemies alive")
    print()
    
    # Demonstrate AI decision making
    print("3. Demonstrating AI decision making...")
    sample_enemy = enemy_manager.get_alive_enemies()[0] if enemy_manager.get_alive_enemies() else None
    
    if sample_enemy:
        # Create a sample state vector for decision making
        # [enemy_x, enemy_y, enemy_z, player_x, player_y, player_z, dist, enemy_health, player_health, time]
        state_vector = [
            sample_enemy.position[0], sample_enemy.position[1], sample_enemy.position[2],
            player_pos[0], player_pos[1], player_pos[2],
            np.linalg.norm(np.array(sample_enemy.position) - np.array(player_pos)),
            sample_enemy.health, 100,  # Assuming player health is 100
            0  # time step
        ]
        
        decision = sample_enemy.get_ai_decision(state_vector)
        action_names = ["forward", "backward", "left", "right", "stay"]
        print(f"   Sample state vector: {state_vector[:5]}...")  # Show first 5 elements
        print(f"   AI decision: {action_names[decision]} (action {decision})")
    print()
    
    # Show enemy types and their characteristics
    print("4. Enemy types and characteristics:")
    enemies = enemy_manager.get_alive_enemies()
    for enemy in enemies:
        print(f"   - {enemy.enemy_type.value}:")
        print(f"     Speed: {enemy.speed}")
        print(f"     Detection radius: {enemy.detection_radius}")
        print(f"     Position: {enemy.position}")
        print(f"     State: {enemy.state}")
    print()
    
    print("=== Enemy AI Demonstration Complete ===")

def demonstrate_training_concept():
    """
    Demonstrate the concept of training enemies
    """
    print("=== Enemy Training Concept ===")
    print()
    print("Enemy training involves:")
    print("1. Creating adversarial environments where enemies learn to hunt players")
    print("2. Using reinforcement learning to improve enemy hunting strategies")
    print("3. Training enemies to predict and intercept player movements")
    print("4. Creating enemy behaviors that adapt to player strategies")
    print()
    
    print("Training process:")
    print("- Enemy observes player position and movement patterns")
    print("- Takes actions to minimize distance to player")
    print("- Receives rewards for successful interceptions")
    print("- Updates neural network weights based on outcomes")
    print()
    
    print("Enemy types and behaviors:")
    print("- WATCHER: Observes from a distance, moves slowly but strategically")
    print("- SMILER: Fast and aggressive, chases player directly")
    print("- HUNTER: Highly aggressive, fastest movement, high detection range")
    print("- FACADE: Deceptive, may hide or pretend to be harmless")
    print()
    
    print("=== Training Concept Complete ===")

if __name__ == "__main__":
    demonstrate_enemy_system()
    print()
    demonstrate_training_concept()
    
    print("\n=== How to Train Models ===")
    print()
    print("To train a player agent:")
    print("  python train_backrooms_agent.py")
    print()
    print("To train enemies against the player:")
    print("  python train_enemies.py")
    print()
    print("To use the enemy AI system in your game:")
    print("  1. Create an EnemyManager instance")
    print("  2. Add enemies with specific types and positions")
    print("  3. Call update_all() each game frame with player position")
    print("  4. Access enemy positions and states for rendering")
    print()
    print("The enemy AI system is now ready for integration with your game!")