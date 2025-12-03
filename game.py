# main game script - StubbornBackroom: Psycho Dream

# there is known 3d game creation libraries (
# import panda3d
# import ursina (panda3d)
# import pygame
# import pyglet
# import OpenGL.GL as gl )

from dataclasses import dataclass
import numpy as np
import random
import time
import sys
import os
# from controls import MouseInput, KeyboardInput
# from audio_module import BackgroundMusic, SoundEffect
# from maps import Map # huge map generated map_generator.py or created by our script map_editor.py
# from something import something

@dataclass
class Config:
    window_size: tuple = (1280, 720)
    window_type = 'windowed'  # ['windowed', 'fullscreen', 'borderless']
    fps: int = 60
    title: str = "StubbornBackroom: Psycho Dream"
    icon_path: str = "textures/wall_texture.png"


class Game:
    def __init__(self):
        self.config = Config()
        pass

