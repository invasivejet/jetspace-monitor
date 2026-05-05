import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cleanup import SafeCleaner
from dynamics import PhysicsModel


def choose_mode(pressure: float, requested_apply: bool) -> bool:
    # Never apply cleanup under high dynamic pressure.
    if pressure >= 0.70:
        return False
    return requested_apply


def main() -> None:
    parser = argparse.ArgumentParser(description="Automated maintenance with overload guards")
    parser.add_argument("--apply", action="store_true", help="Attempt apply mode if safe")
    parser.add_argument("--tag", default="manual", help="Run label for audits")
    args = parser.parse_args()

    model = PhysicsModel()
    state = model.capture()
    cleaner = SafeCleaner()

    apply_mode = choose_mode(state["pressure"], args.apply)
    result = cleaner.run(dry_run=not apply_mode)
    payload = {
        "tag": args.tag,
        "requested_apply": args.apply,
        "actual_apply": apply_mode,
        "physics_state": state,
        "cleanup_result": result,
    }

    out_dir = Path(__file__).resolve().parents[1] / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"maintenance-{args.tag}.json"
    out_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
