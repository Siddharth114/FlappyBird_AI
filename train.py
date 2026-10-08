"""Double DQN on the headless env. Writes checkpoints + metrics.json to --out."""
import argparse
import copy
import json
import random
from collections import deque
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F

from flappy_env import CAP, FlappyEnv, evaluate

# Eval + checkpoint every 25k: DQN here peaks and collapses between evals, sparse marks miss the peak.
CHECKPOINT_STEPS = [0, 10_000] + list(range(25_000, 1_000_001, 25_000))
GAMMA, BATCH, BUFFER, WARMUP = 0.99, 64, 100_000, 1000
EPS_END, EPS_STEPS, EXPLORE_FLAP_P = 0.01, 100_000, 0.1
LR, TARGET_SYNC = 5e-4, 1000  # planning sweep: beat soft updates (tau .005) and LR decay


def make_net() -> nn.Sequential:
    return nn.Sequential(nn.Linear(7, 64), nn.ReLU(), nn.Linear(64, 64), nn.ReLU(), nn.Linear(64, 2))


def greedy(net):
    def policy(env: FlappyEnv) -> bool:
        with torch.no_grad():
            return bool(net(torch.tensor(env.observe())).argmax())  # tie -> 0 (no flap), same as JS
    return policy


def train(total_steps: int, out: Path, checkpoint_steps=CHECKPOINT_STEPS, seed: int = 0) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    random.seed(seed)
    torch.manual_seed(seed)
    net = make_net()
    target = copy.deepcopy(net)
    opt = torch.optim.Adam(net.parameters(), lr=LR)
    buffer = deque(maxlen=BUFFER)
    metrics = {"config": {"gamma": GAMMA, "lr": LR, "target_sync": TARGET_SYNC, "batch": BATCH, "hidden": 64,
                          "eps_steps": EPS_STEPS, "cap": CAP},
               "games": [], "evals": [], "best": None}
    games = 0
    env = FlappyEnv(100_000)
    obs = env.observe()
    marks = {s for s in checkpoint_steps if s <= total_steps} | {total_steps}

    def checkpoint(step: int):
        scores = evaluate(greedy(net))
        ev = {"steps": step, "games": games, "mean": sum(scores) / len(scores), "max": max(scores)}
        metrics["evals"].append(ev)
        payload = {"state_dict": copy.deepcopy(net.state_dict()), "steps": step, "games": games,
                   "eval_mean": ev["mean"], "eval_max": ev["max"]}
        torch.save(payload, out / f"ckpt-{step:06d}.pt")
        if metrics["best"] is None or ev["mean"] > metrics["best"]["mean"]:
            metrics["best"] = ev
            torch.save(payload, out / "ckpt-best.pt")
        print(f"step {step:>7}  games {games:>5}  eval mean {ev['mean']:.1f}  max {ev['max']}", flush=True)

    for step in range(total_steps + 1):
        if step in marks:
            checkpoint(step)
        if step == total_steps:
            break
        eps = max(EPS_END, 1 - step / EPS_STEPS)
        if random.random() < eps:
            action = 1 if random.random() < EXPLORE_FLAP_P else 0
        else:
            with torch.no_grad():
                action = int(net(torch.tensor(obs)).argmax())
        reward = env.step(bool(action))
        next_obs = env.observe()
        buffer.append((obs, action, reward, next_obs, float(env.done)))
        obs = next_obs
        if env.done or env.score >= CAP:  # truncation at CAP is stored as non-terminal
            metrics["games"].append([step, env.score])
            games += 1
            obs = env.reset(100_000 + games)

        if len(buffer) >= WARMUP:
            s, a, r, s2, d = zip(*random.sample(buffer, BATCH))
            s, s2 = torch.tensor(s), torch.tensor(s2)
            a, r, d = torch.tensor(a), torch.tensor(r), torch.tensor(d)
            q = net(s).gather(1, a[:, None]).squeeze(1)
            with torch.no_grad():  # Double DQN: online net picks, target net scores
                best = net(s2).argmax(1, keepdim=True)
                y = r + GAMMA * (1 - d) * target(s2).gather(1, best).squeeze(1)
            loss = F.smooth_l1_loss(q, y)
            opt.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(net.parameters(), 10)
            opt.step()
        if step % TARGET_SYNC == 0:
            target.load_state_dict(net.state_dict())

    (out / "metrics.json").write_text(json.dumps(metrics))
    return metrics


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=300_000)
    ap.add_argument("--out", type=Path, default=Path("runs/dqn"))
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    train(args.steps, args.out, seed=args.seed)
