# Liminalcore Backrooms Project

## Overview
This project contains multiple optimized versions of the StubbornBackrooms game with different features and capabilities. The core concept is to create a liminal, backrooms-style experience with reality distortion effects and pre-made maps instead of procedural generation.

## Project Structure

### Main Game Versions

1. **StubbornBackroomGame_v1_optimized.py** - Enhanced version with full features
   - Uses pre-made maps from the `maps/` directory
   - Enhanced reality distortion system
   - Performance improvements
   - Map switching with 'M' key
   - 3D Map Editor integration (placeholder)

2. **StubbornBackroomGame_v2_optimized.py** - High-performance version
   - Reduced particle effects for better performance
   - Simplified shaders
   - Optimized entity management
   - Minimal decoration system

3. **StubbornBackroomGame_v3_gymnasium.py** - Gymnasium-compatible environment for AI training
   - OpenAI Gymnasium interface
   - Action space: [forward, backward, left, right, jump]
   - Observation space: [position_x, position_y, position_z, distortion_level, stability, reality_state]
   - Reward system based on exploration and stability

4. **StubbornBackroomGame_v4_masterpiece.py** - **NEW MASTERPIECE VERSION**
   - **Highly optimized with pre-made maps only (no procedural generation)**
   - **Best performance and stability**
   - **Gymnasium integration included**
   - Reality distortion system
   - Map switching functionality
   - Perfect for AI training and smooth gameplay

### Baby Bot Integration

The project also includes gymnasium-compatible baby bot implementations:

- **baby_bot/bot_env.py** - FPS Game Bot Environment
  - Action space: [move_forward, move_backward, move_left, move_right, jump, shoot]
  - Observation space: [player_x, player_y, player_z, health, ammo, enemies_nearby, distance_to_closest_enemy]

- **baby_bot/bot.py** - Simple bot implementation with training and testing capabilities
  - Smart action selection based on game state

- **baby_bot/baby_bot.py** - **NEW ADVANCED BOT** with both FPS and Backrooms support
  - Includes BabyFPSBot for FPS games
  - Includes BabyBackroomsBot for Backrooms games
  - Ready for gymnasium integration with both game types

- **sample_fps_game_gym.py** - Gymnasium-compatible version of the sample FPS game
- **baby_bot/sample_fps_game.py** - FPS game specifically designed for baby bot training

## Features

### Liminalcore Aesthetics
- Custom color palette with liminal yellows, beiges, and ambers
- Reality distortion system with 4 states: STABLE, DISTORTED, LIMINAL, CHAOTIC
- Dynamic fog and lighting effects
- Floating particles and liminal messages
- Procedural room generation from pre-made maps

### Performance Optimizations
- Pre-made map system instead of procedural chunk generation
- Efficient entity management
- Reduced particle systems in performance version
- Simplified shaders for better frame rates

### Gymnasium Integration
- Full OpenAI Gymnasium compatibility
- Custom reward systems
- Proper observation and action spaces
- Episode termination conditions

## Installation

```bash
pip install ursina gymnasium numpy
```

## Usage

### Running the Optimized Backrooms Game
```bash
python StubbornBackroomGame_v1_optimized.py
```

### Running the Baby Bot
```bash
python -m baby_bot.bot
```

### Using the Gym Environment
```python
from StubbornBackroomGame_v3_gymnasium import BackroomsEnv

env = BackroomsEnv()
obs = env.reset()
done = False

while not done:
    action = env.action_space.sample()  # or use your agent
    obs, reward, terminated, truncated, info = env.step(action)
    done = terminated or truncated
```

## Controls

### Optimized Backrooms Game
- WASD: Move
- Mouse: Look around
- Space: Jump
- F5: Toggle debug info
- Tab: Reality distortion view
- M: Switch maps
- E: Open 3D Map Editor
- Esc: Quit

### FPS Game
- WASD: Move
- Mouse: Aim
- Left Click: Shoot
- X: Save position
- Z: Return to saved position
- F: Fly up
- Esc: Quit

## Map Files

The game uses pre-made maps stored in the `maps/` directory. You can create new maps using the 3D Map Editor or manually create JSON files with the following structure:

```json
{
  "width": 10,
  "height": 10,
  "map": [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 2, 0, 0, 0, 0, 2, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 2, 0, 0, 0, 0, 2, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
  ],
  "entities": []
}
```

Map Legend:
- `0`: Path (walkable area)
- `1`: Wall (solid wall)
- `2`: Doorway (passage between rooms)
- `3`: Special room
- `4`: Liminal space

## Development Notes

The project was refactored to remove the chunk generation system like Minecraft, focusing instead on pre-made maps for better performance and consistency. The gymnasium integration allows for AI training and reinforcement learning applications.

The liminalcore aesthetic is maintained throughout all versions with careful attention to color palettes, atmosphere, and reality distortion effects that create the characteristic "backrooms" feeling.

## AI Training System

The project now includes a complete AI training system with:

### Player Training
- **train_backrooms_agent.py** - Trains a player agent using Deep Q-Network (DQN)
- Uses reinforcement learning to navigate the backrooms environment
- Optimized for exploration and survival

### Enemy AI System
- **enemy_ai_system.py** - Advanced enemy AI with multiple enemy types:
  - WATCHER: Observes from a distance, moves slowly but strategically
  - SMILER: Fast and aggressive, chases player directly
  - HUNTER: Highly aggressive, fastest movement, high detection range
  - FACADE: Deceptive, may hide or pretend to be harmless
- Each enemy type has unique behaviors and characteristics
- Neural network-based decision making
- Adaptable to player strategies

### Enemy Training
- **train_enemies.py** - Trains enemies to hunt the player
- Uses adversarial reinforcement learning
- Enemies learn to predict and intercept player movements
- Creates challenging opponents that adapt to player behavior

### Integration
- **integrate_enemy_ai.py** - Demonstrates how to integrate enemy AI into the game
- **demo_enemy_ai.py** - Shows enemy AI functionality without full game

## Training Commands

### Train Player Agent
```bash
python train_backrooms_agent.py
```

### Train Enemy Agents
```bash
python train_enemies.py
```

### Run Enemy AI Demo
```bash
python demo_enemy_ai.py
```

## Usage Examples

### Training a Player Agent
```python
from train_backrooms_agent import train_agent

# Train for 1000 episodes
agent = train_agent(episodes=1000)
```

### Using Enemy AI in Your Game
```python
from enemy_ai_system import EnemyManager, EnemyType

# Create enemy manager
enemy_manager = EnemyManager()

# Add enemies
watcher = enemy_manager.add_enemy(EnemyType.WATCHER, (5.0, 0.0, 5.0))
hunter = enemy_manager.add_enemy(EnemyType.HUNTER, (-3.0, 0.0, 8.0))

# Update enemies each frame with player position
enemy_manager.update_all(player_pos)

# Get enemy positions for rendering
enemy_positions = enemy_manager.get_enemy_positions()
```
