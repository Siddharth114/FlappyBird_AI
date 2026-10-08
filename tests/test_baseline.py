import json
from baseline_2023 import run, raw_state
from flappy_env import FlappyEnv


def test_raw_state_is_unscaled_pixels():
    env = FlappyEnv(7)
    assert raw_state(env) == [300, 54, 204, 520, -9]


def test_baseline_smoke(tmp_path):
    run(games=3, out=tmp_path)
    m = json.loads((tmp_path / "metrics.json").read_text())
    assert len(m["games"]) == 3 and m["best"]["mean"] >= 0 and m["test"]["mean"] >= 0
