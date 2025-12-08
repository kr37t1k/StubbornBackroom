# StubbornBackrooms Training and Enemy AI Guide

This guide explains how to train AI models and use the enemy AI system in the StubbornBackrooms game.

## Table of Contents
1. [Training Player Agents](#training-player-agents)
2. [Training Enemy Agents](#training-enemy-agents)
3. [Using Enemy AI in Games](#using-enemy-ai-in-games)
4. [Advanced Training Concepts](#advanced-training-concepts)

## Training Player Agents

### Overview
The player training system uses Deep Q-Network (DQN) reinforcement learning to train agents that can navigate the backrooms environment effectively.

### Files
- `train_backrooms_agent.py` - Main training script for player agents

### Training Process
1. The agent learns through trial and error in the backrooms environment
2. It receives rewards for exploration and maintaining stability
3. The neural network updates based on experiences stored in memory
4. Over time, the agent learns optimal navigation strategies

### Running Player Training
```bash
python train_backrooms_agent.py
```

### Parameters
- Episodes: Number of training episodes (default: 1000)
- Learning rate: How quickly the agent updates its knowledge (default: 0.001)
- Epsilon decay: Exploration vs exploitation balance (default: 0.995)

## Training Enemy Agents

### Overview
Enemy training uses adversarial reinforcement learning where enemies learn to hunt and intercept players.

### Files
- `train_enemies.py` - Main training script for enemy agents

### Training Process
1. Enemies learn to minimize distance to the player
2. They receive rewards for successful interceptions
3. The neural network learns to predict player movements
4. Enemies develop adaptive hunting strategies

### Running Enemy Training
```bash
python train_enemies.py
```

### Enemy Types and Behaviors

#### WATCHER
- **Speed**: 1.5 (slow)
- **Detection Radius**: 15.0 units
- **Behavior**: Observes from a distance, moves strategically
- **Strategy**: Waits for opportunities, flanks the player

#### SMILER
- **Speed**: 2.0 (medium-fast)
- **Detection Radius**: 10.0 units
- **Behavior**: Fast and aggressive, direct chase
- **Strategy**: Pursues player directly, high-pressure tactics

#### HUNTER
- **Speed**: 3.0 (fastest)
- **Detection Radius**: 20.0 units (largest)
- **Behavior**: Highly aggressive, relentless pursuit
- **Strategy**: Most dangerous enemy, quick to respond

#### FACADE
- **Speed**: 1.0 (slowest)
- **Detection Radius**: 5.0 units (smallest)
- **Behavior**: Deceptive, may appear harmless
- **Strategy**: Ambush tactics, surprise attacks

## Using Enemy AI in Games

### Basic Integration
```python
from enemy_ai_system import EnemyManager, EnemyType

# Create enemy manager
enemy_manager = EnemyManager()

# Add different types of enemies
watcher = enemy_manager.add_enemy(EnemyType.WATCHER, (5.0, 0.0, 5.0))
hunter = enemy_manager.add_enemy(EnemyType.HUNTER, (-3.0, 0.0, 8.0))
smiler = enemy_manager.add_enemy(EnemyType.SMILER, (7.0, 0.0, -2.0))

# In your game loop, update enemies with player position
player_pos = (0.0, 0.0, 0.0)  # Example player position
enemy_manager.update_all(player_pos)

# Get enemy information for rendering
alive_enemies = enemy_manager.get_alive_enemies()
enemy_positions = enemy_manager.get_enemy_positions()
```

### Advanced Usage
```python
# Load trained models for enemies (if available)
enemy_manager = EnemyManager()
enemy_manager.default_model_path = "trained_enemy_model.pth"

# Add enemy with potential model loading
hunter = enemy_manager.add_enemy(EnemyType.HUNTER, (10.0, 0.0, 10.0))

# Get detailed enemy information
for enemy in enemy_manager.get_alive_enemies():
    info = enemy.get_render_info()
    print(f"Enemy: {info['type']}, Position: {info['position']}, Health: {info['health']}")
```

### Enemy Decision Making
Enemies make decisions based on:
- Distance to player
- Current state (idle, chasing, attacking)
- Health status
- Environmental factors
- Previous experiences (if trained)

## Advanced Training Concepts

### State Representation
The neural networks use state vectors containing:
- Enemy position (x, y, z)
- Player position (x, y, z)
- Distance between enemy and player
- Enemy health
- Player health
- Environmental factors
- Time step

### Action Space
Actions available to agents:
- 0: Move forward
- 1: Move backward
- 2: Move left
- 3: Move right
- 4: Stay in place

### Reward System
#### For Player Agents:
- Positive rewards for exploration
- Positive rewards for maintaining stability
- Negative rewards for entering chaotic areas
- Bonus rewards for discovering new areas

#### For Enemy Agents:
- Negative rewards for distance from player (closer is better)
- Positive rewards for intercepting player
- Bonus rewards for successful captures
- Negative rewards for being too far from player

### Neural Network Architecture
The system uses a simple but effective neural network:
- Input layer: State vector
- Hidden layer 1: 64 neurons with tanh activation
- Hidden layer 2: 32 neurons with tanh activation
- Output layer: Action values (Q-values)

### Training Tips
1. **Start Simple**: Begin with basic environments before complex scenarios
2. **Balance Exploration**: Adjust epsilon decay to balance exploration vs exploitation
3. **Monitor Progress**: Track rewards to ensure learning is occurring
4. **Save Models**: Regularly save trained models to preserve progress
5. **Test Regularly**: Evaluate agents in actual gameplay scenarios

### Troubleshooting
- **Slow Learning**: Increase learning rate or number of episodes
- **Poor Performance**: Check reward structure and state representation
- **Overfitting**: Add more diverse training scenarios
- **Memory Issues**: Reduce memory buffer size or batch size

## Integration with Gymnasium Environments

The system is fully compatible with gymnasium environments:
```python
from StubbornBackroomGame_v3_gymnasium import BackroomsEnv

# Create environment with enemy integration
env = BackroomsEnv()
obs, info = env.reset()

for step in range(1000):
    action = env.action_space.sample()  # or use trained agent
    obs, reward, terminated, truncated, info = env.step(action)
    
    # Access enemy information from info dict
    if 'enemies' in info:
        enemy_info = info['enemies']
        # Process enemy information as needed
```

## Best Practices

### For Player Training:
- Start with shorter episodes to speed up initial learning
- Use curriculum learning (start with simpler maps)
- Implement proper reward shaping for desired behaviors

### For Enemy Training:
- Train against multiple player strategies
- Include environmental awareness in state vectors
- Use adversarial training for robust opponents

### For Game Integration:
- Update enemy positions at consistent intervals
- Implement proper collision detection
- Balance enemy difficulty for player experience
- Provide visual/audio feedback for enemy presence

This system provides a complete framework for training AI agents that can navigate the backrooms environment and create challenging, adaptive opponents for players.