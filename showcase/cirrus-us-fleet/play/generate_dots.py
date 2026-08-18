#!/usr/bin/env python3
"""Stipple US states. CONUS is full-bleed; AK/HI are tiny insets."""
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
W, H = 1180, 700
PAD = 28
# Insets live in the empty Mexico / Pacific pocket. CONUS uses the whole frame.
AK_BOX = (36.0, H - 176.0, 156.0, 128.0)
HI_BOX = (208.0, H - 102.0, 124.0, 62.0)


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


def project_raw(lon, lat, name: str):
    if name == "Alaska":
        return albers(lon, lat, 64.0, -154.0, 55.0, 65.0)
    if name == "Hawaii":
        return albers(lon, lat, 20.6, -157.0, 19.0, 21.5)
    return albers(lon, lat, 38.0, -96.5, 29.5, 45.5)


def keep_vertex(name: str, lon: float, lat: float) -> bool:
    if name == "Alaska":
        return lon > -169.5 and lat > 51.2
    if name == "Hawaii":
        return -161.0 < lon < -154.0 and 18.5 < lat < 22.5
    return True


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


def bbox(rings):
    xs, ys = [], []
    for ring in rings:
        for x, y in ring:
            xs.append(x)
            ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)


def fit(rings, box, src=None, flip_y=True, pad=4.0):
    bx, by, bw, bh = box
    minx, miny, maxx, maxy = src if src else bbox(rings)
    sx = (bw - 2 * pad) / max(maxx - minx, 1e-9)
    sy = (bh - 2 * pad) / max(maxy - miny, 1e-9)
    s = min(sx, sy)
    cx = (minx + maxx) / 2
    cy = (miny + maxy) / 2
    ox = bx + bw / 2
    oy = by + bh / 2
    out = []
    for ring in rings:
        pts = []
        for x, y in ring:
            px = ox + (x - cx) * s
            py = oy - (y - cy) * s if flip_y else oy + (y - cy) * s
            pts.append((px, py))
        out.append(pts)
    return out


def main() -> None:
    geo = json.loads(GEO.read_text(encoding="utf-8"))
    raw: dict[str, list[list[tuple[float, float]]]] = {}
    for feat in geo["features"]:
        name = feat["properties"]["name"]
        if name in SKIP:
            continue
        abbr = NAME_TO_ABBR[name]
        rings = []
        for ring in rings_of(feat["geometry"]):
            pts = [
                project_raw(lon, lat, name)
                for lon, lat in ring
                if keep_vertex(name, lon, lat)
            ]
            if len(pts) >= 4:
                rings.append(pts)
        if rings:
            raw[abbr] = rings

    conus = {k: v for k, v in raw.items() if k not in {"AK", "HI"}}
    conus_src = bbox([ring for rings in conus.values() for ring in rings])
    px_rings: dict[str, list[list[tuple[float, float]]]] = {}
    frame = (PAD, PAD, W - 2 * PAD, H - 2 * PAD)
    for abbr, rings in conus.items():
        px_rings[abbr] = fit(rings, frame, src=conus_src, pad=0)
    if "AK" in raw:
        px_rings["AK"] = fit(raw["AK"], AK_BOX, pad=3)
    if "HI" in raw:
        px_rings["HI"] = fit(raw["HI"], HI_BOX, pad=2)

    def fill(step: float, only: set[str] | None = None) -> None:
        y = 8.0
        while y < H - 8:
            x = 8.0 + (0 if int(y / step) % 2 == 0 else step * 0.5)
            while x < W - 8:
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

    step = 5.8
    dots: dict[str, list[list[float]]] = {k: [] for k in px_rings}
    fill(step)
    tiny = {k for k, v in dots.items() if len(v) < 14}
    if tiny:
        fill(2.3, tiny)

    labels = {}
    for abbr, pts in dots.items():
        if not pts:
            continue
        labels[abbr] = [
            round(sum(p[0] for p in pts) / len(pts), 1),
            round(sum(p[1] for p in pts) / len(pts), 1),
        ]

    payload = {
        "w": W,
        "h": H,
        "dots": dots,
        "labels": labels,
        "insets": {"AK": list(AK_BOX), "HI": list(HI_BOX)},
    }
    OUT.write_text("window.STATE_DOTS = " + json.dumps(payload, separators=(",", ":")) + ";\n", encoding="utf-8")
    n = sum(len(v) for v in dots.values())
    print(f"states={len(dots)} dots={n} → {OUT.name} ({OUT.stat().st_size:,} bytes)")
    print("AK", len(dots.get("AK", [])), "HI", len(dots.get("HI", [])), "CA", len(dots.get("CA", [])))
    empty = [k for k, v in dots.items() if not v]
    if empty:
        print("empty", empty)


if __name__ == "__main__":
    main()
