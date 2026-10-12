#!/usr/bin/env python3
"""
Ten provisional drill holes for R1, for a client who asked for 10 rig holes (80-110 m) before any field data.

Keeps DT-1..DT-4 from r1_desk_targeting.py as Phase 1, then adds six Phase 2 targets: the next-best
desk-score peaks (score_s, 30 m smoothed) at least MIN_SEP apart from every other target. Collars use the
same search rule as r1_desk_targeting.py (target 50 m below surface, dip 45-65, cut the assumed 117 deg
structure at >= 35 deg, pad slope <= 15 deg, shortest hole), plus: keep collars off the mining camp.

Inputs (already in the repo): outputs/r1_desk/*.csv and the Site 02 DEM / slope GeoTIFFs.
Outputs: outputs/r1_ten_holes/ (CSV, GPX, KML, map).
Run with: python r1_ten_holes.py
"""

import math
import os

import matplotlib
import numpy as np
import pandas as pd
import pyproj
import rasterio

matplotlib.use("Agg")
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt

SITE = "drive-download-20261011T175941Z-1-001"
DESK = "outputs/r1_desk"
OUT = "outputs/r1_ten_holes"
os.makedirs(OUT, exist_ok=True)
TO_LL = pyproj.Transformer.from_crs("EPSG:32647", "EPSG:4326", always_xy=True)
TO_UTM = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32647", always_xy=True)

CAMP_LONLAT = (101.64259225, 18.26464977)  # client's phone pin of the mining camp, received 12 Oct 2026
STRIKE = 117        # dominant straight-drainage trend from r1_desk_targeting.py; assumed, not a mapped structure
TARGET_DEPTH = 50   # m below the target's ground surface
MIN_SEP = 50        # m between targets (DT design used 70 m for 4 targets; 10 do not fit in R1 at 70 m)
CAMP_CLEAR = 40     # m: no collar inside the camp footprint
N_HOLES = 10

cells = pd.read_csv(f"{DESK}/r1_cells_evidence.csv")
desk = pd.read_csv(f"{DESK}/r1_desk_candidates.csv")
desk_holes = pd.read_csv(f"{DESK}/r1_desk_provisional_holes.csv")
with rasterio.open(f"{SITE}/02_Maps/Map_Sheets/07_Elevation.tif") as ds:
    dem, dtr, dem_index = ds.read(1).astype(float), ds.transform, ds.index
with rasterio.open(f"{SITE}/02_Maps/Map_Sheets/08_Slope.tif") as ds:
    slope = ds.read(1).astype(float)
camp_e, camp_n = TO_UTM.transform(*CAMP_LONLAT)

# ------------------------------------------------------------------ targets
targets = [{"id": r.candidate, "e": r.e, "n": r.n, "phase": 1} for r in desk.itertuples()]
for r in cells.sort_values("score_s", ascending=False).itertuples():
    if len(targets) == N_HOLES:
        break
    if all(math.hypot(r.e - t["e"], r.n - t["n"]) >= MIN_SEP for t in targets):
        targets.append({"id": f"RH-{len(targets) + 1:02d}", "e": r.e, "n": r.n, "phase": 2})
assert len(targets) == N_HOLES, f"only {len(targets)} targets fit at {MIN_SEP} m spacing"


def collar(te, tn):
    """Same ranking as r1_desk_targeting.py, plus camp clearance."""
    zt = dem[dem_index(te, tn)] - TARGET_DEPTH
    best = None
    for r_ in range(15, 111, 5):
        for a_ in range(0, 360, 5):
            ce = te + r_ * math.sin(math.radians(a_))
            cn = tn + r_ * math.cos(math.radians(a_))
            if math.hypot(ce - camp_e, cn - camp_n) < CAMP_CLEAR:
                continue
            zc = dem[dem_index(ce, cn)]
            dip = math.degrees(math.atan2(zc - zt, r_))
            if not 45 <= dip <= 65:
                continue
            az = (a_ + 180) % 360
            cut = math.degrees(math.asin(abs(math.sin(math.radians(az - STRIKE))) * math.cos(math.radians(dip))))
            sl = slope[dem_index(ce, cn)]
            L = math.hypot(r_, zc - zt)
            key = (cut < 35, sl > 15, L)
            if best is None or key < best[0]:
                best = (key, ce, cn, zc, az, dip, cut, sl, L)
    return best[1:]


rows = []
for t in targets:
    ce, cn, zc, az, dip, cut, sl, L = collar(t["e"], t["n"])
    near = cells[np.hypot(cells.e - t["e"], cells.n - t["n"]) <= 30]  # same 30 m neighbourhood as the desk score
    tlo, tla = TO_LL.transform(t["e"], t["n"])
    clo, cla = TO_LL.transform(ce, cn)
    rows.append({
        "hole_id": t["id"], "phase": t["phase"],
        "target_e": round(t["e"], 1), "target_n": round(t["n"], 1), "target_lat": round(tla, 6), "target_lon": round(tlo, 6),
        "collar_e": round(ce, 1), "collar_n": round(cn, 1), "collar_lat": round(cla, 6), "collar_lon": round(clo, 6),
        "collar_elev_m": round(zc, 1), "collar_slope_deg": round(sl, 1),
        "azimuth": round(az), "dip": -round(dip), "length_to_target_m": round(L),
        "planned_depth_m": int(math.ceil((L + 40) / 10) * 10),
        "cut_angle_vs_assumed_117": round(cut),
        "desk_score": round(near.score_s.mean(), 3),
        "s2_feox_pct": round(near.pct_feox.mean()), "s2_fe900_pct": round(near.pct_fe900.mean()),
        "s2_clay_pct": round(near.pct_clay.mean()), "bare_freq": round(near.s2p1_bare_freq.mean(), 2),
        "emit_fe_of4": round(near.emit_fe.mean(), 1), "emit_kaol_of4": round(near.emit_kaol.mean(), 1),
        "hand_m": round(near.hand_m.mean(), 1),
        "dist_to_camp_m": round(math.hypot(t["e"] - camp_e, t["n"] - camp_n)),
    })
holes = pd.DataFrame(rows)

# self-check: Phase 1 collars must match the DT design unless the camp rule moved them
for h in holes[holes.phase == 1].itertuples():
    d = desk_holes[desk_holes.candidate == h.hole_id].iloc[0]
    moved = math.hypot(h.collar_e - d.collar_e, h.collar_n - d.collar_n)
    if math.hypot(d.collar_e - camp_e, d.collar_n - camp_n) >= CAMP_CLEAR:
        assert moved < 1, f"{h.hole_id} collar drifted {moved:.1f} m from the DT design"

# collars within 25 m of each other can share one pad
pad = list(range(len(holes)))
for i in range(len(holes)):
    for j in range(i):
        if math.hypot(holes.collar_e[i] - holes.collar_e[j], holes.collar_n[i] - holes.collar_n[j]) <= 25:
            pad[i] = pad[j]
holes["pad"] = [f"P{sorted(set(pad)).index(p) + 1}" for p in pad]
holes.to_csv(f"{OUT}/r1_ten_holes.csv", index=False)
print(holes[["hole_id", "phase", "pad", "collar_e", "collar_n", "azimuth", "dip", "planned_depth_m",
             "desk_score", "dist_to_camp_m"]].to_string(index=False))
print("total metres: phase 1", holes[holes.phase == 1].planned_depth_m.sum(),
      "| phase 2", holes[holes.phase == 2].planned_depth_m.sum(), "| all", holes.planned_depth_m.sum())

# ------------------------------------------------------------------ GPX / KML
gpx = ['<?xml version="1.0" encoding="UTF-8"?>',
       '<gpx version="1.1" creator="r1_ten_holes.py" xmlns="http://www.topografix.com/GPX/1/1">',
       f'<wpt lat="{CAMP_LONLAT[1]}" lon="{CAMP_LONLAT[0]}"><name>CAMP</name><desc>mining camp (client pin)</desc></wpt>']
for h in holes.itertuples():
    gpx.append(f'<wpt lat="{h.collar_lat}" lon="{h.collar_lon}"><ele>{h.collar_elev_m}</ele><name>{h.hole_id}-collar</name>'
               f'<desc>phase {h.phase}, pad {h.pad}, az {h.azimuth}, dip {h.dip}, {h.planned_depth_m} m</desc></wpt>')
    gpx.append(f'<wpt lat="{h.target_lat}" lon="{h.target_lon}"><name>{h.hole_id}-target</name></wpt>')
gpx.append("</gpx>")
open(f"{OUT}/r1_ten_holes.gpx", "w").write("\n".join(gpx))

kml = ['<?xml version="1.0" encoding="UTF-8"?>', '<kml xmlns="http://www.opengis.net/kml/2.2"><Document>',
       '<name>R1 ten provisional holes (unvalidated, UTM 47N assumed)</name>',
       f'<Placemark><name>CAMP</name><Point><coordinates>{CAMP_LONLAT[0]},{CAMP_LONLAT[1]}</coordinates></Point></Placemark>']
for h in holes.itertuples():
    kml.append(f'<Placemark><name>{h.hole_id}</name><description>phase {h.phase}, pad {h.pad}, azimuth {h.azimuth}, '
               f'dip {h.dip}, planned {h.planned_depth_m} m, desk score {h.desk_score}</description>'
               f'<Point><coordinates>{h.collar_lon},{h.collar_lat}</coordinates></Point></Placemark>')
    kml.append(f'<Placemark><name>{h.hole_id} trace</name><LineString><coordinates>{h.collar_lon},{h.collar_lat} '
               f'{h.target_lon},{h.target_lat}</coordinates></LineString></Placemark>')
kml.append("</Document></kml>")
open(f"{OUT}/r1_ten_holes.kml", "w").write("\n".join(kml))

# ------------------------------------------------------------------ map
cx, cy, half = cells.e.mean(), cells.n.mean(), 260
r0, c0 = dem_index(cx - half, cy + half)
r1, c1 = dem_index(cx + half, cy - half)
sub = dem[r0:r1 + 1, c0:c1 + 1]
xs = dtr.c + (np.arange(c0, c1 + 1) + 0.5) * dtr.a
ys = dtr.f + (np.arange(r0, r1 + 1) + 0.5) * dtr.e
gy, gx = np.gradient(sub)
shade = np.clip(0.5 + (gx - gy) / 30, 0, 1)
fig, ax = plt.subplots(figsize=(11, 10))
ax.imshow(shade, extent=[xs[0] - 15, xs[-1] + 15, ys[-1] - 15, ys[0] + 15], cmap="gray", alpha=0.6)
cs = ax.contour(xs, ys, sub, levels=np.arange(300, 470, 10), colors="#92400e", linewidths=0.6, alpha=0.7)
ax.clabel(cs, fontsize=7, fmt="%d")
sc = ax.scatter(cells.e, cells.n, c=cells.score_s, cmap="RdYlBu_r", s=150, marker="s", alpha=0.75, edgecolor="none")
plt.colorbar(sc, ax=ax, fraction=0.04, label="desk score (30 m smoothed)")
for h in holes.itertuples():
    col = "#dc2626" if h.phase == 1 else "#2563eb"
    ax.annotate("", xy=(h.target_e, h.target_n), xytext=(h.collar_e, h.collar_n),
                arrowprops=dict(arrowstyle="-|>", color=col, lw=2))
    ax.scatter(h.collar_e, h.collar_n, s=55, color=col, edgecolor="white", zorder=9)
    ax.text(h.collar_e + 6, h.collar_n - 14, f"{h.hole_id}\n{h.azimuth}°/{h.dip}° {h.planned_depth_m}m", fontsize=7.5,
            color="white", weight="bold", zorder=10, path_effects=[pe.withStroke(linewidth=2.5, foreground=col)])
ax.scatter(camp_e, camp_n, marker="^", s=220, color="#facc15", edgecolor="black", zorder=11)
ax.text(camp_e + 10, camp_n + 8, "CAMP", fontsize=10, weight="bold", zorder=11,
        path_effects=[pe.withStroke(linewidth=3, foreground="white")])
ax.plot([], [], color="#dc2626", lw=2, label="Phase 1: DT-1..DT-4 (desk design)")
ax.plot([], [], color="#2563eb", lw=2, label="Phase 2: only if Phase 1 core shows veining/alteration/Au")
ax.legend(loc="lower right", fontsize=8)
ax.set_xlim(cx - half, cx + half)
ax.set_ylim(cy - half, cy + half)
ax.set_aspect("equal")
ax.set_title(f"R1 - ten provisional holes (arrow = collar to target at {TARGET_DEPTH} m depth)\n"
             f"Assumed strike {STRIKE}° from DEM drainage, not mapped. UTM 47N, unverified. Not a confirmed resource.",
             fontsize=10)
ax.tick_params(labelsize=7)
plt.tight_layout()
fig.savefig(f"{OUT}/r1_ten_holes_map.png", dpi=150)
