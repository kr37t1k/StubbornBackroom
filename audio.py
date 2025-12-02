import pygame
import os

class BackgroundMusic:
    def __init__(self):
        try:
            if os.path.exists("./atomiste.mp3"):
                pygame.mixer.init()
                self.music = pygame.mixer.Sound("./atomiste.mp3")
                self.channel = None
            else:
                self.music = None
                print("Warning: atomiste.mp3 not found, audio disabled")
        except pygame.error:
            self.music = None
            print("Warning: Audio system not available, audio disabled")
    
    def play_audio(self):
        if self.music:
            try:
                self.channel = self.music.play(-1)  # -1 for loop forever
            except pygame.error:
                print("Warning: Could not play audio")
    
    def mute(self):
        if self.music:
            try:
                self.music.set_volume(0)
            except pygame.error:
                pass
    
    def pause(self):
        if self.channel:
            try:
                self.channel.pause()
            except pygame.error:
                pass
    
    def normalize(self):
        if self.music:
            try:
                self.music.set_volume(1.0)
            except pygame.error:
                pass
