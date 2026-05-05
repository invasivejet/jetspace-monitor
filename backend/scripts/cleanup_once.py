import argparse
import base64
import gzip
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cleanup import SafeCleaner
from dynamics import PhysicsModel


def main() -> None:
    parser = argparse.ArgumentParser(description="Safe one-shot cleanup runner")
    parser.add_argument("--apply", action="store_true", help="Perform deletion (default is dry-run)")
    args = parser.parse_args()

    cleaner = SafeCleaner()
    model = PhysicsModel()
    physics_snapshot = model.capture()
    result = cleaner.run(dry_run=not args.apply)
    result["physics_snapshot"] = physics_snapshot

    out_dir = Path(__file__).resolve().parents[1] / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "cleanup-last.json"
    out_file.write_text(json.dumps(result, indent=2), encoding="utf-8")
    encoded = base64.b64encode(gzip.compress(json.dumps(result).encode("utf-8"))).decode("ascii")
    (out_dir / "cleanup-last.autoencoded").write_text(encoded, encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
