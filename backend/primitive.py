import math
import os
import random
import time
from typing import Dict, List

import psutil


def _gpu_snapshot() -> Dict:
    # Optional GPU path: only if nvidia-smi exists.
    import subprocess

    try:
        out = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=utilization.gpu,memory.used,memory.total",
                "--format=csv,noheader,nounits",
            ],
            stderr=subprocess.DEVNULL,
            timeout=1.5,
            text=True,
        ).strip()
        util, mem_used, mem_total = [float(x.strip()) for x in out.split(",")]
        return {
            "available": True,
            "util_percent": util,
            "mem_used_mb": mem_used,
            "mem_total_mb": mem_total,
        }
    except Exception:
        return {"available": False}


def _prng_probe(samples: int = 64) -> Dict:
    start = time.perf_counter()
    data = os.urandom(samples)
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    ones = sum(bin(b).count("1") for b in data)
    bit_balance = ones / (samples * 8)
    return {
        "sample_bytes": samples,
        "latency_ms": round(elapsed_ms, 4),
        "bit_balance": round(bit_balance, 4),
    }


def primitive_state() -> Dict:
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage("C:\\").percent

    # Minimal symplectic update for harmonic oscillator as discrete Hamiltonian map.
    q = random.uniform(-1.0, 1.0)
    p = random.uniform(-1.0, 1.0)
    dt = 0.05
    p_next = p - dt * q
    q_next = q + dt * p_next
    energy = 0.5 * (q_next * q_next + p_next * p_next)

    return {
        "ts": time.time(),
        "memory_state_percent": ram,
        "cpu_transform_percent": cpu,
        "disk_geometry_percent": disk,
        "gpu_field": _gpu_snapshot(),
        "prng_probe": _prng_probe(),
        "discrete_hamiltonian": {
            "q": round(q_next, 6),
            "p": round(p_next, 6),
            "energy": round(energy, 6),
            "meaning": "compute step as symplectic map",
        },
    }


def primitive_language() -> Dict:
    return {
        "memory": "state manifold: where active symbols live",
        "cpu": "discrete rule engine: branch-heavy symbolic transforms",
        "gpu": "field evaluator: same map over many points",
        "prng": "entropy injector for sampling and robust exploration",
        "numerics": "ODE/PDE discretization: reality approximated by update rules",
    }


def solved_minimal_problems() -> List[Dict]:
    return [
        {
            "problem": "Why caches matter for CPU speed",
            "minimal_model": "Sequential sum over array of size n",
            "answer": "Complexity stays O(n), but memory locality changes constant factors by large multiples.",
        },
        {
            "problem": "When GPU beats CPU",
            "minimal_model": "Apply f(x)=x^2 to n values",
            "answer": "CPU O(n) serial; GPU O(n/p) per core-group in practice with transfer overhead; wins at larger n.",
        },
        {
            "problem": "Number theory in machine representation",
            "minimal_model": "Compute a^b mod m with repeated squaring",
            "answer": "Bit complexity O(log b) multiplications; integers are finite-word state objects in memory.",
        },
        {
            "problem": "Discrete Hamiltonian dynamics is computing",
            "minimal_model": "Symplectic Euler on dq/dt=p, dp/dt=-q",
            "answer": "Each step is an information-preserving map; long-horizon behavior is stable vs naive Euler drift.",
        },
    ]

