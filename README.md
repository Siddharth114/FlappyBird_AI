# Flappy Bird AI — Deep Q-Learning, take two

A from-scratch Flappy Bird clone and an agent that learns to play it with deep Q-learning (PyTorch).
**Watch it learn, or race it, in your browser:** https://portfolio-ahl.pages.dev/college/game-ais

## The short version
In 2023 I built this, saw the occasional lucky pipe, and wrote that it had started to learn.
It hadn't — re-running that exact recipe on the same game (table below) shows it never got past luck.
In 2026 I came back, found out why, and fixed it. Both versions are in this repo; the comparison below is measured on the same game, from one training run of each.

![Training](training_results/2026-rework.png)

## Results
The hand-written rule flaps whenever the bird sinks within 40px of the bottom of the next gap.

| | Mean pipes | Best | Training games |
|---|---|---|---|
| 2023 recipe (re-run) | 0.15 | 2 | 500 |
| Hand-written rule | 69.5 | 200 | — |
| 2026 rework | 85.9 | 200 | 577 |

Evaluated greedily on 100 held-out pipe layouts (seeds 2000–2099), capped at 200 pipes. Checkpoints were
selected on a separate 20 (seeds 1000–1019), so selection doesn't flatter these numbers.

## What the agent sees
Seven numbers per frame, scaled to roughly −1…1: distance from the bird to the top and bottom of the
next gap and of the gap after it, horizontal distance to the next pipe, vertical speed, and height.
Two actions: flap or don't. Seeing the gap after next made the biggest difference in my experiments — consecutive gaps can be
350px apart with only 40 frames to get there.

## Why the 2023 version never learned
These are the bugs I found reading the code back; I didn't ablate them one at a time.

- **Raw pixel inputs** (values in the hundreds) with a learning rate of 0.05, which I think saturated the network —
  the stuck-on-one-action collapse I blamed on exploding gradients.
- **Rewards out of scale:** −1000 for dying, +10 for a pipe — and with γ = 0.9 a pipe 40 frames away
  is worth 0.9⁴⁰ ≈ 1.5% of its value. The agent could barely see the thing it was meant to want.
- **A safety override recorded the wrong action:** near the floor/ceiling the game took over,
  but replay memory stored the move the agent *chose*, not the one that happened.
- **Exploration switched off after 80 games.**
- **The TD target wasn't detached,** so each update also pushed the target around.
- **One-sample-at-a-time training** made every update noisy and slow.

## What changed in 2026
Normalised, bird-relative inputs that include the gap after next · rewards of +0.1/frame, +1/pipe,
−1/crash · γ = 0.99 · Double DQN with a target network · Huber loss + gradient clipping (the fix the 2023
README proposed) · mini-batches from a 100k replay buffer · no override — it keeps itself alive ·
keep the best checkpoint by validation score, because DQN on this task oscillates — most of the run's later checkpoints fell apart again.

## Run it
    uv run pytest                                  # tests
    uv run python train.py --steps 300000          # train (CPU, minutes)
    uv run python baseline_2023.py                 # re-run the 2023 recipe
    uv run python export_web.py                    # export to the portfolio
    uv run python human_game.py                    # play it yourself

## Repo layout
`flappy_env.py` headless game (source of truth; the browser port mirrors it) · `train.py` DQN ·
`baseline_2023.py` the old recipe · `export_web.py` portfolio export · `legacy/` the original 2023 code and charts.
