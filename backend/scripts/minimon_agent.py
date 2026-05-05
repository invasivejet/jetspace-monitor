import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dynamics import PhysicsModel
from primitive import primitive_state


def main() -> None:
    model = PhysicsModel()
    out_dir = Path(__file__).resolve().parents[1] / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    stream_file = out_dir / "minimon-stream.jsonl"

    while True:
        physics = model.capture()
        primitive = primitive_state()
        record = {
            "ts": time.time(),
            "physics": physics,
            "primitive": primitive,
        }
        with stream_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, separators=(",", ":")) + "\n")

        # Keep CPU footprint low for always-on mode.
        time.sleep(5)


if __name__ == "__main__":
    main()
