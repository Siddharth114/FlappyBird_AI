import base64
import struct
from export_web import b64f32, layers_of, rolling, golden_env
from train import make_net


def test_b64f32_roundtrips_float32_row_major():
    net = make_net()
    w = net[0].weight
    raw = base64.b64decode(b64f32(w))
    vals = struct.unpack(f"<{w.numel()}f", raw)
    assert list(vals) == w.detach().flatten().tolist()


def test_layers_of_shapes():
    layers = layers_of(make_net().state_dict())
    assert [(l["in"], l["out"]) for l in layers] == [(7, 64), (64, 64), (64, 2)]


def test_rolling_mean_downsamples():
    pts = rolling([[i, i % 2] for i in range(1000)], window=20, points=100)
    assert len(pts) <= 100 and pts[-1][0] == 999 and abs(pts[-1][1] - 0.5) < 1e-9


def test_golden_env_is_400_frames_and_alive():
    g = golden_env()
    assert g["seed"] == 7 and len(g["frames"]) == 400
    assert g["frames"][-1]["done"] is False and g["frames"][-1]["score"] == 8
