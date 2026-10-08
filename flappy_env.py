"""Headless Flappy Bird — integer physics, seeded, no pygame.

Single source of truth for the game rules. The portfolio's lib/flappy/env.ts
mirrors this file line for line; export_web.py writes golden fixtures that
pin the two together. Change one, change both, re-export.
Physics constants match the 2023 ai_game.py; update order and pipe spawning
were simplified (legacy/ai_game.py has the original).
"""
from typing import Callable

W, H = 400, 600
PLAYER_X, R = 80, 10
PIPE_W, GAP, SPACING = 20, 150, 200
PIPE_VX = -5
GRAVITY, MAX_VY, FLAP_VY = 1, 10, -8
START_Y, START_VY = 300, -9
FIRST_PIPE_X = W + 200

CAP = 200
EVAL_SEEDS = range(1000, 1020)  # validation: checkpoint selection
TEST_SEEDS = range(2000, 2100)  # held out: the only numbers that get reported

M32 = 0xFFFFFFFF


class Mulberry32:
    """mulberry32 PRNG — bit-identical to the JS version in lib/flappy/env.ts."""

    def __init__(self, seed: int):
        self.a = seed & M32

    def next(self) -> float:
        self.a = (self.a + 0x6D2B79F5) & M32
        t = self.a
        t = ((t ^ (t >> 15)) * (t | 1)) & M32
        t = ((t + (((t ^ (t >> 7)) * (t | 61)) & M32)) & M32) ^ t
        return ((t ^ (t >> 14)) & M32) / 4294967296


class FlappyEnv:
    def __init__(self, seed: int = 0):
        self.reset(seed)

    def reset(self, seed: int) -> list[float]:
        self.rng = Mulberry32(seed)
        self.y, self.vy = START_Y, START_VY
        self.score = 0
        self.frame = 0
        self.done = False
        self.pipes: list[dict] = []
        for i in range(3):
            self._spawn(FIRST_PIPE_X + i * SPACING)
        return self.observe()

    def _spawn(self, x: int) -> None:
        bottom = 200 + int(self.rng.next() * 350)  # gap bottom in [200, 550), as in 2023
        self.pipes.append({"x": x, "top": bottom - GAP, "bottom": bottom, "passed": False})

    def step(self, flap: bool) -> float:
        assert not self.done, "step() after done; call reset()"
        self.vy = FLAP_VY if flap else min(self.vy + GRAVITY, MAX_VY)
        self.y += self.vy
        for p in self.pipes:
            p["x"] += PIPE_VX
        if self.pipes[0]["x"] < -PIPE_W:
            self.pipes.pop(0)
        if self.pipes[-1]["x"] < W + SPACING:
            self._spawn(self.pipes[-1]["x"] + SPACING)
        self.frame += 1
        if self._crashed():
            self.done = True
            return -1.0
        reward = 0.1
        for p in self.pipes:
            if not p["passed"] and p["x"] + PIPE_W < PLAYER_X:
                p["passed"] = True
                self.score += 1
                reward += 1.0
        return reward

    def _crashed(self) -> bool:
        if self.y - R <= 0 or self.y + R >= H:
            return True
        for p in self.pipes:
            dx = PLAYER_X - max(p["x"], min(PLAYER_X, p["x"] + PIPE_W))
            # Upper pipe spans y <= top, lower pipe y >= bottom; squared distance keeps it integer.
            for cy in (min(self.y, p["top"]), max(self.y, p["bottom"])):
                dy = self.y - cy
                if dx * dx + dy * dy <= R * R:
                    return True
        return False

    def _next_index(self) -> int:
        return next(i for i, p in enumerate(self.pipes) if p["x"] + PIPE_W >= PLAYER_X - R)

    def next_pipe(self) -> dict:
        return self.pipes[self._next_index()]

    def observe(self) -> list[float]:
        """7 features, roughly in [-1, 1], relative to the bird.

        Includes the gap AFTER next: consecutive gaps can differ by 350px with only
        40 frames between them, so the agent has to start moving before it clears
        the current pipe. Without it, every planning-time run plateaued at ~80.
        """
        i = self._next_index()
        p, q = self.pipes[i], self.pipes[i + 1]
        return [
            (p["top"] - self.y) / H,
            (p["bottom"] - self.y) / H,
            (p["x"] - PLAYER_X) / W,
            self.vy / MAX_VY,
            self.y / H,
            (q["top"] - self.y) / H,
            (q["bottom"] - self.y) / H,
        ]


def heuristic(env: FlappyEnv) -> bool:
    """Hand-written baseline: flap when you drop near the bottom of the gap."""
    return env.y > env.next_pipe()["bottom"] - 40


def evaluate(policy: Callable[[FlappyEnv], bool], seeds=EVAL_SEEDS, cap: int = CAP) -> list[int]:
    scores = []
    for s in seeds:
        env = FlappyEnv(s)
        while not env.done and env.score < cap:
            env.step(policy(env))
        scores.append(env.score)
    return scores
