import time
from collections import deque
from dataclasses import asdict, dataclass
from typing import Deque, Dict
from pathlib import Path

import psutil


@dataclass
class PhysicsState:
    ts: float
    cpu: float
    ram: float
    disk: float
    d_cpu: float
    d_ram: float
    d2_cpu: float
    pressure: float
    free_mem_gb: float
    free_disk_gb: float


class PhysicsModel:
    """State-space model for system dynamics and overload risk."""

    def __init__(self) -> None:
        self.disk_root = "C:\\" if Path("C:\\").exists() else "/"
        self.prev_cpu: float | None = None
        self.prev_ram: float | None = None
        self.prev_d_cpu: float | None = None
        self.recent_pressure: Deque[float] = deque(maxlen=120)

    def capture(self) -> Dict:
        ts = time.time()
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage(self.disk_root).percent
        vm = psutil.virtual_memory()
        du = psutil.disk_usage(self.disk_root)

        d_cpu = 0.0 if self.prev_cpu is None else cpu - self.prev_cpu
        d_ram = 0.0 if self.prev_ram is None else ram - self.prev_ram
        d2_cpu = 0.0 if self.prev_d_cpu is None else d_cpu - self.prev_d_cpu

        # Pressure is bounded [0,1], weighted to penalize acceleration spikes.
        pressure = min(
            1.0,
            max(
                0.0,
                0.45 * (cpu / 100.0)
                + 0.35 * (ram / 100.0)
                + 0.20 * min(1.0, abs(d2_cpu) / 20.0),
            ),
        )
        self.recent_pressure.append(pressure)

        self.prev_cpu = cpu
        self.prev_ram = ram
        self.prev_d_cpu = d_cpu

        return asdict(
            PhysicsState(
                ts=ts,
                cpu=cpu,
                ram=ram,
                disk=disk,
                d_cpu=d_cpu,
                d_ram=d_ram,
                d2_cpu=d2_cpu,
                pressure=pressure,
                free_mem_gb=vm.available / (1024**3),
                free_disk_gb=du.free / (1024**3),
            )
        )

