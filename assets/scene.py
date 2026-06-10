import pygame

from qcge import QuantumCircuitGrid
from assets import globals, ui, paddle, ball, computer, resources, bricks, levels


def draw_centered_lines(screen, font, lines, start_y, color=globals.WHITE, line_gap=None):
    """Blit a sequence of text lines, horizontally centered, stacked from start_y.

    Shared by every text screen (how-to-play, concept boards, end screens) so the
    layout logic lives in one place.
    """
    line_gap = line_gap or int(font.get_height() * 1.3)
    for i, line in enumerate(lines):
        if not line:
            continue
        surf = font.render(line, 1, color)
        pos = surf.get_rect(center=(globals.WINDOW_WIDTH / 2, start_y + i * line_gap))
        screen.blit(surf, pos)


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
    def __init__(self, level=None) -> None:
        super().__init__()
        self.level = level or levels.LEVELS[0]
        # fresh score per level attempt
        globals.player_score = 0
        globals.ball_dropped = 0
        # The circuit UI + simulation are now provided by the reusable qcge engine
        # (pip install qcge). backend="auto" -> real Qiskit on desktop, pure-Python
        # statevector simulator in the browser build.
        self.circuit_grid = QuantumCircuitGrid(
            position=(5, globals.FIELD_HEIGHT),
            num_qubits=globals.NUM_QUBITS,
            num_columns=16,
            tile_size=66,                       # fills the width and reaches the bottom
            background_color=globals.WHITE,     # match the original look
            wire_color=globals.BLACK,
            assets_path="assets/images/gates",
            movement_keys="arrows",             # arrows move the cursor, so S/T are free for gates
            allowed_gates=self.level.allowed_gates,  # per-level gate palette (None = all)
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
        
        ## WIN CONDITION -> advance to the next level's concept board, or finish
        if globals.player_score >= self.level.win_score:
            next_number = self.level.number + 1
            if next_number <= len(levels.LEVELS):
                sm.push(ConceptBoardScene(levels.LEVELS[next_number - 1]))
            else:
                sm.push(WinScene())

        ## LOSE CONDITION
        if globals.ball_dropped >= self.level.lose_score:
            sm.push(LoseScene(self.level))


    def draw(self, sm, screen):
        self.circuit_grid.update()      # refresh gate sprites + positions each frame
        self.circuit_grid.draw(screen)
        ui.draw_statevector_grid(screen)
        ui.draw_score(screen, globals.player_score, self.level.win_score)

        # level banner + objective, centered just above the circuit grid (clear of
        # the bricks at the top of the screen)
        font = resources.Font()
        banner = font.vector_font.render(
            f"Level {self.level.number}: {self.level.title}", 1, globals.MAGENTA
        )
        paddle_top = globals.WINDOW_HEIGHT * 0.6
        screen.blit(banner, banner.get_rect(center=(globals.WINDOW_WIDTH / 2, paddle_top - 52)))
        goal = font.vector_font.render(self.level.goal, 1, globals.GRAY)
        screen.blit(goal, goal.get_rect(center=(globals.WINDOW_WIDTH / 2, paddle_top - 24)))

        # live "drops left" counter under the bricks counter, so the lose limit is visible
        drops_left = max(0, self.level.lose_score - globals.ball_dropped)
        drops = font.vector_font.render(f"Drops left: {drops_left}", 1, globals.WHITE)
        screen.blit(drops, drops.get_rect(center=(globals.WINDOW_WIDTH / 2, globals.WINDOW_HEIGHT * 0.47)))

        self.moving_sprites.draw(screen)

        for brick in self.brick_layers.bricks:
            brick.draw(screen)

class LoseScene(Scene):
    def __init__(self, level=None) -> None:
        super().__init__()
        self.level = level or levels.LEVELS[0]

    def update(self, sm):
        # DETECT KEY PRESS AND DO ACTION
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sm.exit = True
            elif event.type == pygame.KEYDOWN:
                # press SPACE to retry the same level (GameScene resets the score)
                if event.key == pygame.K_SPACE:
                    sm.push(GameScene(self.level))

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


class HowToPlayScene(Scene):
    """Opening screen: the goal + controls. Self-contained onboarding so the game
    teaches how to play without any external README."""

    CONTROLS = (
        "QUANTUM BREAKOUT",
        "",
        "Your paddle is a quantum state - build a",
        "circuit to aim it, then break the bricks.",
        "",
        "Arrow keys  -  move the cursor",
        "X  Y  Z  H  -  place that gate",
        "S  T  -  phase gates",
        "C  then  R / F  -  add a control (CX)",
        "Q  E  -  rotate by  -/+ pi/8",
        "Backspace  -  remove     Delete  -  clear",
        "",
        "Press SPACE to begin.",
    )

    def update(self, sm):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sm.exit = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                sm.push(ConceptBoardScene(levels.LEVELS[0]))

    def draw(self, sm, screen):
        font = resources.Font()
        draw_centered_lines(screen, font.vector_font, self.CONTROLS, globals.WIDTH_UNIT * 8)


class ConceptBoardScene(Scene):
    """The in-game teaching board shown before each level: explains the level's
    quantum concept, then drops the player into that level on SPACE."""

    def __init__(self, level) -> None:
        super().__init__()
        self.level = level

    def update(self, sm):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sm.exit = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                sm.push(GameScene(self.level))

    def draw(self, sm, screen):
        font = resources.Font()
        title = font.replay_font.render(
            f"Level {self.level.number}: {self.level.title}", 1, globals.MAGENTA
        )
        screen.blit(title, title.get_rect(center=(globals.WINDOW_WIDTH / 2, globals.WIDTH_UNIT * 8)))

        draw_centered_lines(screen, font.vector_font, self.level.lines, globals.WIDTH_UNIT * 16)

        gate = font.vector_font.render(f"Gate(s): {self.level.gate_hint}", 1, globals.GRAY)
        screen.blit(gate, gate.get_rect(center=(globals.WINDOW_WIDTH / 2, globals.WIDTH_UNIT * 46)))
        prompt = font.vector_font.render("Press SPACE to play", 1, globals.WHITE)
        screen.blit(prompt, prompt.get_rect(center=(globals.WINDOW_WIDTH / 2, globals.WIDTH_UNIT * 52)))


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