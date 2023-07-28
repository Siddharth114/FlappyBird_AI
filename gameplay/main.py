import pygame
from pygame.locals import *
import random
import sys
import math

FPS = 32
SCREEN_WIDTH = 336
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
GROUND_Y = SCREEN_HEIGHT
PIPE_WIDTH = 20
PIPE_HEIGHT = 500
PLAYER_RADIUS = 10


def startScreen():
    player_x = int(SCREEN_WIDTH / 5)
    player_y = int(SCREEN_HEIGHT - PLAYER_RADIUS) / 2
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_SPACE:
                return
            else:
                SCREEN.fill([0, 0, 0])
                pygame.draw.circle(
                    SCREEN, (255, 255, 255), (player_x, player_y), PLAYER_RADIUS
                )
                pygame.display.update()
                FPSCLOCK.tick(FPS)


def mainGame():
    score = 0
    player_x = int(SCREEN_WIDTH / 5)
    player_y = int(SCREEN_HEIGHT / 2)

    new_pipe_1 = getRandomPipe()
    new_pipe_2 = getRandomPipe()

    upper_pipes = [
        {"x": SCREEN_WIDTH + 200, "y": new_pipe_1[0]["y"]},
        {"x": SCREEN_WIDTH + 200 + int(SCREEN_WIDTH * 0.5), "y": new_pipe_2[0]["y"]},
    ]
    lower_pipes = [
        {"x": SCREEN_WIDTH + 200, "y": new_pipe_1[1]["y"]},
        {"x": SCREEN_WIDTH + 200 + int(SCREEN_WIDTH * 0.5), "y": new_pipe_2[1]["y"]},
    ]

    pipe_velocity_x = -4

    player_velocity_y = -9
    player_max_velocity_y = 10
    player_min_velocity_y = 8
    player_accelaration_y = 1
    player_flap_velocity = -8
    player_flapped = False

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_SPACE:
                if player_y > 0:
                    player_velocity_y = player_flap_velocity
                    player_flapped = True

        crash_test = isCollide(player_x, player_y, upper_pipes, lower_pipes)
        if crash_test:
            return

        player_mid_pos = player_x + 5
        for pipe in upper_pipes:
            pipe_mid_pos = pipe["x"] + PIPE_WIDTH / 2
            if pipe_mid_pos <= player_mid_pos < pipe_mid_pos + 4:
                score += 1

        if player_velocity_y < player_max_velocity_y and not player_flapped:
            player_velocity_y += player_accelaration_y

        if player_flapped:
            player_flapped = False

        player_height = 5

        player_y += min(player_velocity_y, GROUND_Y - player_y - player_height)

        for upper_pipe, lower_pipe in zip(upper_pipes, lower_pipes):
            upper_pipe["x"] += pipe_velocity_x
            lower_pipe["x"] += pipe_velocity_x

        if 0 < upper_pipes[0]["x"] < 5:
            new_pipe = getRandomPipe()
            upper_pipes.append(new_pipe[0])
            lower_pipes.append(new_pipe[1])

        if upper_pipes[0]["x"] < -PIPE_WIDTH:
            upper_pipes.pop(0)
            lower_pipes.pop(0)

        SCREEN.fill([0, 0, 0])
        for upper_pipe, lower_pipe in zip(upper_pipes, lower_pipes):
            pygame.draw.rect(
                SCREEN,
                (255, 255, 255),
                pygame.Rect(upper_pipe["x"], upper_pipe["y"], PIPE_WIDTH, PIPE_HEIGHT),
            )
            pygame.draw.rect(
                SCREEN,
                (255, 255, 255),
                pygame.Rect(lower_pipe["x"], lower_pipe["y"], PIPE_WIDTH, PIPE_HEIGHT),
            )
        pygame.draw.circle(SCREEN, (255, 255, 255), (player_x, player_y), 10)
        score_text = my_font.render(str(score), False, (255, 255, 255))
        SCREEN.blit(score_text, (SCREEN_WIDTH / 2, 20))

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def isCollide(player_x, player_y, upper_pipes, lower_pipes):
    if player_y >= GROUND_Y - PLAYER_RADIUS or player_y - PLAYER_RADIUS <= 0:
        return True

    for pipe in upper_pipes:
        bottom_y = pipe['y'] + PIPE_HEIGHT
        left_x = pipe['x']
        right_x = left_x + PIPE_WIDTH

        closest_x = max(pipe['x'], min(player_x, pipe['x'] + PIPE_WIDTH))
        closest_y = max(pipe['y'], min(player_y, pipe['y'] + PIPE_HEIGHT))

        distance = math.sqrt((player_x - closest_x) ** 2 + (player_y - closest_y) ** 2)

        if distance <= PLAYER_RADIUS:
            return True

    for pipe in lower_pipes:
        bottom_y = pipe['y'] + PIPE_HEIGHT
        left_x = pipe['x']
        right_x = left_x + PIPE_WIDTH

        closest_x = max(pipe['x'], min(player_x, pipe['x'] + PIPE_WIDTH))
        closest_y = max(pipe['y'], min(player_y, pipe['y'] + PIPE_HEIGHT))

        distance = math.sqrt((player_x - closest_x) ** 2 + (player_y - closest_y) ** 2)

        if distance <= PLAYER_RADIUS:
            return True

    return False


def getRandomPipe():
    gap = 150
    pipe_x = SCREEN_WIDTH + 10
    lower_pipe_y = random.randrange(gap + 50, SCREEN_HEIGHT - 50)
    upper_pipe_y = lower_pipe_y - gap - PIPE_HEIGHT
    return [{"x": pipe_x, "y": upper_pipe_y}, {"x": pipe_x, "y": lower_pipe_y}]


if __name__ == "__main__":
    pygame.init()
    pygame.font.init()
    my_font = pygame.font.SysFont("Comic Sans MS", 30)
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption("Flappy Bird Clone")

    while True:
        startScreen()
        mainGame()
