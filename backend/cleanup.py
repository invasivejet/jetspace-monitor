import os
import shutil
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List

import psutil


@dataclass
class CleanupItem:
    path: str
    kind: str
    size_bytes: int
    modified_ts: float
    action: str


@dataclass
class CleanupResult:
    dry_run: bool
    scanned_items: int
    planned_items: int
    deleted_items: int
    reclaimed_bytes: int
    skipped_due_to_load: bool
    skipped_due_to_disk_floor: bool
    errors: List[str]
    items: List[CleanupItem]


class SafeCleaner:
    """Safe cleaner focused on temp/cache data only."""

    def __init__(self) -> None:
        self.disk_root = "C:\\" if Path("C:\\").exists() else "/"
        self.max_items = int(os.getenv("JETSPACE_CLEANUP_MAX_ITEMS", "500"))
        self.min_age_hours = int(os.getenv("JETSPACE_CLEANUP_MIN_AGE_HOURS", "24"))
        self.max_delete_mb_per_run = int(os.getenv("JETSPACE_CLEANUP_MAX_DELETE_MB", "2048"))
        self.default_dry_run = os.getenv("JETSPACE_CLEANUP_DRY_RUN", "true").lower() == "true"
        self.max_cpu_percent = float(os.getenv("JETSPACE_CLEANUP_MAX_CPU_PERCENT", "70"))
        self.max_ram_percent = float(os.getenv("JETSPACE_CLEANUP_MAX_RAM_PERCENT", "80"))
        self.min_free_disk_gb = float(os.getenv("JETSPACE_CLEANUP_MIN_FREE_DISK_GB", "8"))

        home = Path.home()
        self.targets = [
            Path(os.getenv("TEMP", str(home / "AppData" / "Local" / "Temp"))),
            home / ".cache",
            home / "AppData" / "Local" / "pip" / "Cache",
            home / ".npm" / "_cacache",
        ]
        # Hard block any critical paths.
        self.blocked = {
            Path("C:/Windows"),
            Path("C:/Program Files"),
            Path("C:/Program Files (x86)"),
            Path("C:/Users"),
            Path("C:/"),
        }

    def _is_safe_path(self, p: Path) -> bool:
        p_resolved = p.resolve()
        for blocked in self.blocked:
            try:
                if p_resolved == blocked.resolve():
                    return False
            except Exception:
                continue
        return True

    def _iter_candidates(self) -> List[CleanupItem]:
        now = time.time()
        min_age_seconds = self.min_age_hours * 3600
        candidates: List[CleanupItem] = []

        for root in self.targets:
            if not root.exists():
                continue
            if not self._is_safe_path(root):
                continue

            try:
                for entry in root.iterdir():
                    try:
                        st = entry.stat()
                        age = now - st.st_mtime
                        if age < min_age_seconds:
                            continue
                        size = st.st_size if entry.is_file() else self._dir_size(entry)
                        candidates.append(
                            CleanupItem(
                                path=str(entry),
                                kind="dir" if entry.is_dir() else "file",
                                size_bytes=size,
                                modified_ts=st.st_mtime,
                                action="delete",
                            )
                        )
                    except Exception:
                        continue
            except Exception:
                continue

        # Largest-first for maximum payoff with low item count.
        candidates.sort(key=lambda x: x.size_bytes, reverse=True)
        return candidates[: self.max_items]

    def _dir_size(self, root: Path) -> int:
        total = 0
        try:
            for base, _, files in os.walk(root):
                for f in files:
                    fp = Path(base) / f
                    try:
                        total += fp.stat().st_size
                    except Exception:
                        continue
        except Exception:
            return total
        return total

    def _system_is_overloaded(self) -> bool:
        cpu = psutil.cpu_percent(interval=0.2)
        ram = psutil.virtual_memory().percent
        return cpu > self.max_cpu_percent or ram > self.max_ram_percent

    def _below_disk_floor(self) -> bool:
        disk = psutil.disk_usage(self.disk_root)
        free_gb = disk.free / (1024**3)
        return free_gb < self.min_free_disk_gb

    def run(self, dry_run: bool | None = None) -> Dict:
        if dry_run is None:
            dry_run = self.default_dry_run

        overloaded = self._system_is_overloaded()
        below_floor = self._below_disk_floor()

        # If machine is already under pressure, do not run destructive cleanup.
        if overloaded and not dry_run:
            result = CleanupResult(
                dry_run=dry_run,
                scanned_items=0,
                planned_items=0,
                deleted_items=0,
                reclaimed_bytes=0,
                skipped_due_to_load=True,
                skipped_due_to_disk_floor=False,
                errors=["cleanup skipped due to high CPU/RAM pressure"],
                items=[],
            )
            return asdict(result)

        # If free disk is critically low, skip to avoid riskier large deletions while pressure is high.
        if below_floor and not dry_run:
            result = CleanupResult(
                dry_run=dry_run,
                scanned_items=0,
                planned_items=0,
                deleted_items=0,
                reclaimed_bytes=0,
                skipped_due_to_load=False,
                skipped_due_to_disk_floor=True,
                errors=["cleanup skipped because free disk is below configured floor"],
                items=[],
            )
            return asdict(result)

        candidates = self._iter_candidates()
        budget_bytes = self.max_delete_mb_per_run * 1024 * 1024

        reclaimed = 0
        deleted = 0
        errors: List[str] = []
        items_applied: List[CleanupItem] = []

        for item in candidates:
            if reclaimed + item.size_bytes > budget_bytes:
                continue

            items_applied.append(item)
            if dry_run:
                reclaimed += item.size_bytes
                continue

            target = Path(item.path)
            try:
                if item.kind == "file":
                    target.unlink(missing_ok=True)
                else:
                    shutil.rmtree(target, ignore_errors=False)
                reclaimed += item.size_bytes
                deleted += 1
            except Exception as exc:
                errors.append(f"{item.path}: {exc}")

        result = CleanupResult(
            dry_run=dry_run,
            scanned_items=len(candidates),
            planned_items=len(items_applied),
            deleted_items=deleted,
            reclaimed_bytes=reclaimed,
            skipped_due_to_load=False,
            skipped_due_to_disk_floor=False,
            errors=errors[:50],
            items=items_applied,
        )
        return asdict(result)

