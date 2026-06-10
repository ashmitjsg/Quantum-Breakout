import pygame

from qcge import QuantumCircuitGrid
from assets import globals, ui, paddle, ball, computer, resources, bricks

class Scene:
    def __init__(self) -> None:
        pass
    def update(self, sm):
        pass
    def draw(self, sm, screen):
        pass

class SceneManager:
    def __init__(self) -> None:
        self.scenes = []
        self.exit = False
    def update(self):
        if len(self.scenes) > 0:
            self.scenes[-1].update(self)

    def draw(self, screen):
        screen.fill(globals.BLACK) # Clear the frame after every second and redraw updated objects
        if len(self.scenes) > 0:
            self.scenes[-1].draw(self, screen)
        pygame.display.flip()
    def push(self, scene):
        self.scenes.append(scene)

class GameScene(Scene):
    def __init__(self) -> None:
        super().__init__()
        # The circuit UI + simulation are now provided by the reusable qcge engine
        # (pip install qcge). backend="auto" -> real Qiskit on desktop, numpy
        # statevector simulator in the browser build.
        self.circuit_grid = QuantumCircuitGrid(
            position=(5, globals.FIELD_HEIGHT),
            num_qubits=globals.NUM_QUBITS,
            num_columns=16,
            assets_path="assets/images/gates",
        )
        self.quantum_paddles = paddle.QuantumPaddles(globals.STATEVECTOR_WIDTH)
        self.quantum_computer = computer.QuantumComputer(self.quantum_paddles, self.circuit_grid)
        self.game_ball = ball.Ball()
        self.brick_layers = bricks.BricksLayers()
        self.moving_sprites = pygame.sprite.Group()
        self.moving_sprites.add(self.quantum_paddles.paddles)
        self.moving_sprites.add(self.game_ball)
        
    
    def update(self, sm):
        for event in pygame.event.get():
            ## Detect Close and Exit
            if event.type == pygame.QUIT:
                sm.exit = True
            elif event.type == pygame.KEYDOWN:
                self.circuit_grid.handle_input(event.key)
            
            # if event.type == pygame.K_p:
            #     print("pressed Pause")
            #     sm.push(PauseScene())

        self.game_ball.update(self.quantum_computer)
        self.quantum_computer.update(self.game_ball)

        ## Collision of Ball and Bricks
        for brick in self.brick_layers.bricks:
            ball_x = self.game_ball.rect.x
            ball_y = self.game_ball.rect.y
            brick_x = brick.rect.x
            brick_y = brick.rect.y
            if (ball_x >= brick_x and ball_x <= (brick_x + globals.BRICK_WIDTH)) or ((ball_x + globals.BALL_SIZE) >= brick_x and (ball_x + globals.BALL_SIZE) <= (brick_x + globals.BRICK_WIDTH)):
                if (ball_y >= brick_y and ball_y <= (brick_y + globals.BRICK_HEIGHT)) or ((ball_y + globals.BALL_SIZE) >= brick_y and (ball_y + globals.BALL_SIZE) <= (brick_y + globals.BRICK_HEIGHT)):
                    brick.visible = False
                    self.brick_layers.bricks.pop(self.brick_layers.bricks.index(brick))
                    self.game_ball.bounce()
                    # Increase Player Score
                    globals.player_score += 1
        
        ## WIN CONDITION
        if globals.player_score >= globals.WIN_SCORE:
            print("Player won the game")
            sm.push(WinScene())

        ## LOSE CONDITION
        if globals.ball_dropped >= globals.LOSE_SCORE:
            print("Player lose the game")
            sm.push(LoseScene())


    def draw(self, sm, screen):
        self.circuit_grid.update()      # refresh gate sprites + positions each frame
        self.circuit_grid.draw(screen)
        ui.draw_statevector_grid(screen)
        ui.draw_score(screen, globals.player_score)
        self.moving_sprites.draw(screen)

        for brick in self.brick_layers.bricks:
            brick.draw(screen)

class LoseScene(Scene):
    def __init__(self) -> None:
        super().__init__()

    def update(self, sm):
        # RESET PLAYER DATA
        globals.player_score = 0
        globals.ball_dropped = 0

        # DETECT KEY PRESS AND DO ACTION
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sm.exit = True
            elif event.type == pygame.KEYDOWN:
                # press SPACE to reply
                if event.key == pygame.K_SPACE:
                    sm.push(GameScene())

    def draw(self, sm, screen):
        font = resources.Font()

        gameover_text = "Game Over"
        text = font.gameover_font.render(gameover_text, 1, globals.WHITE)
        text_pos = text.get_rect(center=(globals.WINDOW_WIDTH/2, globals.WIDTH_UNIT*20))
        screen.blit(text, text_pos)

        gameover_text = "Press Space to Replay!"
        text = font.replay_font.render(gameover_text, 5, globals.WHITE)
        text_pos = text.get_rect(center=(globals.WINDOW_WIDTH/2, globals.WIDTH_UNIT*30))
        screen.blit(text, text_pos)

class WinScene(Scene):
    def __init__(self) -> None:
        super().__init__()

    def update(self, sm):
        for event in pygame.event.get():
            # RESET PLAYER DATA
            globals.player_score = 0
            globals.ball_dropped = 0

            # DETECT KEY PRESS AND DO ACTION
            if event.type == pygame.QUIT:
                sm.exit = True
            elif event.type == pygame.KEYDOWN:
                # press SPACE to reply
                if event.key == pygame.K_SPACE:
                    sm.push(GameScene())

    def draw(self, sm, screen):
        font = resources.Font()

        gameover_text = "Congratulations!"
        text = font.gameover_font.render(gameover_text, 5, globals.WHITE)
        text_pos = text.get_rect(center=(globals.WINDOW_WIDTH/2, globals.WIDTH_UNIT*20))
        screen.blit(text, text_pos)

        gameover_text = "You demonstrated quantum advantage"
        text = font.replay_font.render(gameover_text, 5, globals.WHITE)
        text_pos = text.get_rect(center=(globals.WINDOW_WIDTH/2, globals.WIDTH_UNIT*30))
        screen.blit(text, text_pos)

        gameover_text = "Press Space to Replay!"
        text = font.replay_font.render(gameover_text, 5, globals.WHITE)
        text_pos = text.get_rect(center=(globals.WINDOW_WIDTH/2, globals.WIDTH_UNIT*35))
        screen.blit(text, text_pos)

# class PauseScene(Scene):
#     def __init__(self) -> None:
#         super().__init__()
#         print("Entered Pause");

#     def update(self, sm):
#         # DETECT KEY PRESS AND DO ACTION
#         for event in pygame.event.get():
#             if event.type == pygame.K_p:
#                 pass
        
#     def draw(self, sm, screen):
#         font = resources.Font()

#         gameover_text = "Press Space to get back to game!"
#         text = font.gameover_font.render(gameover_text, 5, globals.WHITE)
#         text_pos = text.get_rect(center=(globals.WINDOW_WIDTH/2, globals.WIDTH_UNIT*20))
#         screen.blit(text, text_pos)