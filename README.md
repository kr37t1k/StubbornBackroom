# StubbornBackrooms

A 3D Backrooms exploration game built with Panda3D. Features procedural generation, atmospheric lighting, textures, and background music.

## Features
- Procedurally generated backrooms environment
- Textured walls, floors, and ceilings
- Background music loop from audio folder
- Atmospheric lighting with flickering effect
- Dream state mechanics with special zones
- Smooth 3D movement and mouse look
- On-screen UI with position and status info

## Requirements
- Python 3.7+
- Panda3D
- noise

## Installation
```bash
pip install panda3d noise
```

## Running the Game
```bash
python panda_backrooms_game.py
```

Controls:
- WASD: Move around
- Mouse: Look around
- ESC: Quit

## Assets
- Textures: Place PNG files in the `textures/` folder
  - Supported: `floor_texture.png`, `floor.png`, `ground.png` for floor
  - Supported: `wall_texture.png`, `wall.png`, `texture.png` for walls
- Audio: Place MP3 files in the `audio/` folder
  - Supported: `atomiste.mp3`, `background.mp3`, `music.mp3`

The game will automatically detect and load the first available texture/audio file from the supported names.