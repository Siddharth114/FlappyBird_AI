import json
from train import train, make_net, greedy
from flappy_env import FlappyEnv


def test_train_smoke_writes_checkpoints_and_metrics(tmp_path):
    train(total_steps=3000, out=tmp_path, checkpoint_steps=[0, 2000])
    for name in ["ckpt-000000.pt", "ckpt-002000.pt", "ckpt-003000.pt", "ckpt-best.pt"]:
        assert (tmp_path / name).exists(), name
    m = json.loads((tmp_path / "metrics.json").read_text())
    assert [e["steps"] for e in m["evals"]] == [0, 2000, 3000]
    assert len(m["games"]) > 0 and m["best"]["mean"] == max(e["mean"] for e in m["evals"])


def test_greedy_returns_bool():
    assert isinstance(greedy(make_net())(FlappyEnv(0)), bool)
