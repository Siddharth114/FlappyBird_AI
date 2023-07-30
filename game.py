import pygame
from pygame.locals import *
import random
import sys
import math

pygame.init()
pygame.font.init()
font = pygame.font.SysFont("Arial", 30)

FPS = 32
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
PIPE_WIDTH = 20
PIPE_HEIGHT = 500
PLAYER_RADIUS = 10
BLACK_COLOR = [0, 0, 0]
RED_COLOR = [255, 0, 0]
GREEN_COLOR = [0, 255, 0]
WHITE_COLOR = [255, 255, 255]

DEATH_REWARD = -10
PIPE_PASSING_REWARD = 10


class FlappyBird:
    def __init__(self):
        self.w = SCREEN_WIDTH
        self.h = SCREEN_HEIGHT
        self.player_r = PLAYER_RADIUS
        self.pipe_h = PIPE_HEIGHT
        self.pipe_w = PIPE_WIDTH
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption("Flappy Bird Clone")
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.player_x = int(self.w / 5)
        self.player_y = int(self.h - self.player_r) / 2
        while True:
            for event in pygame.event.get():
                if event.type == QUIT or (
                    event.type == KEYDOWN and event.key == K_ESCAPE
                ):
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN and event.key == K_SPACE:
                    self.main_game()
                else:
                    self.display.fill(BLACK_COLOR)
                    pygame.draw.circle(
                        self.display,
                        WHITE_COLOR,
                        (self.player_x, self.player_y),
                        self.player_r,
                    )
                    pygame.display.update()
                    self.clock.tick(FPS)

    def play_step(self, event):
        return event.type == KEYDOWN and event.key == K_SPACE

    def main_game(self):
        self.score = 0
        self.player_x = int(self.w / 5)
        self.player_y = int(self.h / 2)

        self.new_pipe_1 = self.get_pipe()
        self.new_pipe_2 = self.get_pipe()

        self.pipe_velocity_x = -5
        self.player_velocity_y = -9
        self.player_max_velocity_y = 10
        self.player_accelaration_y = 1
        self.player_flap_velocity = -8
        self.player_flapped = False

        self.game_over = False

        self.upper_pipes = [{"x": self.w + 200, "y": self.new_pipe_1[0]["y"]}]

        self.lower_pipes = [{"x": self.w + 200, "y": self.new_pipe_1[1]["y"]}]

        self.upper_pipes.append(
            {"x": self.upper_pipes[-1]["x"] + 200, "y": self.new_pipe_2[0]["y"]}
        )

        self.lower_pipes.append(
            {"x": self.lower_pipes[-1]["x"] + 200, "y": self.new_pipe_2[1]["y"]}
        )

        while True:
            for event in pygame.event.get():
                if event.type == QUIT or (
                    event.type == KEYDOWN and event.key == K_ESCAPE
                ):
                    pygame.quit()
                    sys.exit()
                self.is_space = self.play_step(event)
                if self.is_space:
                    if self.player_y > 0:
                        self.player_velocity_y = self.player_flap_velocity
                        self.player_flapped = True

            self.reward = 0
            self.game_over = self.collision(
                self.player_x, self.player_y, self.upper_pipes, self.lower_pipes
            )
            if self.game_over:
                self.reward += DEATH_REWARD
                self.death_screen()

            player_mid_pos = self.player_x + self.player_r // 2
            for pipe in self.upper_pipes:
                pipe_mid_pos = pipe["x"] + self.pipe_w / 2
                if pipe_mid_pos <= player_mid_pos < pipe_mid_pos + 4:
                    self.score += 1
                    self.reward += PIPE_PASSING_REWARD

            if (
                self.player_velocity_y < self.player_max_velocity_y
                and not self.player_flapped
            ):
                self.player_velocity_y += self.player_accelaration_y

            if self.player_flapped:
                self.player_flapped = False

            self.player_height = 5

            self.player_y += min(
                self.player_velocity_y, self.h - self.player_y - self.player_height
            )

            for upper_pipe, lower_pipe in zip(self.upper_pipes, self.lower_pipes):
                upper_pipe["x"] += self.pipe_velocity_x
                lower_pipe["x"] += self.pipe_velocity_x

            if 0 < self.upper_pipes[0]["x"] < self.w//8:
                new_pipe = self.get_pipe(upper_pipes=self.upper_pipes)
                self.upper_pipes.append(new_pipe[0])
                self.lower_pipes.append(new_pipe[1])

            if self.upper_pipes[0]["x"] < -self.pipe_w:
                self.upper_pipes.pop(0)
                self.lower_pipes.pop(0)

            self.display.fill(BLACK_COLOR)
            for upper_pipe, lower_pipe in zip(self.upper_pipes, self.lower_pipes):
                pygame.draw.rect(
                    self.display,
                    WHITE_COLOR,
                    pygame.Rect(
                        upper_pipe["x"], upper_pipe["y"], self.pipe_w, self.pipe_h
                    ),
                )

                pygame.draw.rect(
                    self.display,
                    WHITE_COLOR,
                    pygame.Rect(
                        lower_pipe["x"], lower_pipe["y"], self.pipe_w, self.pipe_h
                    ),
                )

            pygame.draw.circle(
                self.display,
                WHITE_COLOR,
                (self.player_x, self.player_y),
                self.player_r,
            )

            score_text = str(self.score)
            text_width, text_height = font.size(str(score_text))

            text_x = (self.w - text_width) // 2
            text_surface = font.render(score_text, True, GREEN_COLOR)
            self.display.blit(text_surface, (text_x, 20))
            pygame.display.update()
            self.clock.tick(FPS)

    def get_pipe(self, upper_pipes=None):
        gap = 150
        if upper_pipes == None:
            pipe_x = self.w + 10
        else:
            pipe_x = upper_pipes[-1]["x"] + 200
        lower_pipe_y = random.randrange(gap + 50, self.h - 50)
        upper_pipe_y = lower_pipe_y - gap - self.pipe_h
        return [{"x": pipe_x, "y": upper_pipe_y}, {"x": pipe_x, "y": lower_pipe_y}]

    def collision(self, player_x, player_y, upper_pipes, lower_pipes):
        if player_y >= self.h - self.player_r or player_y - self.player_r <= 0:
            return True

        for pipe in upper_pipes:
            closest_x = max(pipe["x"], min(player_x, pipe["x"] + self.pipe_w))
            closest_y = max(pipe["y"], min(player_y, pipe["y"] + self.pipe_h))

            distance = math.sqrt(
                (player_x - closest_x) ** 2 + (player_y - closest_y) ** 2
            )

            if distance <= self.player_r:
                return True

        for pipe in lower_pipes:
            closest_x = max(pipe["x"], min(player_x, pipe["x"] + self.pipe_w))
            closest_y = max(pipe["y"], min(player_y, pipe["y"] + self.pipe_h))

            distance = math.sqrt(
                (player_x - closest_x) ** 2 + (player_y - closest_y) ** 2
            )

            if distance <= self.player_r:
                return True

    def death_screen(self):
        while True:
            for event in pygame.event.get():
                if event.type == QUIT or (
                    event.type == KEYDOWN and event.key == K_ESCAPE
                ):
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN and event.key == K_SPACE:
                    self.reset()

            self.display.fill(BLACK_COLOR)
            text = f"Your Score is {self.score}"

            text_width, text_height = font.size(text)

            text_x = (self.w - text_width) // 2
            text_y = (self.h - text_height) // 2

            text_surface = font.render(text, True, RED_COLOR)
            self.display.blit(text_surface, (text_x, text_y))
            pygame.display.update()


bird = FlappyBird()
