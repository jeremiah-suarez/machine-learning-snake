# basic_snake.py
"""
A minimal, keyboard‑playable Snake game with robust Pygame initialization and logging.
If a window still does not appear, the log will capture why.
"""
import os
import sys
import logging
from pathlib import Path
import random

# -----------------------
# Logging setup
# -----------------------
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "basic_snake.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("basic_snake")
logger.info("=== Basic Snake starting ===")
logger.info(f"Python: {sys.version}")
logger.info(f"Executable: {sys.executable}")

# -----------------------
# Try to initialize pygame video safely
# -----------------------
try:
    import pygame
    logger.info(f"pygame version: {pygame.__version__}")
except Exception:
    logger.exception("Failed to import pygame. Install with: pip install pygame")
    raise

# On some setups, explicitly initialize subsystems
try:
    pygame.init()
    pygame.display.init()
    pygame.font.init()
    logger.info("pygame.init() successful")
except Exception:
    logger.exception("pygame initialization failed")
    raise

# -----------------------
# Game configuration
# -----------------------
CELL = 28
GRID_W, GRID_H = 20, 15
FPS = 10
WIN_W = GRID_W * CELL
INFO_H = 40
WIN_H = GRID_H * CELL + INFO_H

BG = (30, 30, 35)
GRID = (55, 55, 60)
HEAD = (80, 200, 120)
BODY = (60, 170, 100)
FOOD = (220, 70, 70)
TEXT = (230, 230, 230)
INFO_BG = (20, 20, 25)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# -----------------------
# Create window (robust)
# -----------------------
try:
    flags = 0  # pygame.RESIZABLE could be added if desired
    screen = pygame.display.set_mode((WIN_W, WIN_H), flags)
    pygame.display.set_caption("Basic Snake (Playable)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 20)
    logger.info("Window created successfully")
except Exception:
    logger.exception("Failed to create pygame window")
    raise

# -----------------------
# Game state helpers
# -----------------------
class Snake:
    def __init__(self):
        cx, cy = GRID_W // 2, GRID_H // 2
        self.body = [(cx - 1, cy), (cx, cy), (cx + 1, cy)]
        self.dir = RIGHT

    @property
    def head(self):
        return self.body[-1]

    def step(self):
        hx, hy = self.head
        dx, dy = self.dir
        return (hx + dx, hy + dy)

    def move(self, grow=False):
        self.body.append(self.step())
        if not grow:
            self.body.pop(0)

    def turn(self, new_dir):
        # prevent 180-degree turn
        if (self.dir[0] + new_dir[0] == 0) and (self.dir[1] + new_dir[1] == 0):
            return
        self.dir = new_dir


def spawn_food(snake_body):
    while True:
        pos = (random.randint(0, GRID_W - 1), random.randint(0, GRID_H - 1))
        if pos not in snake_body:
            return pos


def draw_grid(surf):
    for x in range(GRID_W):
        pygame.draw.line(surf, GRID, (x * CELL, 0), (x * CELL, GRID_H * CELL), 1)
    for y in range(GRID_H):
        pygame.draw.line(surf, GRID, (0, y * CELL), (GRID_W * CELL, y * CELL), 1)


def draw_cell(surf, pos, color):
    rect = pygame.Rect(pos[0] * CELL + 2, pos[1] * CELL + 2, CELL - 4, CELL - 4)
    pygame.draw.rect(surf, color, rect, border_radius=6)


# -----------------------
# Main game loop
# -----------------------
try:
    snake = Snake()
    food = spawn_food(snake.body)
    score = 0
    game_over = False
    logger.info("Game state initialized")

    logger.info("Entering main loop")
    while True:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logger.info("Quit received; exiting")
                raise SystemExit
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    snake.turn(UP)
                elif event.key == pygame.K_DOWN:
                    snake.turn(DOWN)
                elif event.key == pygame.K_LEFT:
                    snake.turn(LEFT)
                elif event.key == pygame.K_RIGHT:
                    snake.turn(RIGHT)
                elif event.key == pygame.K_r and game_over:
                    snake = Snake()
                    food = spawn_food(snake.body)
                    score = 0
                    game_over = False
                    logger.info("Game reset")

        # Update
        if not game_over:
            next_head = snake.step()
            # Wall collision
            if next_head[0] < 0 or next_head[0] >= GRID_W or next_head[1] < 0 or next_head[1] >= GRID_H:
                logger.info("Game over: wall collision")
                game_over = True
            # Self collision
            elif next_head in snake.body:
                logger.info("Game over: self collision")
                game_over = True
            else:
                grow = next_head == food
                snake.move(grow=grow)
                if grow:
                    score += 1
                    logger.info(f"Food eaten | score={score}")
                    food = spawn_food(snake.body)

        # Render
        screen.fill(BG)
        draw_grid(screen)
        draw_cell(screen, food, FOOD)
        for i, seg in enumerate(snake.body):
            draw_cell(screen, seg, HEAD if i == len(snake.body) - 1 else BODY)
        pygame.draw.rect(screen, INFO_BG, pygame.Rect(0, GRID_H * CELL, WIN_W, INFO_H))
        info = f"Score: {score}  | Arrows=Move  R=Restart"
        if game_over:
            info = f"GAME OVER | Score: {score} | Press R to Restart"
        screen.blit(font.render(info, True, TEXT), (10, GRID_H * CELL + 10))

        pygame.display.flip()
        clock.tick(FPS)

except SystemExit:
    # Normal exit path
    pass
except Exception:
    logger.exception("Fatal error in main loop")
finally:
    logger.info("Shutting down")
    try:
        pygame.quit()
    except Exception:
        pass
