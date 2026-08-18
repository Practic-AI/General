#!/usr/bin/env python3
"""Stipple US states into a regular grid of dots (Polymarket-style)."""
from __future__ import annotations

import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
GEO = HERE / "_us-states.json"
OUT = HERE / "dots-data.js"

NAME_TO_ABBR = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI",
    "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
    "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME",
    "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
    "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE",
    "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM",
    "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
    "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI",
    "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX",
    "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
}

SKIP = {"Puerto Rico"}
W, H = 1100, 680
PAD = 18


def albers(lon, lat, lat0, lon0, lat1, lat2):
    d = math.pi / 180.0
    phi, lam = lat * d, lon * d
    phi0, lam0 = lat0 * d, lon0 * d
    phi1, phi2 = lat1 * d, lat2 * d
    n = 0.5 * (math.sin(phi1) + math.sin(phi2))
    if abs(n) < 1e-9:
        n = 1e-9
    c = math.cos(phi1) ** 2 + 2 * n * math.sin(phi1)
    rho0 = math.sqrt(max(c - 2 * n * math.sin(phi0), 0.0)) / n
    theta = n * (lam - lam0)
    rho = math.sqrt(max(c - 2 * n * math.sin(phi), 0.0)) / n
    return rho * math.sin(theta), rho0 - rho * math.cos(theta)


def project(lon, lat, name: str):
    if name == "Alaska":
        x, y = albers(lon, lat, 63.0, -152.0, 55.0, 65.0)
        return x * 0.37 - 0.72, y * 0.37 + 0.18
    if name == "Hawaii":
        x, y = albers(lon, lat, 20.9, -157.0, 8.0, 18.0)
        return x * 1.15 - 0.22, y * 1.15 + 0.22
    return albers(lon, lat, 37.5, -96.0, 29.5, 45.5)


def rings_of(geom):
    t = geom["type"]
    if t == "Polygon":
        return [geom["coordinates"][0]]
    if t == "MultiPolygon":
        return [poly[0] for poly in geom["coordinates"]]
    return []


def pip(x, y, ring):
    inside = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-15) + xi:
            inside = not inside
        j = i
    return inside


def main() -> None:
    geo = json.loads(GEO.read_text(encoding="utf-8"))
    projected: dict[str, list[list[tuple[float, float]]]] = {}
    xs, ys = [], []
    for feat in geo["features"]:
        name = feat["properties"]["name"]
        if name in SKIP:
            continue
        abbr = NAME_TO_ABBR[name]
        rings = []
        for ring in rings_of(feat["geometry"]):
            pts = [project(lon, lat, name) for lon, lat in ring]
            rings.append(pts)
            for x, y in pts:
                xs.append(x)
                ys.append(y)
        projected[abbr] = rings

    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    # flip y for canvas
    span = max(maxx - minx, maxy - miny)

    def to_px(x, y):
        px = PAD + (x - minx) / (maxx - minx) * (W - 2 * PAD)
        py = PAD + (1.0 - (y - miny) / (maxy - miny)) * (H - 2 * PAD)
        return px, py

    px_rings: dict[str, list[list[tuple[float, float]]]] = {}
    for abbr, rings in projected.items():
        px_rings[abbr] = [[to_px(x, y) for x, y in ring] for ring in rings]

    def fill(step: float, only: set[str] | None = None) -> None:
        y = PAD
        while y < H - PAD:
            x = PAD + (0 if int((y - PAD) / step) % 2 == 0 else step * 0.5)
            while x < W - PAD:
                hit = None
                for abbr, rings in px_rings.items():
                    if only is not None and abbr not in only:
                        continue
                    if any(pip(x, y, ring) for ring in rings):
                        hit = abbr
                        break
                if hit:
                    dots[hit].append([round(x, 1), round(y, 1)])
                x += step
            y += step

    step = 5.6
    dots: dict[str, list[list[float]]] = {k: [] for k in px_rings}
    fill(step)
    tiny = {k for k, v in dots.items() if len(v) < 12}
    if tiny:
        fill(2.4, tiny)

    labels = {}
    for abbr, pts in dots.items():
        if not pts:
            continue
        labels[abbr] = [
            round(sum(p[0] for p in pts) / len(pts), 1),
            round(sum(p[1] for p in pts) / len(pts), 1),
        ]

    payload = {"w": W, "h": H, "dots": dots, "labels": labels}
    OUT.write_text("window.STATE_DOTS = " + json.dumps(payload, separators=(",", ":")) + ";\n", encoding="utf-8")
    n = sum(len(v) for v in dots.values())
    print(f"states={len(dots)} dots={n} → {OUT.name} ({OUT.stat().st_size:,} bytes)")
    empty = [k for k, v in dots.items() if not v]
    if empty:
        print("empty", empty)


if __name__ == "__main__":
    main()
