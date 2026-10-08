"""Export trained runs to the portfolio: weights, chart data, summary, golden fixtures."""
import argparse
import base64
import json
import struct
from pathlib import Path

import torch

from flappy_env import CAP, TEST_SEEDS, FlappyEnv, evaluate, heuristic
from train import greedy, make_net


def b64f32(t: torch.Tensor) -> str:
    vals = t.detach().flatten().tolist()
    return base64.b64encode(struct.pack(f"<{len(vals)}f", *vals)).decode()


def layers_of(state_dict) -> list[dict]:
    out = []
    for i in (0, 2, 4):
        w, b = state_dict[f"{i}.weight"], state_dict[f"{i}.bias"]
        out.append({"in": w.shape[1], "out": w.shape[0], "w": b64f32(w), "b": b64f32(b)})
    return out


def rolling(games: list[list[int]], window: int = 20, points: int = 200) -> list[list[float]]:
    scores = [s for _, s in games]
    means, acc = [], 0.0
    for i, s in enumerate(scores):
        acc += s
        if i >= window:
            acc -= scores[i - window]
        means.append(acc / min(i + 1, window))
    stride = max(1, -(-len(means) // points))  # ceil
    idx = list(range(len(means) - 1, -1, -stride))[::-1]  # always keep the last point
    return [[i, round(means[i], 3)] for i in idx]


def golden_env() -> dict:
    env = FlappyEnv(7)
    frames = []
    while not env.done and env.frame < 400:
        flap = heuristic(env)
        env.step(flap)
        frames.append({"flap": flap, "y": env.y, "vy": env.vy, "score": env.score,
                       "done": env.done, "obs": env.observe()})
    return {"seed": 7, "frames": frames}


def golden_policy(net, file: str) -> dict:
    env, inputs = FlappyEnv(3), []
    while not env.done and env.frame < 64:
        if env.frame % 4 == 0:
            inputs.append(env.observe())
        env.step(heuristic(env))
    with torch.no_grad():
        outputs = net(torch.tensor(inputs)).tolist()
    rollout = evaluate(greedy(net), seeds=[1000])[0]
    return {"file": file, "inputs": inputs, "outputs": outputs, "rollout": {"seed": 1000, "score": rollout}}


def readme_chart(before, ckpts, heuristic_mean, path: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 3.6), dpi=150)
    ax.plot(*zip(*before), color="#64748b", label="2023 recipe (rolling mean of training games)")
    ax.plot(*zip(*[(c["games"], c["evalMean"]) for c in ckpts]), color="#d97706", marker="o",
            label="2026 rework (greedy, validation layouts)")
    ax.axhline(heuristic_mean, color="#94a3b8", ls="--", lw=1, label="hand-written rule (held-out layouts)")
    ax.set_xlabel("games played")
    ax.set_ylabel(f"pipes passed (cap {CAP})")
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)


def main(portfolio: Path, runs: Path):
    dqn = json.loads((runs / "dqn/metrics.json").read_text())
    legacy = json.loads((runs / "legacy/metrics.json").read_text())
    pub = portfolio / "public/lab/flappy"
    lib = portfolio / "lib/flappy"
    for d in (pub, lib / "fixtures"):
        d.mkdir(parents=True, exist_ok=True)

    # Milestones up to (and including) the best checkpoint; the best one closes the scrubber.
    best = dqn["best"]
    ckpts = []
    for ev in dqn["evals"]:
        if ev["steps"] > best["steps"]:
            break
        ck = torch.load(runs / f"dqn/ckpt-{ev['steps']:06d}.pt")
        name = f"ckpt-{ev['steps']:06d}.json"
        (pub / name).write_text(json.dumps({"steps": ck["steps"], "games": ck["games"],
                                            "evalMean": ck["eval_mean"],
                                            "layers": layers_of(ck["state_dict"])}))
        ckpts.append({"file": name, "steps": ck["steps"], "games": ck["games"], "evalMean": ck["eval_mean"]})

    mean = lambda xs: sum(xs) / len(xs)
    heur = evaluate(heuristic, seeds=TEST_SEEDS)
    heuristic_mean = mean(heur)
    best_games = [g for g in dqn["games"] if g[0] <= best["steps"]]
    before = rolling([[i, s] for i, s in legacy["games"]])
    after = rolling([[i, s] for i, (_, s) in enumerate(best_games)])
    (lib / "lab.json").write_text(json.dumps({"cap": CAP, "heuristicMean": heuristic_mean,
                                              "series": {"before": before, "after": after},
                                              "checkpoints": ckpts}))
    net = make_net()
    net.load_state_dict(torch.load(runs / f"dqn/ckpt-{best['steps']:06d}.pt")["state_dict"])
    after_test = evaluate(greedy(net), seeds=TEST_SEEDS)  # held out: selection used EVAL_SEEDS
    summary = {"cap": CAP, "testSeeds": len(TEST_SEEDS),
               "before": {"mean": legacy["test"]["mean"], "max": legacy["test"]["max"],
                          "games": legacy["best"]["games"]},
               "after": {"mean": mean(after_test), "max": max(after_test),
                         "games": best["games"], "steps": best["steps"]},
               "heuristic": {"mean": heuristic_mean, "max": max(heur)}}
    (lib / "summary.json").write_text(json.dumps(summary, indent=2))
    (lib / "fixtures/golden-env.json").write_text(json.dumps(golden_env()))
    (lib / "fixtures/golden-policy.json").write_text(json.dumps(golden_policy(net, ckpts[-1]["file"])))
    readme_chart(before, ckpts, heuristic_mean, Path("training_results/2026-rework.png"))

    b, a, h = summary["before"], summary["after"], summary["heuristic"]
    print("| | Mean pipes | Best | Training games |\n|---|---|---|---|")
    f = lambda v: f"{v:.2f}" if v < 1 else f"{v:.1f}"  # same rule as the site
    print(f"| 2023 recipe (re-run) | {f(b['mean'])} | {b['max']} | {b['games']} |")
    print(f"| Hand-written rule | {f(h['mean'])} | {h['max']} | — |")
    print(f"| 2026 rework | {f(a['mean'])} | {a['max']} | {a['games']:,} |")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--portfolio", type=Path, default=Path.home() / "code/portfolio")
    ap.add_argument("--runs", type=Path, default=Path("runs"))
    args = ap.parse_args()
    main(args.portfolio, args.runs)
