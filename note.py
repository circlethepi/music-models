import key_length as kl
import song_processer as ps

class note :
    def __init__(self, pitch, duration):
        self.pitch = pitch
        self.duration = duration
        self.note = (self.pitch, self.duration)


