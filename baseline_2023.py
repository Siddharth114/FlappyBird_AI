"""The 2023 recipe, re-run verbatim on the new env — the honest 'before' line.

Hyperparameters, network and QTrainer come straight from legacy/ (agent.py,
model.py). Its known bugs are kept on purpose; this measures them.
"""
import argparse
import json
import random
from collections import deque
from pathlib import Path

import torch

from flappy_env import CAP, H, PLAYER_X, TEST_SEEDS, FlappyEnv, evaluate
from legacy.model import Linear_QNet, QTrainer

LR, GAMMA, HIDDEN, BATCH, MAX_MEMORY = 0.05, 0.9, 256, 1000, 100_000


def raw_state(env: FlappyEnv) -> list[float]:
    p = env.next_pipe()  # 2023 state: raw pixels, unscaled
    return [env.y, p["top"], p["bottom"], p["x"] - PLAYER_X, env.vy]


def override(env: FlappyEnv, flap: bool) -> bool:
    """2023 'safety' rule. The executed action can differ from the recorded one — a bug."""
    if env.y >= 0.8 * H:
        return True
    if env.y <= 0.2 * H:
        return False
    return flap


def run(games: int, out: Path, seed: int = 0) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    random.seed(seed)
    torch.manual_seed(seed)
    net = Linear_QNet(5, HIDDEN, 2)
    trainer = QTrainer(net, lr=LR, gamma=GAMMA)
    memory = deque(maxlen=MAX_MEMORY)
    scores = []

    def act(state):
        with torch.no_grad():
            return int(torch.argmax(net(torch.tensor(state, dtype=torch.float))).item())

    for n in range(games):
        env = FlappyEnv(100_000 + n)
        while not env.done and env.score < CAP:
            s = raw_state(env)
            move = random.randint(0, 1) if random.randint(0, 200) < 80 - n else act(s)
            prev = env.score
            env.step(override(env, move == 1))
            r = -1000.0 if env.done else 10.0 * (env.score - prev)
            s2 = raw_state(env)
            one_hot = [0, 0]
            one_hot[move] = 1  # records the CHOSEN move, not the executed one
            trainer.train_step(s, one_hot, r, s2, env.done)
            memory.append((s, one_hot, r, s2, env.done))
        for t in random.sample(memory, min(len(memory), BATCH)):  # one sample at a time, as in 2023
            trainer.train_step(*t)
        scores.append([n, env.score])
        print(f"game {n:>4}  score {env.score}", flush=True)

    policy = lambda e: override(e, act(raw_state(e)) == 1)  # evaluated as deployed, override on
    ev, te = evaluate(policy), evaluate(policy, seeds=TEST_SEEDS)
    best = {"steps": 0, "games": games, "mean": sum(ev) / len(ev), "max": max(ev)}
    metrics = {"games": scores, "evals": [best], "best": best,
               "test": {"mean": sum(te) / len(te), "max": max(te)}}
    (out / "metrics.json").write_text(json.dumps(metrics))
    return metrics


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=500)
    ap.add_argument("--out", type=Path, default=Path("runs/legacy"))
    args = ap.parse_args()
    run(args.games, args.out)
