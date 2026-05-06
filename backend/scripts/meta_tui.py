import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request


API_BASE = os.getenv("JETSPACE_API_BASE", "http://127.0.0.1:8010")


def _get_json(path: str):
    with urllib.request.urlopen(f"{API_BASE}{path}", timeout=4) as r:
        return json.loads(r.read().decode("utf-8"))


def _gpu_probe():
    try:
        out = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=utilization.gpu,memory.used,memory.total",
                "--format=csv,noheader,nounits",
            ],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=1.2,
        ).strip()
        util, mem_used, mem_total = [x.strip() for x in out.split(",")]
        return f"GPU util={util}% mem={mem_used}/{mem_total} MB"
    except Exception:
        return "GPU unavailable (no nvidia-smi or no NVIDIA GPU)"


def _prng_probe():
    t0 = time.perf_counter()
    b = os.urandom(64)
    dt_ms = (time.perf_counter() - t0) * 1000.0
    ones = sum(bin(x).count("1") for x in b)
    bal = ones / (64 * 8)
    return f"PRNG latency={dt_ms:.3f}ms bit-balance={bal:.3f}"


def _bar(value: float, width: int = 24) -> str:
    v = max(0.0, min(100.0, value))
    n = int((v / 100.0) * width)
    return "█" * n + "·" * (width - n)


def _pressure_label(p: float) -> str:
    if p < 0.35:
        return "stable"
    if p < 0.65:
        return "watch"
    return "high"


def _render(phys, control, problems):
    purple = "\033[38;5;141m"
    lilac = "\033[38;5;183m"
    white = "\033[38;5;255m"
    reset = "\033[0m"
    bold = "\033[1m"
    clear = "\033[2J\033[H"
    lines = [
        clear,
        f"{bold}{purple}JETSPACE META CONTROL TERMINAL{reset}  {lilac}(physics invariants + primitive compute){reset}",
        f"{lilac}local-only control plane | ethical diagnostics | safe actuation gates{reset}",
        "",
        f"{white}STATE MANIFOLD (memory/resources){reset}",
        f"  CPU  {phys['cpu']:5.1f}% [{_bar(phys['cpu'])}]",
        f"  RAM  {phys['ram']:5.1f}% [{_bar(phys['ram'])}]",
        f"  DISK {phys['disk']:5.1f}% [{_bar(phys['disk'])}]",
        f"  free_mem={phys['free_mem_gb']:.2f}GB free_disk={phys['free_disk_gb']:.2f}GB",
        "",
        f"{white}DYNAMICS (discrete flow){reset}",
        f"  d_cpu={phys['d_cpu']:.2f} d_ram={phys['d_ram']:.2f} d2_cpu={phys['d2_cpu']:.2f}",
        f"  pressure={phys['pressure']:.3f} ({_pressure_label(phys['pressure'])})",
        "",
        f"{white}PRIMITIVES{reset}",
        f"  {_gpu_probe()}",
        f"  {_prng_probe()}",
        "",
        f"{white}CLEANUP CONTROL{reset}",
        f"  plan_items={control['cleanup_plan']['planned_items']} "
        f"plan_reclaim_mb={control['cleanup_plan']['reclaimed_bytes']/(1024*1024):.1f} "
        f"bridge_events={control['bridge_recent_events']}",
        "",
        f"{white}MINIMAL PROBLEMS (solved){reset}",
    ]
    for i, p in enumerate(problems, start=1):
        lines.append(f"  {i}. {p['problem']} -> {p['answer']}")
    lines += [
        "",
        f"{lilac}Complexity note:{reset} asymptotic class + hardware geometry (memory locality, parallel width) determine real speed.",
        f"{lilac}Hamiltonian note:{reset} discrete symplectic updates preserve structure better than naive updates.",
        "",
        f"{purple}keys:{reset} Ctrl+C quit | refresh ~{os.getenv('JETSPACE_META_REFRESH_SEC', '2.5')}s",
    ]
    sys.stdout.write("\n".join(lines))
    sys.stdout.flush()


def main():
    while True:
        try:
            phys = _get_json("/physics/state")
            control = _get_json("/control/state")
            problems = _get_json("/primitive/problems")
            _render(phys, control, problems)
        except urllib.error.URLError:
            sys.stdout.write("\033[2J\033[H\033[38;5;197mAPI not reachable at " + API_BASE + "\033[0m\n")
            sys.stdout.write("Start backend API then retry.\n")
            sys.stdout.flush()
        time.sleep(float(os.getenv("JETSPACE_META_REFRESH_SEC", "2.5")))


if __name__ == "__main__":
    main()
