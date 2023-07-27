import pygame
from pygame.locals import *
import random
import sys

FPS = 32
SCREEN_WIDTH = 289
SCREEN_HEIGHT = 511
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
GROUND_Y = SCREEN_HEIGHT
PIPE_WIDTH = 20
PIPE_HEIGHT = 500


def startScreen():
    player_x = int(SCREEN_WIDTH / 5)
    player_y = int(SCREEN_HEIGHT - 10)/2
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_SPACE:
                return
            else:
                SCREEN.fill([0,0,0])
                pygame.draw.circle(SCREEN, (255, 255, 255), (player_x, player_y), 10)
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
        {"x": SCREEN_WIDTH + 200 + (SCREEN_WIDTH / 2), "y": new_pipe_2[0]["y"]},
    ]
    lower_pipes = [
        {"x": SCREEN_WIDTH + 200, "y": new_pipe_1[1]["y"]},
        {"x": SCREEN_WIDTH + 200 + (SCREEN_WIDTH / 2), "y": new_pipe_2[1]["y"]},
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

        player_mid_pos = player_x + 5    #GAME_SPRITES["player"].get_width() / 2
        for pipe in upper_pipes:
            pipe_mid_pos = pipe['x'] + PIPE_WIDTH/2
            if pipe_mid_pos<=player_mid_pos<pipe_mid_pos+4:
                score+=1

        if player_velocity_y < player_max_velocity_y and not player_flapped:
            player_velocity_y += player_accelaration_y
        
        if player_flapped:
            player_flapped=False

        player_height = 5   #GAME_SPRITES['player'].get_height()

        player_y += min(player_velocity_y, GROUND_Y - player_y - player_height)

        for upper_pipe, lower_pipe in zip(upper_pipes, lower_pipes):
            upper_pipe['x'] += pipe_velocity_x
            lower_pipe['x'] += pipe_velocity_x

        if 0<upper_pipes[0]['x']<5:
            new_pipe = getRandomPipe()
            upper_pipes.append(new_pipe[0])
            lower_pipes.append(new_pipe[1])

        if upper_pipes[0]['x'] < -PIPE_WIDTH:
            upper_pipes.pop(0)
            lower_pipes.pop(0)

        SCREEN.fill([0,0,0])
        for upper_pipe, lower_pipe in zip(upper_pipes, lower_pipes):
            pygame.draw.rect(SCREEN, (255,255,255), pygame.Rect(upper_pipe['x'], upper_pipe['y'], PIPE_WIDTH, PIPE_HEIGHT))
            pygame.draw.rect(SCREEN, (255,255,255), pygame.Rect(lower_pipe['x'], lower_pipe['y'], PIPE_WIDTH, PIPE_HEIGHT))
            # SCREEN.blit(GAME_SPRITES['pipe'][0], (upper_pipe['x'], upper_pipe['y']))
            # SCREEN.blit(GAME_SPRITES['pipe'][1], (lower_pipe['x'], lower_pipe['y']))
        pygame.draw.circle(SCREEN, (255, 255, 255), (player_x, player_y), 10)
        # SCREEN.blit(GAME_SPRITES['player'], (player_x, player_y))
        score_text = my_font.render(str(score), False, (255, 255, 255))
        SCREEN.blit(score_text, (SCREEN_WIDTH/2, 20))

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def isCollide(player_x, player_y, upper_pipes, lower_pipes):
    return False



def getRandomPipe():
    pipe_height = PIPE_HEIGHT
    offset = SCREEN_HEIGHT / 3
    y2 = offset + random.randrange(0, SCREEN_HEIGHT)
    pipe_x = SCREEN_WIDTH + 10
    y1 = pipe_height - y2 + offset
    return [{"x": pipe_x, "y": -y1}, {"x": pipe_x, "y": y2}]


if __name__ == "__main__":
    pygame.init()
    pygame.font.init()
    my_font = pygame.font.SysFont('Comic Sans MS', 30)
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption("Flappy Bird Clone")

    while True:
        startScreen()
        mainGame()
