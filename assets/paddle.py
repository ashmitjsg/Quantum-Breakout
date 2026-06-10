import pygame

from . import globals

class Paddle(pygame.sprite.Sprite):
    def __init__(self, x_pos=0, y_pos=0):
        super().__init__()

        self.image = pygame.Surface([globals.PADDLE_WIDTH, globals.PADDLE_HEIGHT])
        self.image.fill(globals.WHITE)
        # start hidden; the quantum computer reveals each paddle in proportion to
        # its state probability, so the empty circuit doesn't flash a full-width bar
        self.image.set_alpha(0)
        self.rect = self.image.get_rect()
        self.rect.x = x_pos
        self.rect.y = y_pos

class QuantumPaddles:
    def __init__(self, x_pos=0, y_pos=globals.WINDOW_HEIGHT * 0.6):
        self.paddles = []
        for i in range(2**globals.NUM_QUBITS):
            self.paddles.append(Paddle(i*x_pos, y_pos))
