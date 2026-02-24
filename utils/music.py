import pygame
from utils.helpers import resource_path

class MusicManager:
    def __init__(self):
        pygame.mixer.init()
        self.music_path = resource_path("assets/bg.mp3")
        self.enabled = True
        self.is_playing = False
        self.volume = 0.30

    def start(self):
        if not self.enabled:
            return
        if not self.is_playing:
            pygame.mixer.music.load(self.music_path)
            pygame.mixer.music.play(-1)
            self.is_playing = True
        pygame.mixer.music.set_volume(self.volume)

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False

    def toggle(self):
        self.enabled = not self.enabled
        if self.enabled:
            self.start()
        else:
            self.stop()

    def set_volume(self, value):
        # value expected 0..1
        self.volume = max(0.0, min(1.0, float(value)))
        pygame.mixer.music.set_volume(self.volume)