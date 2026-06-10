"""Quantum Breakout - entry point (desktop + browser via pygbag).

Browser-build rules, learned the hard way:
  1. Bring the SDL display up (pygame.init + set_mode) BEFORE importing the game
     modules - importing image/font-loading code before the canvas exists breaks
     display init in pygbag.
  2. Never import numpy on the startup path. Importing numpy inside pygbag poisons
     the SDL display (grey screen / "video driver did not add any displays").
     qcge's backend="auto" resolves to its dependency-free pure-Python simulator in
     the browser (and to real Qiskit on the desktop), so no numpy is needed.
"""

import asyncio

import pygame

from assets import globals


def start_music():
    # Runs on desktop and in the browser. Browsers block autoplay until the
    # player's first gesture; pygbag resumes the queued stream on that gesture.
    try:
        from pygame import mixer
        mixer.init()
        mixer.music.load('./assets/8BitAdventure.ogg')
        mixer.music.set_volume(0.9)
        mixer.music.play(-1)  # loop the background track
    except Exception:
        pass


async def main():
    # Display first, then import the (image/font-loading) game modules.
    pygame.init()
    screen = pygame.display.set_mode((globals.WINDOW_WIDTH, globals.WINDOW_HEIGHT))
    pygame.display.set_caption('Quantum Breakout')
    clock = pygame.time.Clock()

    start_music()

    from assets import scene

    scene_manager = scene.SceneManager()
    scene_manager.push(scene.HowToPlayScene())

    while not scene_manager.exit:
        scene_manager.update()
        scene_manager.draw(screen)
        clock.tick(60)
        await asyncio.sleep(0)  # yield to the browser each frame (no-op on desktop)


asyncio.run(main())
