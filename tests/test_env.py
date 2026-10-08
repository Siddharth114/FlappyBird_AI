import pytest
from flappy_env import (FlappyEnv, Mulberry32, heuristic, evaluate,
                        H, R, W, SPACING)


def test_rng_matches_js_reference():
    # Same three values Node prints for mulberry32(42) — parity with lib/flappy/env.ts.
    r = Mulberry32(42)
    assert [r.next() for _ in range(3)] == [
        0.6011037519201636, 0.44829055899754167, 0.8524657934904099]


def test_reset_is_deterministic_per_seed():
    a, b, c = FlappyEnv(7), FlappyEnv(7), FlappyEnv(8)
    assert a.pipes == b.pipes and a.pipes != c.pipes
    assert [p["bottom"] for p in a.pipes] == [204, 221, 541]


def test_never_flapping_hits_the_floor():
    env = FlappyEnv(0)
    rewards = []
    while not env.done:
        rewards.append(env.step(False))
    assert env.frame == 47 and env.y + R >= H and rewards[-1] == -1.0


def test_always_flapping_hits_the_ceiling():
    env = FlappyEnv(0)
    while not env.done:
        env.step(True)
    assert env.frame == 37 and env.y - R <= 0


def test_heuristic_scores_and_pipe_bonus_paid_once_per_pipe():
    env = FlappyEnv(1)
    rewards = []
    while not env.done:
        rewards.append(env.step(heuristic(env)))
    assert env.score == 64 and env.frame == 2662
    assert sum(1 for r in rewards if r > 1.0) == env.score


def test_pipes_stay_evenly_spaced_and_stocked():
    env = FlappyEnv(1)
    while not env.done:
        env.step(heuristic(env))
        xs = [p["x"] for p in env.pipes]
        assert all(b - a == SPACING for a, b in zip(xs, xs[1:]))
        assert xs[-1] >= W + SPACING and len(xs) <= 6


def test_step_after_done_raises():
    env = FlappyEnv(0)
    while not env.done:
        env.step(False)
    with pytest.raises(AssertionError):
        env.step(False)


def test_evaluate_respects_cap_and_seeds():
    assert evaluate(lambda e: False, seeds=range(3)) == [0, 0, 0]
    assert evaluate(heuristic, seeds=[1], cap=5) == [5]


def test_observe_includes_the_gap_after_next():
    # seed 7: pipes at x=600 (gap 54..204) and x=800 (gap 71..221); bird y=300, vy=-9
    assert FlappyEnv(7).observe() == pytest.approx(
        [-246 / 600, -96 / 600, 520 / 400, -0.9, 0.5, -229 / 600, -79 / 600])
