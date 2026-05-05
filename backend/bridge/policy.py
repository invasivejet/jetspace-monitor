from collections import deque
from dataclasses import dataclass


@dataclass
class PolicyDecision:
    label: str
    reason: str


class CorrelationPolicy:
    def __init__(self, window: int = 30) -> None:
        self.window = window
        self.cpu_series: deque[float] = deque(maxlen=window)
        self.ram_series: deque[float] = deque(maxlen=window)

    def evaluate(self, payload: dict) -> PolicyDecision:
        cpu = float(payload.get("state", {}).get("cpu", 0.0))
        ram = float(payload.get("state", {}).get("ram", 0.0))
        anomaly = float(payload.get("anomaly_score", 0.0))

        self.cpu_series.append(cpu)
        self.ram_series.append(ram)

        cpu_avg = sum(self.cpu_series) / len(self.cpu_series) if self.cpu_series else cpu
        ram_avg = sum(self.ram_series) / len(self.ram_series) if self.ram_series else ram

        if anomaly > 0.8:
            return PolicyDecision("alert", "remote anomaly score above 0.8")
        if cpu > 85 and ram > 80:
            return PolicyDecision("pressure", "high cpu+ram pair")
        if cpu > cpu_avg + 15 or ram > ram_avg + 12:
            return PolicyDecision("watch", "deviation above rolling baseline")
        return PolicyDecision("normal", "within expected band")

