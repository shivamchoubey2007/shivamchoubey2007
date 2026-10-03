"""Turn a dark-theme card SVG into its light-theme twin by remapping colours."""
import re

MAP = {
    "#0d0e16": "#f8fafc", "#12141f": "#eef2f7", "#10121c": "#eef2f7", "#141726": "#ffffff",
    "#0f1220": "#f1f5f9", "#1e293b": "#cbd5e1",
    "#f8fafc": "#0f172a", "#f1f5f9": "#0f172a", "#e2e8f0": "#1e293b", "#cbd5e1": "#334155",
    "#94a3b8": "#475569", "#64748b": "#5b6b80",
    "#22d3ee": "#0891b2", "#a78bfa": "#7c3aed", "#f472b6": "#db2777", "#fca5a5": "#dc2626",
    "#61dafb": "#0e7490", "#f7df1e": "#a16207", "#fcd34d": "#b45309", "#6cc24a": "#3f7d20",
    "#60a5fa": "#2563eb", "#38bdf8": "#0369a1", "#fb7185": "#be123c", "#4ade80": "#15803d", "#fb923c": "#c2410c", "#3178c6": "#2563eb",
}

def to_light(svg: str) -> str:
    # translucent white overlays (surfaces, borders, dots) become translucent dark ones
    svg = re.sub(r'(fill|stroke)="#fff"(\s+(?:fill-opacity|stroke-opacity|opacity)=)', r'\1="#0f172a"\2', svg)
    return re.sub(r"#[0-9a-fA-F]{6}\b", lambda m: MAP.get(m.group(0).lower(), m.group(0)), svg)
