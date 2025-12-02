import pyglet.media as media

class BackgroundMusic:
    def __init__(self):
        self.music = media.load("./atomiste.mp3")
        self.player = media.Player
    def play_audio_no(self):
        self.player = media.Player()
        self.player.queue(preload)
        self.player.play()

    def play_audio(self):
        self.player = self.music.play()
        self.player.volume = 1.0
    def mute(self):
        self.player.volume = 0
    def pause(self):
        self.player.pause()
    def normalize(self):
        self.player.volume = 1.0
