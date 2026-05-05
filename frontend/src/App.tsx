import { useEffect, useMemo, useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

type Sample = {
  ts: number;
  cpu: number;
  ram: number;
  disk: number;
  net_sent: number;
  net_recv: number;
  d_cpu: number;
  d2_cpu: number;
};

type Physics = {
  ts: number;
  cpu: number;
  ram: number;
  disk: number;
  d_cpu: number;
  d_ram: number;
  d2_cpu: number;
  pressure: number;
  free_mem_gb: number;
  free_disk_gb: number;
};

type WsPayload =
  | Sample
  | {
      sample: Sample;
      physics: Physics;
    };

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8010";
const MAX_POINTS = 180;

function isWsEnvelope(raw: WsPayload): raw is { sample: Sample; physics: Physics } {
  return typeof raw === "object" && raw !== null && "sample" in raw && "physics" in raw;
}

function normalizeWsPayload(raw: WsPayload): { sample: Sample; physics?: Physics } {
  if (isWsEnvelope(raw)) {
    return { sample: raw.sample, physics: raw.physics };
  }
  return { sample: raw };
}

function App() {
  const [connected, setConnected] = useState(false);
  const [rows, setRows] = useState<Array<{ sample: Sample; physics?: Physics }>>([]);
  const [events, setEvents] = useState<string[]>([]);
  const [modalSummary, setModalSummary] = useState<string>("");

  useEffect(() => {
    const ws = new WebSocket(`${API_BASE.replace("http", "ws")}/ws`);
    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onerror = () => setConnected(false);
    ws.onmessage = (event: MessageEvent<string>) => {
      const parsed: WsPayload = JSON.parse(event.data);
      const norm = normalizeWsPayload(parsed);
      setRows((prev) => [...prev.slice(-MAX_POINTS + 1), norm]);

      const p = norm.physics;
      const cpu = norm.sample.cpu;
      const ram = norm.sample.ram;
      const pressure = p?.pressure;
      const freeDisk = p?.free_disk_gb;

      const hot =
        cpu > 85 ||
        ram > 85 ||
        (typeof pressure === "number" && pressure > 0.85) ||
        (typeof freeDisk === "number" && freeDisk < 5);

      if (hot) {
        const ts = new Date(norm.sample.ts * 1000).toLocaleTimeString();
        const pressureTxt = typeof pressure === "number" ? ` pressure=${pressure.toFixed(3)}` : "";
        const diskTxt = typeof freeDisk === "number" ? ` free_disk_gb=${freeDisk.toFixed(2)}` : "";
        setEvents((prev) =>
          [`[${ts}] cpu=${cpu.toFixed(1)} ram=${ram.toFixed(1)}${pressureTxt}${diskTxt}`, ...prev].slice(0, 200)
        );
      }
    };

    return () => ws.close();
  }, []);

  useEffect(() => {
    let cancelled = false;
    const tick = async () => {
      try {
        const r = await fetch(`${API_BASE}/modal/latest-diagnostic`);
        if (!r.ok) return;
        const d = await r.json();
        if (cancelled) return;
        setModalSummary(`${d.classification ?? "unknown"} @ ${d.generated_at ?? "?"}`);
      } catch {
        // ignore — optional transparency panel
      }
    };
    tick();
    const id = window.setInterval(tick, 15000);
    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
  }, []);

  const latest = rows[rows.length - 1];
  const latestPhysics = latest?.physics;

  const chartPrimary = useMemo(
    () =>
      rows.map((r) => {
        const s = r.sample;
        const p = r.physics;
        return {
          time: new Date(s.ts * 1000).toLocaleTimeString(),
          cpu: Number(s.cpu.toFixed(2)),
          ram: Number(s.ram.toFixed(2)),
          disk: Number(s.disk.toFixed(2)),
          pressure: p ? Number(p.pressure.toFixed(4)) : null,
          d_ram: p ? Number(p.d_ram.toFixed(3)) : null,
          d_cpu: Number(s.d_cpu.toFixed(2)),
          d2_cpu: Number(s.d2_cpu.toFixed(2))
        };
      }),
    [rows]
  );

  const chartResources = useMemo(
    () =>
      rows.map((r) => {
        const s = r.sample;
        const p = r.physics;
        return {
          time: new Date(s.ts * 1000).toLocaleTimeString(),
          free_mem_gb: p ? Number(p.free_mem_gb.toFixed(3)) : null,
          free_disk_gb: p ? Number(p.free_disk_gb.toFixed(3)) : null,
          net_sent_kbps: Number(((s.net_sent * 8) / 1000).toFixed(1)),
          net_recv_kbps: Number(((s.net_recv * 8) / 1000).toFixed(1))
        };
      }),
    [rows]
  );

  return (
    <main className="container">
      <section className="header">
        <div>
          <div className="title">Jetspace Monitor</div>
          <div className="subtitle">
            Real-time physics + resource telemetry — API <span className="kbd">{API_BASE}</span>
          </div>
        </div>
        <div className="headerRight">
          <div className={`pill ${connected ? "ok" : "bad"}`}>{connected ? "live" : "offline"}</div>
          <div className="muted small">
            panels: <span className="kbd">/control</span> · <span className="kbd">/mini</span>
          </div>
        </div>
      </section>

      <section className="grid4">
        <div className="card">
          <div className="muted">CPU</div>
          <div className="metric">{latest ? `${latest.sample.cpu.toFixed(1)}%` : "--"}</div>
        </div>
        <div className="card">
          <div className="muted">RAM</div>
          <div className="metric">{latest ? `${latest.sample.ram.toFixed(1)}%` : "--"}</div>
        </div>
        <div className="card">
          <div className="muted">Disk</div>
          <div className="metric">{latest ? `${latest.sample.disk.toFixed(1)}%` : "--"}</div>
        </div>
        <div className="card">
          <div className="muted">Pressure</div>
          <div className="metric">{latestPhysics ? latestPhysics.pressure.toFixed(3) : "--"}</div>
        </div>
        <div className="card">
          <div className="muted">Free RAM (GB)</div>
          <div className="metric">{latestPhysics ? latestPhysics.free_mem_gb.toFixed(2) : "--"}</div>
        </div>
        <div className="card">
          <div className="muted">Free disk (GB)</div>
          <div className="metric">{latestPhysics ? latestPhysics.free_disk_gb.toFixed(2) : "--"}</div>
        </div>
        <div className="card span2">
          <div className="muted">Modal diagnostic (latest report)</div>
          <div className="metric smallMetric">{modalSummary || "—"}</div>
        </div>
      </section>

      <section className="panels">
        <div className="card">
          <h3>Utilization + dynamics</h3>
          <div className="chart">
            <ResponsiveContainer>
              <LineChart data={chartPrimary}>
                <CartesianGrid strokeDasharray="3 3" stroke="#243250" />
                <XAxis dataKey="time" tick={{ fill: "#9fb0c5", fontSize: 11 }} minTickGap={24} />
                <YAxis tick={{ fill: "#9fb0c5", fontSize: 11 }} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="cpu" stroke="#7c5cff" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="ram" stroke="#ff4ecd" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="disk" stroke="#4cc9f0" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="pressure" stroke="#b388ff" strokeWidth={2} dot={false} connectNulls />
                <Line type="monotone" dataKey="d_cpu" stroke="#fca311" dot={false} />
                <Line type="monotone" dataKey="d2_cpu" stroke="#80ed99" dot={false} />
                <Line type="monotone" dataKey="d_ram" stroke="#ffd166" dot={false} connectNulls />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="stack">
          <div className="card">
            <h3>Headroom + network deltas</h3>
            <div className="chart chartShort">
              <ResponsiveContainer>
                <LineChart data={chartResources}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#243250" />
                  <XAxis dataKey="time" tick={{ fill: "#9fb0c5", fontSize: 11 }} minTickGap={24} />
                  <YAxis tick={{ fill: "#9fb0c5", fontSize: 11 }} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="free_mem_gb" stroke="#56cfe1" strokeWidth={2} dot={false} connectNulls />
                  <Line type="monotone" dataKey="free_disk_gb" stroke="#ff9f1c" strokeWidth={2} dot={false} connectNulls />
                  <Line type="monotone" dataKey="net_sent_kbps" stroke="#c77dff" dot={false} connectNulls />
                  <Line type="monotone" dataKey="net_recv_kbps" stroke="#72efdd" dot={false} connectNulls />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="card">
            <h3>Pressure events</h3>
            <div className="log">
              {events.length === 0 ? "No notable pressure events yet." : events.join("\n")}
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}

export default App;
